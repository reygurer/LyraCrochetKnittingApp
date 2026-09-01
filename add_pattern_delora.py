"""
Adds/replaces the "Delora Top" knit pattern (definition in
delora_pattern.py) so you can test it in the Patterns tab.

Run: python3 add_pattern_delora.py
"""
from models import SessionLocal, Pattern, init_db
from delora_pattern import build_delora_pattern, DELORA_SLUG

init_db()
session = SessionLocal()

if session.query(Pattern).filter_by(slug=DELORA_SLUG).first():
    session.query(Pattern).filter_by(slug=DELORA_SLUG).delete()
    session.commit()
    print("Existing Delora pattern removed, replacing it.")

session.add(build_delora_pattern())
session.commit()
print("Delora Top pattern added.")

session.close()
