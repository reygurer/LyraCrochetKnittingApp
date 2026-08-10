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
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

        .stApp {{ background-color: {BG}; font-family: 'Inter', sans-serif; }}

        /* Main content text */
        .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
        .stMarkdown, .stCaption {{
            color: {INK} !important;
            font-family: 'Inter', sans-serif;
        }}
        .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
            color: {INK} !important;
            font-family: 'Fraunces', serif;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            color: {INK} !important;
        }}

        /* Brand eyebrow — the small uppercase caption used at the top of
           each page (e.g. "PERSONALIZED KNIT / CROCHET PATTERNS"). */
        .brand-eyebrow {{
            color: {GOLD} !important;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 0.78rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }}

        /* Cards — anything built with st.container(border=True), used for
           the pattern library and the home page nav tiles. Gives both the
           same rounded, warm-bordered look instead of Streamlit's default
           thin grey box. */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #F7F2E4;
            border: 1px solid {LINE} !important;
            border-radius: 14px !important;
            transition: box-shadow 0.15s ease, border-color 0.15s ease;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: {GOLD} !important;
            box-shadow: 0 3px 14px rgba(35, 42, 34, 0.08);
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
            border-radius: 8px;
            transition: box-shadow 0.15s ease, transform 0.05s ease;
        }}
        .stButton > button:hover {{
            box-shadow: 0 2px 8px rgba(35, 42, 34, 0.12);
        }}
        .stButton > button:active {{
            transform: translateY(1px);
        }}
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {{
            color: {INK} !important;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {GOLD};
            color: #ffffff !important;
            border: none;
        }}
        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 2px 10px rgba(185, 138, 46, 0.35);
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


def eyebrow(text):
    """Small uppercase gold caption used at the top of each page, in place
    of st.caption (which is styled plainly elsewhere, e.g. 'Signed in as
    ...' labels — this one is specifically for the brand line)."""
    st.markdown(f'<div class="brand-eyebrow">{text}</div>', unsafe_allow_html=True)
