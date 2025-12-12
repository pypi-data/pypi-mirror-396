from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, JSON, String, Text

from app.db.base import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True)
    scope = Column(String, index=True)
    entity_id = Column(String, index=True, nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    importance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, nullable=True)
    ttl = Column(DateTime, nullable=True)
    embedding = Column(Text, nullable=True)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(String, primary_key=True, index=True)
    if_json = Column(JSON, nullable=False)
    then_json = Column(JSON, nullable=False)
    guardrails_json = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)
    tool_name = Column(String, index=True, nullable=True)
    scope = Column(String, index=True, nullable=True)
    entity_id = Column(String, index=True, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
