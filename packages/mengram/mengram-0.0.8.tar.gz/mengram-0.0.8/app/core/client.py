from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
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
