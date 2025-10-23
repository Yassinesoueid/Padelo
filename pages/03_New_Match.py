import streamlit as st
from datetime import date as dtdate
from lib.db import get_leagues, get_league_players, insert_match, insert_match_set
from lib.scoring import determine_winner_and_clean

st.title("📝 New Match")

leagues = get_leagues()
if not leagues:
    st.info("Create a league first in the **Leagues** page.")
    st.stop()

league_map = {lname: lid for (lid, lname, _c) in leagues}
league_name = st.selectbox("Select league", list(league_map.keys()))
league_id = league_map[league_name]

roster = get_league_players(league_id)
if len(roster) < 4:
    st.info("Add at least 4 players to this league in the **Players** page.")
    st.stop()

names = [r[1] for r in roster]
id_by_name = {r[1]: r[0] for r in roster}

colA, colB = st.columns(2)
with colA:
    st.subheader("Team A")
    a1 = st.selectbox("Player 1 (A)", names, key="a1")
    a2 = st.selectbox("Player 2 (A)", [n for n in names if n != a1], key="a2")
with colB:
    st.subheader("Team B")
    b1 = st.selectbox("Player 1 (B)", [n for n in names if n not in {a1,a2}], key="b1")
    b2 = st.selectbox("Player 2 (B)", [n for n in names if n not in {a1,a2,b1}], key="b2")

st.subheader("Set Scores")
st.caption("Enter at least 2 sets. Set 3 is optional.")
c1,c2,c3,c4,c5,c6 = st.columns(6)
s1a = c1.number_input("Set 1 A", min_value=0, max_value=7, value=6, step=1)
s1b = c2.number_input("Set 1 B", min_value=0, max_value=7, value=4, step=1)
s2a = c3.number_input("Set 2 A", min_value=0, max_value=7, value=6, step=1)
s2b = c4.number_input("Set 2 B", min_value=0, max_value=7, value=3, step=1)
s3a = c5.number_input("Set 3 A", min_value=0, max_value=7, value=0, step=1)
s3b = c6.number_input("Set 3 B", min_value=0, max_value=7, value=0, step=1)

date_val = st.date_input("Date", value=dtdate.today())
court = st.text_input("Court (optional)", placeholder="4Padel Boulogne, Court 2")

def validate_sets(sets):
    completed = [(a,b) for a,b in sets if not (a==0 and b==0)]
    if len(completed) < 2:
        return False, "Please enter at least two sets."
    wa = sum(1 for a,b in completed if a>b)
    wb = sum(1 for a,b in completed if b>a)
    if max(wa,wb) < 2:
        return False, "One team must win at least 2 sets."
    return True, ""

if st.button("Save Match", type="primary"):
    set_scores = [(int(s1a), int(s1b)), (int(s2a), int(s2b))]
    if (s3a, s3b) != (0,0):
        set_scores.append((int(s3a), int(s3b)))
    ok, msg = validate_sets(set_scores)
    if not ok:
        st.error(msg)
    elif len({a1,a2,b1,b2}) < 4:
        st.error("Each player must be unique across both teams.")
    else:
        winner, clean = determine_winner_and_clean(set_scores)
        mid = insert_match(
            league_id=league_id,
            date=str(date_val),
            court=court.strip(),
            a1=id_by_name[a1], a2=id_by_name[a2],
            b1=id_by_name[b1], b2=id_by_name[b2],
            winner_team=winner, clean_win=int(clean)
        )
        for i,(ga,gb) in enumerate(set_scores, start=1):
            insert_match_set(mid, i, int(ga), int(gb))
        st.success(f"Match saved (ID {mid}).")
        st.rerun()