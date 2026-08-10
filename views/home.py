import streamlit as st
from theme import apply_theme, eyebrow

apply_theme()

eyebrow("Personalized Knit / Crochet Patterns")
st.title("Not a size chart. Your own measurements.")
st.write(
    "Every pattern comes with stitch and row counts calculated from your own "
    "swatch and body measurements — not S/M/L, made for you."
)

st.divider()

pages = st.session_state.get("_nav_pages", {})


def nav_card(col, key, title, description, label):
    with col:
        with st.container(border=True):
            st.subheader(title)
            st.write(description)
            if st.button(label, key=f"nav_{key}", use_container_width=True):
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

col4, col5, col6 = st.columns(3)
nav_card(col4, "scaler", "Pattern Scaler",
         "Recalculate a stitch/row count for a different gauge or size.",
         "Open →")
nav_card(col5, "rows", "Row Counter",
         "Track multiple projects at once.",
         "Open →")
nav_card(col6, "bodice", "Bodice Shaping Calculator",
         "Plan the bottom panel rows and bust increases from your own measurements.",
         "Open →")
