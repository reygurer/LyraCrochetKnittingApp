"""
Database schema.

If DATABASE_URL is not set, falls back to SQLite for local testing.
In production (Render/Railway etc.), just point DATABASE_URL at a
PostgreSQL connection — the code doesn't change.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///local_patterns.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    tag = Column(String, default="")
    description = Column(Text, default="")

    # Access: if is_free, no key is required. Otherwise unlocked with access_key.
    is_free = Column(Boolean, default=False)
    access_key = Column(String, nullable=True)

    # Field definitions — each a list like [{"id": "...", "label": "..."}]
    swatch_fields = Column(JSON, default=list)
    yarn_fields = Column(JSON, default=list)
    measurement_fields = Column(JSON, default=list)

    # Computed sections — [{"id":"A","label":"...","formula":"...","round":...}]
    computed_fields = Column(JSON, default=list)

    # Yarn estimate — {"area_formula": "..."} or None
    yarn_estimate = Column(JSON, nullable=True)

    # Instruction text — contains placeholders like {A}, {B}
    instructions_template = Column(Text, default="")

    # Optional walkthrough video for this pattern only — a YouTube/Vimeo
    # link or a direct video file URL. Only shown once the buyer has
    # actually unlocked the pattern (see views/patterns.py — the form/
    # results steps are only reachable after that), so it's effectively
    # gated behind purchase the same way the instructions/formulas are.
    video_url = Column(String, nullable=True)


class Unlock(Base):
    """
    Persists which patterns an email has unlocked, so access survives across
    sessions/devices instead of living only in st.session_state. A row here
    means: this email successfully entered this pattern's access_key once.
    """

    __tablename__ = "unlocks"
    __table_args__ = (UniqueConstraint("email", "pattern_id", name="uq_unlock_email_pattern"),)

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, index=True)
    pattern_id = Column(Integer, ForeignKey("patterns.id"), nullable=False)


class PurchaseAuthorization(Base):
    """
    Records which email actually bought which pattern on Etsy. You add a row
    here yourself (see add_order.py) when an order comes in. Unlocking now
    requires BOTH the correct access_key AND a matching row here for the
    signed-in email — so a shared/leaked key alone isn't enough to unlock a
    pattern for an email that never actually bought it.
    """

    __tablename__ = "purchase_authorizations"
    __table_args__ = (UniqueConstraint("email", "pattern_id", name="uq_purchase_email_pattern"),)

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, index=True)
    pattern_id = Column(Integer, ForeignKey("patterns.id"), nullable=False)


class Project(Base):
    """For the row counter — tracks multiple projects in parallel."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    total_rows = Column(Integer, default=0)
    current_row = Column(Integer, default=0)
    notes = Column(Text, default="")


def init_db():
    Base.metadata.create_all(engine)
    _ensure_column("patterns", "video_url", "VARCHAR")


def _ensure_column(table, column, coltype):
    """
    Base.metadata.create_all only creates tables that don't exist yet — it
    never adds a new column to a table that's already there. Since this
    project has no migration tool (Alembic etc.), this does the one thing
    we actually need: add a column if it's missing, on both SQLite (local)
    and Postgres (production), so existing databases pick up new Pattern
    fields (like video_url) without anyone having to drop/recreate them.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    existing = [c["name"] for c in inspector.get_columns(table)]
    if column not in existing:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}"))
