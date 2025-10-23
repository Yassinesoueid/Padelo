import streamlit as st
from lib.db import get_leagues, create_league, delete_league

st.title("🏟️ Leagues")

with st.expander("➕ Create a new league", expanded=True):
    name = st.text_input("League name", placeholder="e.g., Padel Mafia 8 — Oct 2025")
    if st.button("Create League", type="primary", disabled=not name.strip()):
        try:
            create_league(name.strip())
            st.success(f"League '{name}' created.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

st.subheader("Existing leagues")
rows = get_leagues()
if not rows:
    st.info("No leagues yet.")
else:
    for (lid, lname, created) in rows:
        cols = st.columns([6,2])
        cols[0].markdown(f"**{lname}**  \nCreated: {created}")
        if cols[1].button("🗑️ Delete", key=f"del_{lid}"):
            delete_league(lid)
            st.success(f"League '{lname}' deleted (matches, sets, memberships removed).")
            st.rerun()