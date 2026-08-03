"""
General-purpose knit/crochet calculation tools — not tied to a specific
pattern. This carries over the logic from the earlier toolkit's
gauge_converter / yarn_calculator / pattern_scaler modules.
"""

# ---------------------------------------------------------------- GAUGE

NEEDLE_MM_TO_US = [
    (2.0, "0"), (2.25, "1"), (2.75, "2"), (3.0, "2/3"), (3.25, "3"),
    (3.5, "4"), (3.75, "5"), (4.0, "6"), (4.5, "7"), (5.0, "8"),
    (5.5, "9"), (6.0, "10"), (6.5, "10.5"), (8.0, "11"), (9.0, "13"),
    (10.0, "15"), (12.0, "17"), (16.0, "19"), (19.0, "35"),
]


def calculate_gauge(stitch_count: float, row_count: float, width_cm: float, height_cm: float):
    """Returns stitches/rows per 10cm from a swatch."""
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
