import streamlit as st
from models import SessionLocal, Project, init_db
from theme import apply_theme

apply_theme()
st.title("Row Counter")
init_db()

if "rt_db" not in st.session_state:
    st.session_state.rt_db = SessionLocal()
session = st.session_state.rt_db

with st.expander("Add a new project"):
    name = st.text_input("Project name")
    total = st.number_input("Total row count (if known)", min_value=0, value=0)
    if st.button("Add") and name:
        session.add(Project(name=name, total_rows=total, current_row=0))
        session.commit()
        st.rerun()

projects = session.query(Project).all()

if not projects:
    st.info("No projects yet, add one above.")

for p in projects:
    with st.container(border=True):
        st.subheader(p.name)
        progress_text = f"{p.current_row} / {p.total_rows}" if p.total_rows else str(p.current_row)
        st.write(f"Row: **{progress_text}**")

        c1, c2, c3, c4 = st.columns(4)
        if c1.button("−1", key=f"minus_{p.id}") and p.current_row > 0:
            p.current_row -= 1
            session.commit()
            st.rerun()
        if c2.button("+1", key=f"plus_{p.id}"):
            p.current_row += 1
            session.commit()
            st.rerun()
        if c3.button("Reset", key=f"reset_{p.id}"):
            p.current_row = 0
            session.commit()
            st.rerun()
        if c4.button("Delete", key=f"del_{p.id}"):
            session.delete(p)
            session.commit()
            st.rerun()

        note = st.text_input("Note", value=p.notes or "", key=f"note_{p.id}")
        if note != (p.notes or ""):
            p.notes = note
            session.commit()
