"""SQLAlchemy declarative base + shared metadata.

Models (added in Phase 1) subclass `Base`. Alembic imports this module's metadata
for autogenerate, so every model module must be imported into `app.db.base` before
migrations are generated (a `models` aggregator import will be added in Phase 1).
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
