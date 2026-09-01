"""
The Delora Top Knit Pattern's field/formula definition, shared by
add_pattern_delora.py (manual run) and auto_seed.py (auto-run on app
startup). One source of truth, so the two never drift apart.

Construction: a 2x2 rib waistband cast on snug to the underbust (worked at
40% stretch, since that's roughly how rib actually sits once worn), knit up
to the underbust, then a stockinette body that increases to the bust if the
rib cast-on isn't already wide enough. From the bust, the body splits into a
front and back panel; the front panel gets a center V-neck (2 sts bound off
in the middle) with a shoulder decrease on each side.

Every computed field gets a letter (A-Y minus R — see below — in the order
they're calculated) rather than a mix of lettered and plain-described
rows — matches the written pattern text, where every quantity is a
bracketed letter. The ones that actually get quoted in the written
pattern are:
    A - cast-on stitches for the rib waistband
    B - rows of rib from hem to underbust
    C - rows knit plain between increase rows. NOT a user choice — it's
        calculated from the target row count (Q, from M8) and the number
        of increase rows (D). This is the same formula that used to sit
        under a separate letter, R ("suggested C, for reference") — now
        that C *is* that calculation, R is retired and no longer appears
        anywhere. Like D, C lands on 0 when the cast-on is already wide
        enough for the bust (no increases needed).
    D - total number of increase rows (her R1 instructions increase at
        both markers each increase round — see the note further down
        about whether that's 2 or 4 sts per round; D currently assumes 2)
    E - rows the shoulder decrease is worked over
    F - total stitches increased over the upper body
    G - total rows worked over the increase section
    P - stitch count at the bust once the increases are done (the full
        round, before it splits into front and back panels)
    T - front panel stitch count once the panels are separated
    U - front panel stitches per side, after the center 2-st bind-off
The rest (H, I, J, K, L, M, N, O, Q, S, V, W, X, Y) are the gauge and
intermediate steps behind those — not quoted directly in the pattern text,
but lettered the same way so every row in Results reads the same.

computed_fields below stays in DEPENDENCY order, not alphabetical order —
formula_engine.compute_all() (the live app) evaluates this list top to
bottom, feeding each result into a scope dict that later formulas read
from, so every formula can only reference fields already earlier in this
same list. C now depends on both Q and D, so it has to stay positioned
after them — the same spot R used to occupy. The blank-template Excel
(export_delora_excel.py) displays these same letters sorted A→Y instead;
that's safe there because an Excel formula can reference any cell
regardless of which row it's written on, but it would NOT be safe to
reorder this Python list the same way — reordering it would break
compute_all() and the shared excel_export.py exporter, both of which walk
this list sequentially.

Sleeve shaping isn't designed yet — sleeveLength (M7) is collected so the
field is in place, but no formula uses it yet.
"""
from models import Pattern

DELORA_SLUG = "delora-top"


