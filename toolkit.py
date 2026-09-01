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


# ---------------------------------------------------------------- V-NECK BODICE (RIB WAIST + STOCKINETTE BODY)
#
# New construction (2026-08): rib waistband cast on snug to the underbust,
# worked up to the underbust in 2x2 rib, then a stockinette body that may
# need increases to reach the bust, split into front/back panels, and a
# center V-neck + shoulder decrease on the front panel. Sleeves aren't
# designed yet — kol_boyu (M7) is collected but unused for now.
#
# Measurements are named M1..M9 throughout (matching the order they're
# collected in the UI), and the four values the designer explicitly names
# in her own notes keep those letters: A (cast on), B (rib rows), C
# (rows knit plain between increase rows), E (rows over which the shoulder
# decreases happen). Everything else gets a plain descriptive label instead
# of a letter, since only those four were named.

def mround(value: float, multiple: int) -> int:
    """Round to the nearest multiple, e.g. mround(37, 4) -> 36."""
    if multiple <= 0:
        return round(value)
    return int(round(value / multiple) * multiple)


def rib_gauge_at_stretch(stitch_count: float, relaxed_width_cm: float, stretched_width_cm: float,
                          stretch_pct: float = 0.40) -> float:
    """
    Ribbing is worn partway between fully relaxed and fully stretched.
    Interpolates the swatch width `stretch_pct` of the way from relaxed to
    stretched (0.40 = 40% stretch), then converts to stitches/cm. This is
    the gauge used for the cast-on (A) — NOT for row gauge, which uses the
    relaxed swatch instead (see rib_row_gauge below).
    """
    if relaxed_width_cm <= 0:
        return 0.0
    width_at_stretch = relaxed_width_cm + stretch_pct * (stretched_width_cm - relaxed_width_cm)
    if width_at_stretch <= 0:
        return 0.0
    return stitch_count / width_at_stretch


def rib_row_gauge(row_count: float, relaxed_height_cm: float) -> float:
    return (row_count / relaxed_height_cm) if relaxed_height_cm > 0 else 0.0


def stockinette_gauge(stitch_count: float, row_count: float, relaxed_width_cm: float, relaxed_height_cm: float):
    """Returns (stitches_per_cm, rows_per_cm) from the relaxed stockinette swatch."""
    sts_per_cm = (stitch_count / relaxed_width_cm) if relaxed_width_cm > 0 else 0.0
    rows_per_cm = (row_count / relaxed_height_cm) if relaxed_height_cm > 0 else 0.0
    return sts_per_cm, rows_per_cm


def calculate_cast_on_and_rib_rows(
    underbust_cm: float,          # M2
    hem_to_underbust_cm: float,   # M5
    rib_stitch_count: float,
    rib_row_count: float,
    rib_relaxed_width_cm: float,
    rib_relaxed_height_cm: float,
    rib_stretched_width_cm: float,
    stretch_pct: float = 0.40,
):
    """
    A: cast-on stitch count for the 2x2 rib waistband, snug to the underbust
       at `stretch_pct` stretch. Rounded to a multiple of 4 — needed to keep
       the 2x2 rib pattern working, and it also guarantees the later bust
       stitch count (also rounded to a multiple of 4) splits into an even
       front panel.
    B: rows of 2x2 rib to knit from hem to underbust, from the *relaxed* row
       gauge (rows don't stretch lengthwise the way stitches stretch
       around the body, so the relaxed swatch is used here, not the 40% one).
    """
    sts_per_cm_at_stretch = rib_gauge_at_stretch(
        rib_stitch_count, rib_relaxed_width_cm, rib_stretched_width_cm, stretch_pct
    )
    A_cast_on = mround(underbust_cm * sts_per_cm_at_stretch, 4)

    rows_per_cm = rib_row_gauge(rib_row_count, rib_relaxed_height_cm)
    B_rib_rows = round(hem_to_underbust_cm * rows_per_cm)

    return {
        "rib_stitches_per_cm_at_stretch": sts_per_cm_at_stretch,
        "rib_rows_per_cm_relaxed": rows_per_cm,
        "A_cast_on": A_cast_on,
        "B_rib_rows": B_rib_rows,
    }


