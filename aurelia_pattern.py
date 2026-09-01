"""
The Aurelia Top Crochet Pattern's field/formula definition, shared by
add_pattern_aurelia.py (manual run) and auto_seed.py (auto-run on app
startup). One source of truth, so the two never drift apart.

This is the sideways bottom panel + shaped upper panel construction we
worked out earlier (see the standalone Bodice Shaping Calculator, since
folded into this real pattern): gauge from a 10-stitch/10-row swatch,
bottom panel rows from the waist/underbust average, upper panel starting
stitches at double that, then increases spread over the underbust-to-
underarm height until the bust stitch count is reached.
"""
from models import Pattern

AURELIA_SLUG = "aurelia-top"


def build_aurelia_pattern() -> Pattern:
    return Pattern(
        slug=AURELIA_SLUG,
        name="Aurelia Top Crochet Pattern",
        tag="crochet",
        description="A personalized crochet top pattern, sized from your own gauge and measurements.",
        is_free=False,  # locked — needs the access key below plus a matching order (see add_order.py)
        access_key="AURELIA-2026",  # change this to whatever you'll send buyers on Etsy
        swatch_fields=[
            {"id": "swatchWidth10st", "label": "Width for 10 stitches (cm)"},
            {"id": "swatchHeight10row", "label": "Height for 10 rows (cm)"},
        ],
        yarn_fields=[],
        measurement_fields=[
            {"id": "hemToUnderbust", "label": "1 — From hem until underbust (cm)"},
            {"id": "waist", "label": "2 — Around the waist (cm)"},
            {"id": "underbustToUnderarm", "label": "3 — From underbust to underarm (cm)"},
            {"id": "shoulderToUnderarm", "label": "4 — From shoulder to underarm (cm)"},
            {"id": "bust", "label": "5 — Around the bust (cm)"},
            {"id": "underbust", "label": "6 — Around the underbust (cm)"},
        ],
        # Every result gets its own letter, in the order it's calculated, so
        # the instructions below (and anyone reading the results table) can
        # refer to "A", "B", "C"... instead of a long field name.
        computed_fields=[
            {"id": "A", "label": "A — Stitches per 10cm (from swatch)",
             "formula": "100/swatchWidth10st", "round": "none"},
            {"id": "B", "label": "B — Rows per 10cm (from swatch)",
             "formula": "100/swatchHeight10row", "round": "none"},
            {"id": "C", "label": "C — Bottom panel stitch count (from hem to underbust)",
             "formula": "(A/10)*hemToUnderbust", "round": {"type": "mround", "multiple": 1}},
            {"id": "D", "label": "D — Bottom panel rows",
             "formula": "(B/10)*((waist+underbust)/2)", "round": {"type": "mround", "multiple": 1}},
            {"id": "E", "label": "E — Upper panel starting stitches",
             "formula": "D*2", "round": "none"},
            {"id": "F", "label": "F — Target stitches for the bust",
             "formula": "(A/10)*bust", "round": {"type": "mround", "multiple": 1}},
            {"id": "G", "label": "G — Total stitches to increase",
             "formula": "F-E", "round": "none"},
            {"id": "H", "label": "H — Rows to reach underarm",
             "formula": "(B/10)*underbustToUnderarm", "round": {"type": "mround", "multiple": 1}},
        ],
        yarn_estimate=None,
        instructions_template=(
            "Bottom panel: cast on {C} sts and work sideways for {D} rows to "
            "reach your waist/underbust average.\n"
            "Upper panel: cast on / pick up {E} sts.\n"
            "Increase a total of {G} sts, spread evenly, over {H} rows, "
            "until you reach the underarm and have {F} sts for the bust."
        ),
    )
