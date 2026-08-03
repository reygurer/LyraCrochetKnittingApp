import streamlit as st
from theme import apply_theme

apply_theme()

st.caption("PERSONALIZED KNIT / CROCHET PATTERNS")
st.title("Not a size chart. Your own measurements.")
st.write(
    "Every pattern comes with stitch and row counts calculated from your own "
    "swatch and body measurements — not S/M/L, made for you."
)

st.divider()

pages = st.session_state.get("_nav_pages", {})


def nav_card(col, key, title, description, label):
    with col:
        st.subheader(title)
        st.write(description)
        if st.button(label, key=f"nav_{key}"):
            st.switch_page(pages[key])


col1, col2, col3 = st.columns(3)
nav_card(col1, "patterns", "Patterns",
         "Pick a pattern, enter your measurements, download your personal Excel sheet.",
         "Go to patterns →")
nav_card(col2, "gauge", "Gauge Converter",
         "Calculate your real gauge from a swatch and get a needle size suggestion.",
         "Open →")
nav_card(col3, "yarn", "Yarn Calculator",
         "Get a rough yarn estimate based on project type.",
         "Open →")

col4, col5 = st.columns(2)
nav_card(col4, "scaler", "Pattern Scaler",
         "Recalculate a stitch/row count for a different gauge or size.",
         "Open →")
nav_card(col5, "rows", "Row Counter",
         "Track multiple projects at once.",
         "Open →")

st.divider()
st.caption(
    "This is placeholder brand copy — once you have your real brand name, "
    "story, and images, we'll fill this in together."
)