def calculate_bust_increase(
    A_cast_on: int,
    bust_cm: float,                      # M3
    underbust_to_bustpoint_cm: float,    # M8
    st_stitch_count: float,
    st_row_count: float,
    st_relaxed_width_cm: float,
    st_relaxed_height_cm: float,
    increase_frequency_c: int | None = None,
):
    """
    Checks whether A, knit up in stockinette, is already wide enough for the
    bust. If it falls short, works out the total stitches to increase (2 per
    increase row — 1 each side) and, given a chosen frequency C (rows knit
    plain between increase rows), how the resulting length compares to the
    underbust-to-bustpoint target length.

    increase_frequency_c: pass None to get a *suggested* C (the target
    length divided by the number of increase rows needed, so it's only ever
    exact if that division is whole) — pass a specific C back in (e.g. from
    a UI control) to check how that choice lands against the target length.
    """
    st_sts_per_cm, st_rows_per_cm = stockinette_gauge(
        st_stitch_count, st_row_count, st_relaxed_width_cm, st_relaxed_height_cm
    )

    A_in_stockinette_cm = (A_cast_on / st_sts_per_cm) if st_sts_per_cm > 0 else 0.0
    needs_increase = A_in_stockinette_cm < bust_cm

    if not needs_increase:
        return {
            "stockinette_stitches_per_cm": st_sts_per_cm,
            "stockinette_rows_per_cm": st_rows_per_cm,
            "A_in_stockinette_cm": A_in_stockinette_cm,
            "needs_increase": False,
            "target_bust_stitches": A_cast_on,
            "total_increase_stitches": 0,
            "increase_rows_count": 0,
            "suggested_c": None,
            "increase_frequency_c": None,
            "achieved_rows": 0,
            "achieved_cm": 0.0,
            "target_rows": 0,
        }

    # Multiple of 4 so the front-panel split later (target/2) comes out even.
    target_bust_stitches = mround(bust_cm * st_sts_per_cm, 4)
    total_increase = max(0, target_bust_stitches - A_cast_on)
    increase_rows_count = total_increase // 2  # 2 sts per increase row (1 each side)

    target_rows = round(underbust_to_bustpoint_cm * st_rows_per_cm)

    if increase_rows_count > 0:
        suggested_c = max(0, round(target_rows / increase_rows_count) - 1)
    else:
        suggested_c = 0

    c = increase_frequency_c if increase_frequency_c is not None else suggested_c
    achieved_rows = increase_rows_count * (c + 1)
    achieved_cm = (achieved_rows / st_rows_per_cm) if st_rows_per_cm > 0 else 0.0

    return {
        "stockinette_stitches_per_cm": st_sts_per_cm,
        "stockinette_rows_per_cm": st_rows_per_cm,
        "A_in_stockinette_cm": A_in_stockinette_cm,
        "needs_increase": True,
        "target_bust_stitches": target_bust_stitches,
        "total_increase_stitches": total_increase,
        "increase_rows_count": increase_rows_count,
        "suggested_c": suggested_c,
        "increase_frequency_c": c,
        "achieved_rows": achieved_rows,
        "achieved_cm": achieved_cm,
        "target_rows": target_rows,
    }


def calculate_shoulder_decrease(
    front_panel_stitches: int,             # FP, at bust level
    shoulder_to_underbust_cm: float,       # M6
    underbust_to_bustpoint_cm: float,      # M8
    final_shoulder_width_cm: float,        # M9
    st_stitches_per_cm: float,
    st_rows_per_cm: float,
):
    """
    front_panel_stitches (FP) must be even (guaranteed if the bust stitch
    count feeding it is a multiple of 4 — see calculate_bust_increase).

    Center 2 stitches are bound off at the V; each side then starts with
    (FP-2)/2 stitches and decreases 1 stitch every 2 rows, down to the
    stitch count matching M9 (the strap width), over the length from the
    bust point to the shoulder (M6 - M8).
    """
    available_cm = shoulder_to_underbust_cm - underbust_to_bustpoint_cm
    available_rows = round(available_cm * st_rows_per_cm)

    side_start_stitches = (front_panel_stitches - 2) / 2
    final_stitches_per_side = round(final_shoulder_width_cm * st_stitches_per_cm)
    stitches_to_decrease = max(0, side_start_stitches - final_stitches_per_side)

    E_decrease_rows = int(stitches_to_decrease * 2)  # 1 decrease every 2 rows
    fits = E_decrease_rows <= available_rows

    return {
        "available_cm": available_cm,
        "available_rows": available_rows,
        "side_start_stitches": side_start_stitches,
        "final_stitches_per_side": final_stitches_per_side,
        "stitches_to_decrease_per_side": stitches_to_decrease,
        "E_decrease_rows": E_decrease_rows,
        "fits": fits,
    }
