"""
Single entry point. Run with:  streamlit run streamlit_app.py

Uses st.navigation + st.Page instead of the automatic pages/ folder
convention — the latter has a known page_link/url_pathname bug in some
Streamlit versions. This is the approach Streamlit's own docs recommend
for anything beyond the simplest case.
"""
import streamlit as st
from auto_seed import ensure_default_patterns

st.set_page_config(page_title="Personalized Knit/Crochet Patterns", page_icon="🧶", layout="centered")

# Recreates the default patterns if they're missing — needed on hosts where
# there's no shell to run seed_demo.py / add_pattern_aurelia.py by hand, and
# on hosts where a SQLite database resets on every redeploy.
ensure_default_patterns()

PAGES = {
    "home": st.Page("views/home.py", title="Home", url_path="home", default=True),
    "patterns": st.Page("views/patterns.py", title="Patterns", url_path="patterns"),
    "gauge": st.Page("views/gauge_converter.py", title="Gauge Converter", url_path="gauge-converter"),
    "yarn": st.Page("views/yarn_calculator.py", title="Yarn Calculator", url_path="yarn-calculator"),
    "scaler": st.Page("views/pattern_scaler.py", title="Pattern Scaler", url_path="pattern-scaler"),
    "rows": st.Page("views/row_counter.py", title="Row Counter", url_path="row-counter"),
}

# So views/home.py can switch pages on button click.
st.session_state["_nav_pages"] = PAGES

nav = st.navigation(list(PAGES.values()))
nav.run()
