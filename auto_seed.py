"""
Runs on every app startup (see streamlit_app.py) so patterns show up even on
hosts with no shell access (Streamlit Community Cloud, etc.) — on platforms
where the database resets on every deploy, this recreates them automatically
instead of needing someone to SSH in and run a script by hand.

Idempotent: checks each pattern's slug and skips it if already there, so
running this on every boot never duplicates or overwrites existing patterns.
"""
from models import SessionLocal, Pattern, init_db
from aurelia_pattern import build_aurelia_pattern
from delora_pattern import build_delora_pattern


def _add_if_missing(session, pattern: Pattern):
    if session.query(Pattern).filter_by(slug=pattern.slug).first():
        return False
    session.add(pattern)
    return True


def ensure_default_patterns():
    init_db()
    session = SessionLocal()
    added = 0

    if _add_if_missing(session, build_aurelia_pattern()):
        added += 1

    if _add_if_missing(session, build_delora_pattern()):
        added += 1

    if added:
        session.commit()
    session.close()
