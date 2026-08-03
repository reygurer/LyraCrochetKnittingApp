import streamlit as st
from toolkit import (
    PROJECT_BASE_METERAGE,
    YARN_WEIGHT_FACTOR,
    SIZE_FACTOR,
    estimate_yarn,
    check_sufficient,
)
from theme import apply_theme

apply_theme()
st.title("Yarn Calculator")
st.write(
    "A rough, general-purpose estimate, not tied to a specific pattern. "
    "For an exact amount, use the pattern's own calculation (Excel output)."
)

c1, c2, c3 = st.columns(3)
with c1:
    project_type = st.selectbox("Project type", list(PROJECT_BASE_METERAGE.keys()))
with c2:
    size = st.selectbox("Size", list(SIZE_FACTOR.keys()), index=2)
with c3:
    yarn_weight = st.selectbox("Yarn weight", list(YARN_WEIGHT_FACTOR.keys()), index=4)

needed = estimate_yarn(project_type, size, yarn_weight)
st.metric("Estimated amount needed", f"{needed} m")

st.divider()
st.subheader("Do you have enough?")
c4, c5 = st.columns(2)
with c4:
    skeins = st.number_input("Skeins you have", min_value=0, value=3)
with c5:
    meters_per_skein = st.number_input("Meters per skein", min_value=0.0, value=200.0)

sufficient, have = check_sufficient(needed, skeins, meters_per_skein)
if have > 0:
    if sufficient:
        st.success(f"Enough — you have {have:.0f}m, you need {needed}m.")
    else:
        st.warning(f"Might not be enough — you have {have:.0f}m, you need {needed}m.")
