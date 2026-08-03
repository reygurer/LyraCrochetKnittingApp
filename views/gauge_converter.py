import streamlit as st
from toolkit import calculate_gauge_relaxed_stretched, needle_recommendation, mm_to_us
from theme import apply_theme

apply_theme()
st.title("Gauge Converter")
st.write(
    "Calculate your real gauge from a swatch, accounting for both its "
    "relaxed and stretched state, and get a needle size suggestion."
)

st.subheader("Your swatch")
st.caption("Stitch and row count stay the same — measure the same swatch twice.")
c1, c2 = st.columns(2)
with c1:
    stitch_count = st.number_input("Stitch count", min_value=0.0, value=20.0)
with c2:
    row_count = st.number_input("Row count", min_value=0.0, value=28.0)

st.markdown("**Relaxed (resting flat, unstretched)**")
c3, c4 = st.columns(2)
with c3:
    relaxed_width_cm = st.number_input("Width (cm)", min_value=0.01, value=10.0, key="relaxed_w")
with c4:
    relaxed_height_cm = st.number_input("Height (cm)", min_value=0.01, value=10.0, key="relaxed_h")

st.markdown("**Stretched (gently pulled to wearing tension)**")
c5, c6 = st.columns(2)
with c5:
    stretched_width_cm = st.number_input("Width (cm)", min_value=0.01, value=11.0, key="stretched_w")
with c6:
    stretched_height_cm = st.number_input("Height (cm)", min_value=0.01, value=10.5, key="stretched_h")

gauge = calculate_gauge_relaxed_stretched(
    stitch_count, row_count,
    relaxed_width_cm, relaxed_height_cm,
    stretched_width_cm, stretched_height_cm,
)

st.divider()
st.subheader("Results")

r1, r2, r3 = st.columns(3)
with r1:
    st.markdown("Relaxed")
    st.metric("Stitches / 10cm", f"{gauge['relaxed'][0]:.1f}")
    st.metric("Rows / 10cm", f"{gauge['relaxed'][1]:.1f}")
with r2:
    st.markdown("Stretched")
    st.metric("Stitches / 10cm", f"{gauge['stretched'][0]:.1f}")
    st.metric("Rows / 10cm", f"{gauge['stretched'][1]:.1f}")
with r3:
    st.markdown("Average (recommended)")
    st.metric("Stitches / 10cm", f"{gauge['average'][0]:.1f}")
    st.metric("Rows / 10cm", f"{gauge['average'][1]:.1f}")

st.caption(
    "The average is usually the best number to design from — worn fabric "
    "settles somewhere between fully relaxed and fully stretched."
)

st.divider()
st.subheader("Needle suggestion")

reference = st.radio(
    "Use which gauge as your current gauge?",
    ["Average", "Relaxed", "Stretched"],
    horizontal=True,
)
current_gauge = gauge[reference.lower()][0]

c7, c8 = st.columns(2)
with c7:
    target_gauge = st.number_input("Target gauge (stitches per 10cm)", min_value=0.0, value=22.0)
with c8:
    current_mm = st.number_input("Needle you're using (mm)", min_value=1.0, value=4.0, step=0.25)

if st.button("Suggest", type="primary"):
    msg, new_mm = needle_recommendation(current_gauge, target_gauge, current_mm)
    st.info(msg)
    if new_mm != current_mm:
        st.caption(f"Approximate US equivalent: {mm_to_us(new_mm)}")