def build_delora_pattern() -> Pattern:
    return Pattern(
        slug=DELORA_SLUG,
        name="Delora Top",
        tag="knit",
        description=(
            "A personalized knit top pattern — 2x2 rib waistband, stockinette "
            "body with bust shaping, and a center V-neck. Sized from your own "
            "gauge and measurements."
        ),
        is_free=True,  # flip to False and set access_key below once it's ready to sell
        access_key=None,
        swatch_fields=[
            {"id": "ribStitchCount", "label": "2x2 Rib swatch — stitch count"},
            {"id": "ribRowCount", "label": "2x2 Rib swatch — row count"},
            {"id": "ribRelaxedWidth", "label": "2x2 Rib swatch — relaxed width (cm)"},
            {"id": "ribRelaxedHeight", "label": "2x2 Rib swatch — relaxed height (cm)"},
            {"id": "ribStretchedWidth", "label": "2x2 Rib swatch — stretched width (cm)"},
            {"id": "ribStretchedHeight", "label": "2x2 Rib swatch — stretched height (cm)"},
            {"id": "stStitchCount", "label": "Stockinette swatch — stitch count"},
            {"id": "stRowCount", "label": "Stockinette swatch — row count"},
            {"id": "stRelaxedWidth", "label": "Stockinette swatch — relaxed width (cm)"},
            {"id": "stRelaxedHeight", "label": "Stockinette swatch — relaxed height (cm)"},
            {"id": "stStretchedWidth", "label": "Stockinette swatch — stretched width (cm)"},
            {"id": "stStretchedHeight", "label": "Stockinette swatch — stretched height (cm)"},
        ],
        yarn_fields=[],
        measurement_fields=[
            {"id": "waist", "label": "M1 — Waist (cm)"},
            {"id": "underbust", "label": "M2 — Underbust (cm)"},
            {"id": "bust", "label": "M3 — Bust (cm)"},
            {"id": "biceps", "label": "M4 — Biceps (cm)"},
            {"id": "hemToUnderbust", "label": "M5 — Hem to underbust (cm)"},
            {"id": "shoulderToUnderbust", "label": "M6 — Shoulder to underbust (cm)"},
            {"id": "sleeveLength", "label": "M7 — Sleeve length (cm) — not used yet"},
            {"id": "underbustToBustpoint", "label": "M8 — Underbust to bust point (cm)"},
            {"id": "finalShoulderWidth", "label": "M9 — Front panel width at the shoulder, for the V-neck (cm)"},
        ],
        # Every result gets its own id, in the order it's calculated, so the
        # instructions below (and the results table) can refer to them by
        # name — A, B, C (input), D, E, F are the designer's own letters;
        # the rest are plain descriptive ids.
        #
        # No if/else here: formula_engine.eval_expr() would happily run
        # Python's ternary syntax, but excel_export.py only substitutes cell
        # references — it doesn't translate Python syntax to Excel syntax —
        # so a formula has to be plain arithmetic to work in both places.
        # Conditionals are written as (condition)*value_if_true +
        # (opposite_condition)*value_if_false instead, since a comparison
        # evaluates to 1/0 in both Python and Excel. Where that's divided by
        # something that can legitimately be zero, the denominator is
        # guarded with "+ (denominator<=0)" so it never divides by zero in
        # either engine — only "<", ">", "<=", ">=" are safe to use this way
        # (Excel's "=" for equality isn't valid Python, and Python's "=="
        # isn't valid Excel).
        computed_fields=[
            {"id": "H", "label": "H — Rib width at 40% stretch (cm)",
             "formula": "ribRelaxedWidth + 0.4*(ribStretchedWidth - ribRelaxedWidth)", "round": "none"},
            {"id": "I", "label": "I — Rib stitches per cm at 40% stretch",
             "formula": "ribStitchCount/H", "round": "none"},
            {"id": "J", "label": "J — Rib rows per cm (relaxed)",
             "formula": "ribRowCount/ribRelaxedHeight", "round": "none"},
            {"id": "A", "label": "A — Cast-on stitches (2x2 rib waistband, snug to underbust)",
             "formula": "underbust*I", "round": {"type": "mround", "multiple": 4}},
            {"id": "B", "label": "B — Rows of 2x2 rib (hem to underbust)",
             "formula": "hemToUnderbust*J", "round": {"type": "mround", "multiple": 1}},
            {"id": "K", "label": "K — Stockinette stitches per cm (relaxed)",
             "formula": "stStitchCount/stRelaxedWidth", "round": "none"},
            {"id": "L", "label": "L — Stockinette rows per cm (relaxed)",
             "formula": "stRowCount/stRelaxedHeight", "round": "none"},
            {"id": "M", "label": "M — A worked in stockinette (cm) — compare to bust (M3)",
             "formula": "A/K", "round": {"type": "round", "digits": 1}},
            {"id": "N", "label": "N — Bust stitch count, raw",
             "formula": "bust*K", "round": "none"},
            {"id": "O", "label": "O — Bust stitch count, rounded to a multiple of 4",
             "formula": "N", "round": {"type": "mround", "multiple": 4}},
            {"id": "P", "label": "P — Stitch count at the bust after the upper-body increases",
             "formula": "(M<bust)*O + (M>=bust)*A", "round": "none"},
            {"id": "F", "label": "F — Total stitches increased",
             "formula": "(P>A)*(P-A)", "round": "none"},
            {"id": "D", "label": "D — Total number of increase rows (2 sts each, 1 per side)",
             "formula": "F/2", "round": "none"},
            {"id": "Q", "label": "Q — Target row count for the increase section (from M8)",
             "formula": "underbustToBustpoint*L", "round": {"type": "mround", "multiple": 1}},
            {"id": "C", "label": "C — Rows knit plain between increase rows (calculated from your target row count)",
             "formula": "((Q/(D+(D<=0)))-1)*(D>0)",
             "round": {"type": "mround", "multiple": 1}},
            {"id": "G", "label": "G — Total rows worked in the increase section (D increase rows, C plain rows between each)",
             "formula": "D*(C+1)", "round": "none"},
            {"id": "S", "label": "S — Length worked in the increase section (cm) — compare to M8",
             "formula": "G/L", "round": {"type": "round", "digits": 1}},
            {"id": "T", "label": "T — Front panel stitch count at the bust, once panels are separated",
             "formula": "P/2", "round": "none"},
            {"id": "U", "label": "U — Front panel stitches per side, after the center 2-st bind-off",
             "formula": "(T-2)/2", "round": "none"},
            {"id": "V", "label": "V — Target stitches per side at the shoulder (from M9)",
             "formula": "finalShoulderWidth*K", "round": {"type": "mround", "multiple": 1}},
            {"id": "W", "label": "W — Stitches to decrease per side",
             "formula": "(U>V)*(U-V)", "round": "none"},
            {"id": "E", "label": "E — Decrease worked over this many rows (1 st every 2 rows)",
             "formula": "W*2", "round": "none"},
            {"id": "X", "label": "X — Rows available for shoulder shaping (M6 minus M8)",
             "formula": "(shoulderToUnderbust-underbustToBustpoint)*L", "round": {"type": "mround", "multiple": 1}},
            {"id": "Y", "label": "Y — Shaping margin (X minus E) — if negative, choose a larger M9",
             "formula": "X-E", "round": "none"},
        ],
        yarn_estimate=None,
        instructions_template=(
            "Rib waistband: cast on {A} sts (2x2 rib) and work {B} rows to reach the underbust.\n"
            "Bust increases: increase a total of {F} sts over {D} increase rows "
            "(2 sts each, 1 per side), working {C} rows plain between each — this reaches roughly "
            "{S}cm against a target of {Q} rows from M8, ending with {P} sts at the bust.\n"
            "Split into a front and back panel of {T} sts each at the bust.\n"
            "V-neck: bind off the center 2 sts, {U} sts remain on each side. Decrease 1 st "
            "every 2 rows, {W} times per side, over {E} rows, down to {V} sts "
            "at the shoulder. {X} rows are available for this shaping — if {Y} "
            "is negative, choose a larger M9 and recalculate."
        ),
    )
