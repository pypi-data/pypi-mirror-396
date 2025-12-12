"""
Primary public package surface for mengram.

Exports:
- MemoryClient: programmatic API for memories/rules/events
- init_memory_os_schema: creates required tables (idempotent)
"""

from app.core import MemoryClient
from app.db.init_db import init_memory_os_schema

__all__ = ["MemoryClient", "init_memory_os_schema"]
