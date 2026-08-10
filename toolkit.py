"""
General-purpose knit/crochet calculation tools — not tied to a specific
pattern. This carries over the logic from the earlier toolkit's
gauge_converter / yarn_calculator / pattern_scaler modules.
"""

import math

# ---------------------------------------------------------------- GAUGE

NEEDLE_MM_TO_US = [
    (2.0, "0"), (2.25, "1"), (2.75, "2"), (3.0, "2/3"), (3.25, "3"),
    (3.5, "4"), (3.75, "5"), (4.0, "6"), (4.5, "7"), (5.0, "8"),
    (5.5, "9"), (6.0, "10"), (6.5, "10.5"), (8.0, "11"), (9.0, "13"),
    (10.0, "15"), (12.0, "17"), (16.0, "19"), (19.0, "35"),
]


def calculate_gauge(stitch_count: float, row_count: float, width_cm: float, height_cm: float):
    """
    Returns stitches/rows per 10cm from a swatch.

    width_cm is the horizontal measurement (the direction the beginning
    chain/foundation row runs, i.e. the stitch direction). height_cm is the
    vertical measurement (the direction rows stack going up from that chain).
    """
    sts_per_10cm = (stitch_count / width_cm) * 10 if width_cm else 0
    rows_per_10cm = (row_count / height_cm) * 10 if height_cm else 0
    return sts_per_10cm, rows_per_10cm


def calculate_gauge_relaxed_stretched(
    stitch_count: float,
    row_count: float,
    relaxed_width_cm: float,
    relaxed_height_cm: float,
    stretched_width_cm: float,
    stretched_height_cm: float,
):
    """
    Stretchy fabrics (ribbing, lace, bias, anything with drape) measure
    differently at rest vs. gently stretched, and worn fabric usually
    settles somewhere between the two. Same stitch/row count, measured
    twice — once with the swatch relaxed, once gently stretched to typical
    wearing tension.

    Returns a dict with "relaxed", "stretched", and "average" keys, each a
    (sts_per_10cm, rows_per_10cm) tuple. "average" is generally the best
    number to design from.
    """
    relaxed = calculate_gauge(stitch_count, row_count, relaxed_width_cm, relaxed_height_cm)
    stretched = calculate_gauge(stitch_count, row_count, stretched_width_cm, stretched_height_cm)
    average = ((relaxed[0] + stretched[0]) / 2, (relaxed[1] + stretched[1]) / 2)
    return {"relaxed": relaxed, "stretched": stretched, "average": average}


def needle_recommendation(current_gauge: float, target_gauge: float, current_mm: float):
    """
    If the current gauge is tighter than the target (more stitches), suggests
    a bigger needle; if looser, a smaller one.
    """
    if target_gauge <= 0 or current_gauge <= 0:
        return "Enter a valid gauge value.", current_mm

    diff_pct = (current_gauge - target_gauge) / target_gauge

    if abs(diff_pct) < 0.03:
        return "Your gauge is already close to the target, no need to change needles.", current_mm

    step = 0.25 if abs(diff_pct) < 0.08 else 0.5
    if diff_pct > 0:
        new_mm = round(current_mm + step, 2)
        msg = f"Too many stitches — try a bigger needle: around {new_mm}mm."
    else:
        new_mm = round(current_mm - step, 2)
        msg = f"Too few stitches — try a smaller needle: around {new_mm}mm."
    return msg, new_mm


def mm_to_us(mm: float) -> str:
    closest = min(NEEDLE_MM_TO_US, key=lambda x: abs(x[0] - mm))
    return closest[1]


# ---------------------------------------------------------------- YARN

# Rough estimates — worsted weight yarn, based on size M (meters).
# Actual need varies by yarn brand, gauge, and design.
PROJECT_BASE_METERAGE = {
    "Beanie / Hat": 180,
    "Scarf": 350,
    "Mittens": 150,
    "Socks (pair)": 400,
    "Tank Top": 700,
    "Sweater": 1300,
    "Cardigan": 1500,
    "Shawl": 600,
    "Bag": 400,
}

# Multiplier by yarn weight — worsted (1.0) is the baseline
YARN_WEIGHT_FACTOR = {
    "Lace": 3.0,
    "Fingering": 2.2,
    "Sport": 1.6,
    "DK": 1.25,
    "Worsted": 1.0,
    "Aran": 0.85,
    "Bulky": 0.6,
    "Super Bulky": 0.4,
}

SIZE_FACTOR = {"XS": 0.75, "S": 0.85, "M": 1.0, "L": 1.15, "XL": 1.3, "2XL+": 1.45}


