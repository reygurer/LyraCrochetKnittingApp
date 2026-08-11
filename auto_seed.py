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


def _add_if_missing(session, pattern: Pattern):
    if session.query(Pattern).filter_by(slug=pattern.slug).first():
        return False
    session.add(pattern)
    return True


def ensure_default_patterns():
    init_db()
    session = SessionLocal()
    added = 0

    if _add_if_missing(session, Pattern(
        slug="demo-basic-top",
        name="Test Pattern — Simple Tank Top",
        tag="sample / test",
        description="A comprehensive example (same measurement set as the Stockholm-style reference) to check the engine works. Not real ratios.",
        is_free=True,
        access_key=None,
        swatch_fields=[
            {"id": "swatchStretchedAcross", "label": "Stretched swatch — width (cm)"},
            {"id": "swatchStretchedDown", "label": "Stretched swatch — length (cm)"},
            {"id": "swatchRelaxedAcross", "label": "Relaxed swatch — width (cm)"},
            {"id": "swatchRelaxedDown", "label": "Relaxed swatch — length (cm)"},
        ],
        yarn_fields=[
            {"id": "skeinMeterage", "label": "Total meterage of 1 skein (m)"},
            {"id": "skeinWeight", "label": "Total weight of 1 skein (g)"},
            {"id": "swatchWeight", "label": "Swatch weight (g) — leave 0 if unknown"},
            {"id": "swatchYarnLength", "label": "Yarn length used in swatch (cm) — only if you didn't weigh it"},
        ],
        measurement_fields=[
            {"id": "underbust", "label": "1 — Around the underbust (cm)"},
            {"id": "bust", "label": "2 — Around the bust (cm)"},
            {"id": "waist", "label": "3 — Around the waist (cm)"},
            {"id": "overBust", "label": "4 — Inline with underarm to underbust, over the bust (cm)"},
            {"id": "shoulderToUnderarm", "label": "5 — Top of shoulder to underarm (cm)"},
            {"id": "underbustToWaist", "label": "6 — Underbust to waist (cm)"},
            {"id": "torsoEnd", "label": "7 — Around the torso where you want the top to end (cm)"},
            {"id": "waistToEnd", "label": "8 — Waist to where you want the top to end (cm)"},
        ],
        computed_fields=[
            {"id": "A", "label": "Neckline circumference — stitch count",
             "formula": "(bust/2) / swatchStretchedAcross * 20", "round": "even"},
            {"id": "B", "label": "Rows to waist shaping",
             "formula": "underbustToWaist / swatchRelaxedDown * 20", "round": "none"},
            {"id": "C", "label": "Waist — stitch count",
             "formula": "(waist/2) / swatchStretchedAcross * 20", "round": "even"},
            {"id": "D", "label": "Waist shaping — rows between each decrease",
             "formula": "B / ((A-C)/2)", "round": {"type": "mround", "multiple": 1}},
        ],
        yarn_estimate={"area_formula": "bust * (underbustToWaist + waistToEnd) * 1.15"},
        instructions_template=(
            "Cast on {A} sts for the neckline. Work {B} rows plain, then "
            "decrease every {D} rows down to {C} sts."
        ),
    )):
        added += 1

    if _add_if_missing(session, build_aurelia_pattern()):
        added += 1

    if added:
        session.commit()
    session.close()
