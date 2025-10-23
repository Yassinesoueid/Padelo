import streamlit as st
from lib.db import get_leagues, get_matches, get_match_sets, delete_match

st.title("📜 Matches")

leagues = get_leagues()
if not leagues:
    st.info("Create a league first in the **Leagues** page.")
    st.stop()

league_map = {lname: lid for (lid, lname, _c) in leagues}
league_name = st.selectbox("Select league", list(league_map.keys()))
league_id = league_map[league_name]

rows = get_matches(league_id)
if not rows:
    st.info("No matches yet.")
else:
    for (mid, date, court, a1, a2, b1, b2, winner, clean, created) in rows:
        sets = get_match_sets(mid)
        sets_str = ", ".join(f"{ga}-{gb}" for (_no, ga, gb) in sets)
        cols = st.columns([6,2])
        with cols[0]:
            st.markdown(f"""
**Date:** {date}  
**Court:** {court or '-'}  
**Team A:** {a1} & {a2}  
**Team B:** {b1} & {b2}  
**Winner:** Team {winner}  
**Clean 2–0:** {'Yes' if bool(clean) else 'No'}  
**Sets:** {sets_str}
""")
        with cols[1]:
            if st.button("🗑️ Delete match", key=f"delm_{mid}"):
                delete_match(mid)
                st.success(f"Match {mid} deleted.")
                st.rerun()
        st.divider()