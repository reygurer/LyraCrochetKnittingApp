import streamlit as st
from toolkit import scale_count
from theme import apply_theme

apply_theme()
st.title("Pattern Scaler")
st.write("Recalculate a stitch or row count for a different gauge or size.")

c1, c2 = st.columns(2)
with c1:
    base_count = st.number_input("Original count (stitches or rows)", min_value=0, value=80)
    base_gauge = st.number_input("Original gauge (per 10cm)", min_value=0.1, value=20.0)
with c2:
    multiple_of = st.number_input("Must be a multiple of (0 to skip)", min_value=0, value=0)
    target_gauge = st.number_input("Your gauge (per 10cm)", min_value=0.1, value=22.0)

extra_ease = st.number_input("Extra ease (cm, optional)", value=0.0)

result = scale_count(
    base_count, base_gauge, target_gauge,
    multiple_of=multiple_of or None, extra_ease_cm=extra_ease,
)
st.metric("Your count", result)
