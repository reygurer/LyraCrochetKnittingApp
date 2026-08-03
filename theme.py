import streamlit as st

BG = "#EDE7D9"
INK = "#232A22"
GOLD = "#B98A2E"
LINE = "#D8CFB8"
SIDEBAR_BG = "#2F4538"
SIDEBAR_TEXT = "#F4F1E8"


def apply_theme():
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {BG}; }}

        /* Main content text */
        .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        .stMarkdown, .stCaption {{
            color: {INK} !important;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            color: {INK} !important;
        }}

        /* Sidebar nav — its own background + light text, independent of the
           dark-ink rule above (fixes invisible/low-contrast menu items).
           Streamlit dims inactive nav links via opacity, so that's forced
           back to full strength too, not just the color. */
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG} !important;
        }}
        [data-testid="stSidebar"] *,
        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNav"] span,
        [data-testid="stSidebarNavLink"],
        [data-testid="stSidebarNavLink"] *,
        [data-testid="stSidebarNavItems"] * {{
            color: {SIDEBAR_TEXT} !important;
            opacity: 1 !important;
            font-weight: 500 !important;
        }}
        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            background-color: rgba(244, 241, 232, 0.15) !important;
        }}

        /* Buttons — explicit background+text pair so contrast never depends
           on Streamlit's own light/dark theme (fixes invisible "Open" text).
           Streamlit renders the button label inside a child <p>/<span>, and
           the broad ".stApp p/span" rule above applies directly to that
           child (not inherited), so it can silently win over the color set
           on the <button> itself. These descendant selectors are more
           specific, so they always win regardless of rule order. */
        .stButton > button {{
            background-color: #ffffff;
            color: {INK} !important;
            border: 1px solid {INK};
        }}
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {{
            color: {INK} !important;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {INK};
            color: #ffffff !important;
            border: none;
        }}
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] span,
        .stButton > button[kind="primary"] div {{
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
