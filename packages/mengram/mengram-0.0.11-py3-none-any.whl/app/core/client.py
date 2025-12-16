from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.auto.models import (
    ALLOWED_MEMORY_TYPES,
    ALLOWED_SCOPES,
    Extractor,
    Interaction,
    MemoryCandidate,
)
from app.models.memory import Memory
from app.schemas.memory import (
    EventIn,
    EventResponse,
    ForgetIn,
    MemoryOut,
    PlanCondition,
    PlanIn,
    PlanThen,
    ProspectiveAction,
    ReflectIn,
    RememberIn,
)
from app.services.event_service import handle_event
from app.services.memory_service import (
    forget_memory,
    recall_memories,
    reflect_session,
    remember_memory,
    store_plan,
)
from app.services.embedding import embed_text
from app.utils.text import normalize_text


class MemoryClient:
    """Programmatic interface that mirrors the REST API surface."""

    def __init__(
        self,
        *,
        session_factory: Optional[Callable[[], Session]] = None,
        embed_fn: Optional[Callable[[str], Any]] = None,
        redact_pii: bool = True,
    ):
        self._session_factory = session_factory or SessionLocal
        self._embed_fn = embed_fn or embed_text
        self._redact_pii = redact_pii

    @contextmanager
    def _get_session(self, session: Optional[Session] = None):
        if session is not None:
            yield session
            return
        db = self._session_factory()
        try:
            yield db
        finally:
            db.close()

    def remember(
        self,
        *,
        content: str,
        type: str,
        scope: str,
        entity_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.0,
        ttl_hours: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None,
    ) -> MemoryOut:
        payload = RememberIn(
            content=content,
            type=type,
            scope=scope,
            entity_id=entity_id,
            tags=tags,
            importance=importance,
            ttl_hours=ttl_hours,
            metadata=metadata,
        )
        with self._get_session(session) as db:
            return remember_memory(db, payload, embed_fn=self._embed_fn, redact=self._redact_pii)

    def recall(
        self,
        *,
        query: str,
        k: int = 8,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        as_of: Optional[datetime | str] = None,
        session: Optional[Session] = None,
    ) -> List[MemoryOut]:
        as_of_value: Optional[str]
        if isinstance(as_of, datetime):
            as_of_value = as_of.isoformat()
        else:
            as_of_value = as_of
        with self._get_session(session) as db:
            return recall_memories(
                db,
                query=query,
                k=k,
                scope=scope,
                entity_id=entity_id,
                as_of=as_of_value,
                embed_fn=self._embed_fn,
            )

    def reflect(
        self,
        *,
        session_id: str,
        budget_tokens: int = 1500,
        session: Optional[Session] = None,
    ):
        payload = ReflectIn(session_id=session_id, budget_tokens=budget_tokens)
        with self._get_session(session) as db:
            return reflect_session(db, payload, embed_fn=self._embed_fn)

    def create_rule(
        self,
        *,
        condition: Dict[str, Any],
        actions: Dict[str, Any],
        guardrails: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None,
    ):
        plan_condition = PlanCondition(**condition)
        # Allow callers to pass raw action dicts or already-validated models
        if "actions" in actions and isinstance(actions["actions"], Iterable):
            action_models = [ProspectiveAction(**action) for action in actions["actions"]]  # type: ignore[arg-type]
        else:
            raise ValueError("actions dictionary must include an 'actions' list.")
        plan_then = PlanThen(actions=action_models)
        plan_payload = PlanIn(if_=plan_condition, then=plan_then, guardrails=guardrails)
        with self._get_session(session) as db:
            return store_plan(db, plan_payload)

    def record_event(
        self,
        *,
        event_type: str,
        tool_name: Optional[str] = None,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None,
    ) -> EventResponse:
        event_payload = EventIn(
            event_type=event_type,
            tool_name=tool_name,
            scope=scope,
            entity_id=entity_id,
            payload=payload,
        )
        with self._get_session(session) as db:
            return handle_event(db, event_payload)

    def forget(
        self,
        *,
        id: Optional[str] = None,
        policy: Optional[str] = None,
        reason: Optional[str] = "unspecified",
        session: Optional[Session] = None,
    ):
        payload = ForgetIn(id=id, policy=policy, reason=reason)
        with self._get_session(session) as db:
            return forget_memory(db, payload)

    def auto_ingest(
        self,
        *,
        interactions: List[Interaction],
        extractor: Extractor,
        scope: Optional[str] = None,
        entity_id: Optional[str] = None,
        max_memories: Optional[int] = None,
        min_importance: Optional[float] = None,
        session: Optional[Session] = None,
    ) -> List[MemoryOut]:
        if not interactions:
            return []
        if extractor is None:
            raise ValueError("auto_ingest requires a non-null extractor")

        candidates = extractor(interactions)
        normalized: List[MemoryCandidate] = []
        for candidate in candidates:
            content = (candidate.content or "").strip()
            if not content:
                continue

            ctype = candidate.type if candidate.type in ALLOWED_MEMORY_TYPES else "semantic"
            importance = candidate.importance
            if min_importance is not None and importance is not None and importance < min_importance:
                continue

            scoped = candidate.model_copy()
            scoped.content = content
            scoped.type = ctype

            # Clamp scope to allowed values; default to provided scope or "session".
            effective_scope = scope or "session"
            if scoped.scope in ALLOWED_SCOPES:
                effective_scope = scoped.scope
            scoped.scope = effective_scope

            # Use candidate entity_id when provided, else fallback to outer entity_id.
            scoped.entity_id = scoped.entity_id or entity_id

            normalized.append(scoped)

        # Deduplicate against existing memories per (scope, entity_id) and within this batch
        with self._get_session(session) as db:
            seen_by_key: Dict[tuple, set] = {}

            def get_seen(scope_val: str, entity_val: Optional[str]) -> set:
                key = (scope_val, entity_val)
                if key not in seen_by_key:
                    q = db.query(Memory).filter(Memory.scope == scope_val)
                    if entity_val:
                        q = q.filter(Memory.entity_id == entity_val)
                    existing = q.all()
                    seen_by_key[key] = {normalize_text(mem.content) for mem in existing}
                return seen_by_key[key]

            deduped: List[MemoryCandidate] = []
            for candidate in normalized:
                eff_scope = candidate.scope or "session"
                eff_entity = candidate.entity_id
                seen = get_seen(eff_scope, eff_entity)
                norm_content = normalize_text(candidate.content)
                if norm_content in seen:
                    continue
                seen.add(norm_content)
                deduped.append(candidate)

            # Apply max_memories after dedupe, sorted by importance desc (None -> 0.0)
            deduped.sort(key=lambda c: c.importance if c.importance is not None else 0.0, reverse=True)
            if max_memories is not None:
                deduped = deduped[:max_memories]

            stored: List[MemoryOut] = []
            for candidate in deduped:
                stored.append(
                    self.remember(
                        content=candidate.content,
                        type=candidate.type,
                        scope=candidate.scope or "session",
                        entity_id=candidate.entity_id,
                        tags=candidate.tags,
                        importance=candidate.importance or 0.0,
                        metadata=candidate.metadata,
                        session=db,
                    )
                )
        return stored
