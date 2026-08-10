import io
import streamlit as st
from sqlalchemy.exc import IntegrityError

from models import SessionLocal, Pattern, Unlock, PurchaseAuthorization, init_db
from formula_engine import compute_all, render_instructions
from excel_export import build_workbook
from theme import apply_theme, eyebrow

apply_theme()
init_db()


def get_session():
    if "db" not in st.session_state:
        st.session_state.db = SessionLocal()
    return st.session_state.db


def go(step, **kwargs):
    st.session_state.step = step
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


def load_unlocked(session, email):
    """All pattern ids this email has previously unlocked (from the DB, not
    just this browser session — so it follows the buyer across devices)."""
    rows = session.query(Unlock.pattern_id).filter_by(email=email).all()
    return {row[0] for row in rows}


def sign_in(email):
    email = email.strip().lower()
    st.session_state.user_email = email
    st.query_params["email"] = email
    st.session_state.unlocked = load_unlocked(get_session(), email)
    go("library")


def sign_out():
    st.session_state.pop("user_email", None)
    st.session_state.unlocked = set()
    if "email" in st.query_params:
        del st.query_params["email"]
    go("login")


if "step" not in st.session_state:
    st.session_state.step = "login"
if "unlocked" not in st.session_state:
    st.session_state.unlocked = set()

session = get_session()
eyebrow("Personalized Knit / Crochet Patterns")

# Returning visit via a bookmarked/shared link with ?email=... in the URL —
# skip straight past the login screen.
if "user_email" not in st.session_state and "email" in st.query_params:
    sign_in(st.query_params["email"])

# ---------------------------------------------------------------- LOGIN
if st.session_state.step == "login" and "user_email" not in st.session_state:
    st.title("Sign in")
    st.write(
        "Enter the email you used on Etsy. This is how the app remembers "
        "which patterns you've already unlocked — no password needed."
    )
    email_input = st.text_input("Email")
    if st.button("Continue", type="primary"):
        if email_input and "@" in email_input:
            sign_in(email_input)
        else:
            st.error("Enter a valid email.")

# ---------------------------------------------------------------- LIBRARY
elif st.session_state.step == "library":
    top_l, top_r = st.columns([4, 1])
    with top_l:
        st.title("Choose a pattern")
    with top_r:
        st.caption(f"Signed in as **{st.session_state.user_email}**")
        if st.button("Not you? Sign out"):
            sign_out()

    patterns = session.query(Pattern).all()

    if not patterns:
        st.info("No patterns added yet. Run `python3 seed_demo.py` to add the test data.")

    for p in patterns:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(p.name)
                st.write(p.description)
            with col2:
                st.caption(p.tag or ("free" if p.is_free else "locked"))

            if p.is_free:
                if st.button("Open", key=f"open_{p.id}"):
                    go("form", pattern_id=p.id)
            else:
                if p.id in st.session_state.unlocked:
                    if st.button("Open", key=f"open_{p.id}"):
                        go("form", pattern_id=p.id)
                else:
                    with st.expander("Unlock with a key"):
                        key_input = st.text_input(
                            "Your access key for this pattern", type="password", key=f"key_{p.id}"
                        )
                        if st.button("Verify", key=f"verify_{p.id}"):
                            authorized = (
                                session.query(PurchaseAuthorization)
                                .filter_by(email=st.session_state.user_email, pattern_id=p.id)
                                .first()
                            )
                            if not authorized:
                                # This email has no recorded Etsy order for this
                                # pattern (see add_order.py) — the key alone
                                # isn't enough, even if it's correct.
                                st.error(
                                    "We don't have an order on file for this email and "
                                    "pattern. Make sure you're using the same email you "
                                    "checked out with on Etsy."
                                )
                            elif key_input and key_input == p.access_key:
                                # Persist the unlock against this email so it's
                                # remembered next time, on any device.
                                try:
                                    session.add(Unlock(email=st.session_state.user_email, pattern_id=p.id))
                                    session.commit()
                                except IntegrityError:
                                    session.rollback()  # already unlocked, ignore
                                st.session_state.unlocked.add(p.id)
                                go("form", pattern_id=p.id)
                            else:
                                st.error("Wrong key.")

# ---------------------------------------------------------------- FORM
elif st.session_state.step == "form":
    pattern = session.query(Pattern).get(st.session_state.pattern_id)

    if st.button("← Back to patterns"):
        go("library")

    st.title(pattern.name)

    # Reachable only from the library once this pattern is free or already
    # unlocked (see the LIBRARY step above) — both the video and the form
    # below are gated behind purchase that way, no extra check needed here.

    if "inputs" not in st.session_state or st.session_state.get("inputs_pattern_id") != pattern.id:
        st.session_state.inputs = {}
        st.session_state.inputs_pattern_id = pattern.id

    def field_group(title, fields):
        if not fields:
            return
        st.subheader(title)
        for f in fields:
            st.session_state.inputs[f["id"]] = st.number_input(
                f["label"],
                value=float(st.session_state.inputs.get(f["id"], 0.0)),
                key=f"input_{pattern.id}_{f['id']}",
            )

    def render_written_form():
        field_group("Swatch measurements", pattern.swatch_fields)
        field_group("Yarn info", pattern.yarn_fields)
        field_group("Body measurements", pattern.measurement_fields)

        if st.button("Calculate my numbers", type="primary"):
            go("results", pattern_id=pattern.id)

    if pattern.video_url:
        # Two explicit options, instead of stacking the video above the
        # form — buyer picks one before doing anything else.
        tab_video, tab_written = st.tabs(["Watch video", "Written pattern & measurements"])
        with tab_video:
            st.video(pattern.video_url)
        with tab_written:
            render_written_form()
    else:
        # No video for this pattern — go straight to the written form,
        # same as before.
        render_written_form()

# ---------------------------------------------------------------- RESULTS
elif st.session_state.step == "results":
    pattern = session.query(Pattern).get(st.session_state.pattern_id)
    inputs = st.session_state.inputs

    results, yarn = compute_all(pattern, inputs)

    if st.button("← Edit measurements"):
        go("form", pattern_id=pattern.id)

    st.title("Your numbers")

    with st.container(border=True):
        for f in pattern.computed_fields:
            c1, c2 = st.columns([3, 1])
            c1.write(f["label"])
            c2.write(f"**{results[f['id']]}**")
        if yarn:
            c1, c2 = st.columns([3, 1])
            c1.write("Estimated total yarn")
            c2.write(f"**{yarn['total_meters']:.0f} m / {yarn['total_weight']:.0f} g**")

    if pattern.instructions_template:
        st.subheader("Instructions with your numbers")
        st.write(render_instructions(pattern, results))

    wb = build_workbook(pattern, inputs, results, yarn)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    st.download_button(
        "Download as Excel",
        data=buf,
        file_name=f"{pattern.slug}-your-numbers.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
