import streamlit as st
from toolkit import calculate_bodice_shaping, calculate_gauge
from theme import apply_theme

apply_theme()
st.title("Bodice Shaping Calculator")
st.write(
    "For a sideways-knit bottom panel plus a shaped upper panel: figure out "
    "how many rows to knit at the bottom, how many stitches to start the "
    "upper panel with, and how to space the bust increases."
)

st.subheader("Your gauge swatch")
st.caption(
    "Work 10 stitches and 10 rows, then measure the swatch. The beginning "
    "chain sits along the bottom, so the width (horizontal) is your stitch "
    "direction and the height (vertical) is your row direction."
)
c1, c2 = st.columns(2)
with c1:
    swatch_width_cm = st.number_input("Width for 10 stitches (cm)", min_value=0.1, value=5.0)
with c2:
    swatch_height_cm = st.number_input("Height for 10 rows (cm)", min_value=0.1, value=10.5)

stitch_per_10cm, row_per_10cm = calculate_gauge(10, 10, swatch_width_cm, swatch_height_cm)
st.caption(f"That's {stitch_per_10cm:.1f} stitches and {row_per_10cm:.1f} rows per 10cm.")

st.divider()
st.subheader("Measurements you will need")
c3, c4 = st.columns(2)
with c3:
    hem_to_underbust_cm = st.number_input("1: From hem until underbust (cm)", min_value=0.0, value=40.0)
    waist_cm = st.number_input("2: Around the waist (cm)", min_value=0.0, value=65.0)
    underbust_to_underarm_cm = st.number_input("3: From underbust to underarm (cm)", min_value=0.0, value=8.0)
with c4:
    shoulder_to_underarm_cm = st.number_input("4: From shoulder to underarm (cm)", min_value=0.0, value=20.0)
    bust_cm = st.number_input("5: Around the bust (cm)", min_value=0.0, value=90.0)
    underbust_cm = st.number_input("6: Around the underbust (cm)", min_value=0.0, value=78.0)

st.caption(
    "Note: bottom panel stitches are calculated from measurement 1 (hem to "
    "underbust) via your stitch gauge. Measurement 4 (shoulder to underarm) "
    "isn't used in this calculation yet."
)

if st.button("Calculate", type="primary"):
    bottom_panel_stitches = round((stitch_per_10cm / 10) * hem_to_underbust_cm)
    result = calculate_bodice_shaping(
        bust_cm, waist_cm, underbust_cm, underbust_to_underarm_cm,
        bottom_panel_stitches, stitch_per_10cm, row_per_10cm,
    )

    st.divider()
    st.subheader("Results")

    with st.container(border=True):
        r1, r2 = st.columns(2)
        with r1:
            st.metric("(a) Bottom panel rows", result["bottom_panel_rows"])
            st.caption("Knit the sideways bottom panel for this many rows.")
        with r2:
            st.metric("(b) Upper panel starting stitches", result["upper_panel_start_stitches"])
            st.caption("Cast on / pick up this many stitches to start the upper panel.")

        r3, r4 = st.columns(2)
        with r3:
            st.metric("(d) Increase rows", result["increase_rows"])
            st.caption("Spread the increases over this many rows.")
        with r4:
            st.metric("(c) Increase per row (total)", result["per_row_increase"])
            st.caption(f"That's {result['per_side_increase']} stitches on each side, every increase row.")

    st.caption(
        f"Target stitch count for a {bust_cm:.0f}cm bust: {result['target_stitches']}. "
        f"Total stitches to increase from {result['upper_panel_start_stitches']}: {result['total_increase']}."
    )

    if result["total_increase"] == 0:
        st.info(
            "The upper panel's starting stitch count already meets or exceeds "
            "your bust target, so no increases are needed."
        )
