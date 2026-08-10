"""
Adds the real "Aurelia Top Crochet Pattern" so it shows up in the Patterns
tab. Measurement fields match the table we've been using for the bodice
shaping math (hem to underbust, waist, underbust to underarm, shoulder to
underarm, bust, underbust). Computed fields / instructions are left empty
for now, add those once the shaping formulas for this pattern are final.

Run: python3 add_pattern_aurelia.py
"""
from models import SessionLocal, Pattern, init_db

init_db()
session = SessionLocal()

if session.query(Pattern).filter_by(slug="aurelia-top").first():
    session.query(Pattern).filter_by(slug="aurelia-top").delete()
    session.commit()
    print("Existing Aurelia pattern removed, replacing it.")

aurelia = Pattern(
    slug="aurelia-top",
    name="Aurelia Top Crochet Pattern",
    tag="crochet",
    description="A personalized crochet top pattern, sized from your own gauge and measurements.",
    is_free=True,  # flip to False and set access_key once it's ready to sell
    access_key=None,
    swatch_fields=[],
    yarn_fields=[],
    measurement_fields=[
        {"id": "hemToUnderbust", "label": "1 — From hem until underbust (cm)"},
        {"id": "waist", "label": "2 — Around the waist (cm)"},
        {"id": "underbustToUnderarm", "label": "3 — From underbust to underarm (cm)"},
        {"id": "shoulderToUnderarm", "label": "4 — From shoulder to underarm (cm)"},
        {"id": "bust", "label": "5 — Around the bust (cm)"},
        {"id": "underbust", "label": "6 — Around the underbust (cm)"},
    ],
    computed_fields=[],
    yarn_estimate=None,
    instructions_template="",
)
session.add(aurelia)
session.commit()
print("Aurelia Top Crochet Pattern added.")

session.close()
