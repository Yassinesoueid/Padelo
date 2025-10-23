import streamlit as st
from lib.db import get_leagues, get_all_players, add_player, add_player_to_league, get_league_players

st.title("👥 Players")

leagues = get_leagues()
if not leagues:
    st.info("Create a league first in the **Leagues** page.")
    st.stop()

league_map = {lname: lid for (lid, lname, _c) in leagues}
league_name = st.selectbox("Select league", list(league_map.keys()))
league_id = league_map[league_name]

with st.expander("➕ Add player"):
    new_name = st.text_input("Player name", placeholder="Type name and click 'Add'")
    if st.button("Add to global players"):
        if not new_name.strip():
            st.warning("Enter a name first.")
        else:
            pid = add_player(new_name.strip())
            st.success(f"Player '{new_name}' added (id={pid}).")

all_players = get_all_players()
if not all_players:
    st.info("No players yet. Add one above.")
else:
    names = [row[1] for row in all_players]
    selected = st.multiselect("Add existing players to this league", names)
    if st.button("Add selected to league"):
        for nm in selected:
            pid = [r[0] for r in all_players if r[1]==nm][0]
            add_player_to_league(league_id, pid)
        st.success("Players added to league.")
        st.rerun()

st.subheader(f"League roster — {league_name}")
roster = get_league_players(league_id)
if not roster:
    st.info("No players in this league yet.")
else:
    st.dataframe({"Player ID":[r[0] for r in roster], "Name":[r[1] for r in roster]}, hide_index=True, use_container_width=True)