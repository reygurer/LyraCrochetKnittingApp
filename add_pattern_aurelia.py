"""
Adds/replaces the "Aurelia Top Crochet Pattern" (definition in
aurelia_pattern.py) so you can test it in the Patterns tab.

Run: python3 add_pattern_aurelia.py
"""
from models import SessionLocal, Pattern, init_db
from aurelia_pattern import build_aurelia_pattern, AURELIA_SLUG

init_db()
session = SessionLocal()

if session.query(Pattern).filter_by(slug=AURELIA_SLUG).first():
    session.query(Pattern).filter_by(slug=AURELIA_SLUG).delete()
    session.commit()
    print("Existing Aurelia pattern removed, replacing it.")

session.add(build_aurelia_pattern())
session.commit()
print("Aurelia Top Crochet Pattern added.")

session.close()