def estimate_yarn(project_type: str, size: str, yarn_weight: str):
    base = PROJECT_BASE_METERAGE.get(project_type, 500)
    meters = base * SIZE_FACTOR.get(size, 1.0) * YARN_WEIGHT_FACTOR.get(yarn_weight, 1.0)
    return round(meters)


def check_sufficient(needed_meters: float, skeins_on_hand: int, meters_per_skein: float):
    have = skeins_on_hand * meters_per_skein
    return have >= needed_meters, have


# ---------------------------------------------------------------- SCALE

def scale_count(base_count: float, base_gauge: float, target_gauge: float,
                 multiple_of: int | None = None, extra_ease_cm: float = 0.0):
    """
    base_count: original stitch/row count
    base_gauge / target_gauge: stitches per 10cm (same direction)
    extra_ease_cm: extra ease to add (cm), converted to stitches via target_gauge
    """
    if base_gauge <= 0:
        return base_count
    scaled = base_count * (target_gauge / base_gauge)
    scaled += (extra_ease_cm / 10) * target_gauge
    if multiple_of and multiple_of > 0:
        scaled = round(scaled / multiple_of) * multiple_of
    else:
        scaled = round(scaled)
    return int(scaled)


# ---------------------------------------------------------------- BODICE SHAPING

def calculate_bodice_shaping(
    bust_cm: float,
    waist_cm: float,
    underbust_cm: float,
    underbust_to_armpit_cm: float,
    bottom_panel_stitches: float,
    stitch_per_10cm: float,
    row_per_10cm: float,
):
    """
    Sideways bottom panel + shaped upper (bust) panel, worked as:

    - Bottom panel: cast on `bottom_panel_stitches` (a free choice, sets how
      tall/long the panel is, not derived from gauge) and knit sideways until
      it's wide enough to cover the average of the waist and underbust
      circumference (since the panel tapers between those two measurements).
      That row count is `bottom_panel_rows` (a).
    - Upper panel: picked up / cast on at `2 * bottom_panel_rows` stitches (b)
      to start (roughly converts the same edge length from the row gauge into
      the stitch gauge for the new, normal-orientation panel).
    - From there, increase evenly on both sides every row until both the
      bust stitch count (from `bust_cm`) and the vertical height
      (`underbust_to_armpit_cm`, converted to rows) are reached.
    - The total stitches to increase are spread across those rows. Since an
      increase row adds stitches to both sides symmetrically, the per-row
      total must be even: round up to the next even number if it isn't, then
      split it in half for each side.

    Returns a dict with:
        bottom_panel_rows            -> (a) rows to knit for the bottom panel
        upper_panel_start_stitches   -> (b) cast on for the upper panel (2x)
        target_stitches              -> stitch count matching bust_cm
        total_increase               -> stitches still needed to reach that
        increase_rows                -> (d) rows over which to spread the increases
        per_row_increase             -> (c) total stitches increased each row (both sides)
        per_side_increase            -> per_row_increase split in half, one side
    """
    stitch_per_cm = stitch_per_10cm / 10
    row_per_cm = row_per_10cm / 10

    bottom_panel_rows = round(row_per_cm * (waist_cm + underbust_cm) / 2)
    upper_panel_start_stitches = 2 * bottom_panel_rows

    target_stitches = round(stitch_per_cm * bust_cm)
    total_increase = target_stitches - upper_panel_start_stitches

    increase_rows = round(row_per_cm * underbust_to_armpit_cm)

    if total_increase <= 0:
        # Already at (or past) the target width — nothing left to increase.
        return {
            "bottom_panel_rows": bottom_panel_rows,
            "upper_panel_start_stitches": upper_panel_start_stitches,
            "target_stitches": target_stitches,
            "total_increase": 0,
            "increase_rows": increase_rows,
            "per_row_increase": 0,
            "per_side_increase": 0,
        }

    if increase_rows <= 0:
        # Not enough vertical room per the gauge — do it all in one row.
        increase_rows = 1

    per_row_increase = math.ceil(total_increase / increase_rows)
    if per_row_increase % 2 != 0:
        per_row_increase += 1  # round up to the next even number so it splits cleanly
    per_side_increase = per_row_increase // 2

    return {
        "bottom_panel_rows": bottom_panel_rows,
        "upper_panel_start_stitches": upper_panel_start_stitches,
        "target_stitches": target_stitches,
        "total_increase": total_increase,
        "increase_rows": increase_rows,
        "per_row_increase": per_row_increase,
        "per_side_increase": per_side_increase,
    }
