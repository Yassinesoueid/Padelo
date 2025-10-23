import streamlit as st
import pandas as pd
from io import BytesIO
from lib.db import get_leagues, get_league_players, get_matches, get_match_sets
from lib.scoring import count_bagels

st.title("📊 Standings")

leagues = get_leagues()
if not leagues:
    st.info("Create a league first in the **Leagues** page.")
    st.stop()

league_map = {lname: lid for (lid, lname, _c) in leagues}
league_name = st.selectbox("Select league", list(league_map.keys()))
league_id = league_map[league_name]

roster = get_league_players(league_id)
if not roster:
    st.info("Add players to this league in the **Players** page.")
    st.stop()

stats = {pid: {"Player": name, "Matches Played":0, "Wins":0, "Losses":0,
               "Clean Wins (2-0)":0, "Bagels For":0, "Bagels Against":0, "Points":0}
         for (pid, name) in roster}

rows = get_matches(league_id)
if rows:
    id_by_name = {name: pid for (pid, name) in roster}
    for (mid, date, court, a1n, a2n, b1n, b2n, winner, clean, created) in rows:
        team_a = [id_by_name[a1n], id_by_name[a2n]]
        team_b = [id_by_name[b1n], id_by_name[b2n]]
        sets = [(ga,gb) for (_no, ga, gb) in get_match_sets(mid)]
        bagels_a, bagels_b = count_bagels(sets)
        for pid in team_a + team_b:
            stats[pid]["Matches Played"] += 1
        winners = team_a if winner=="A" else team_b
        losers  = team_b if winner=="A" else team_a
        for pid in winners:
            stats[pid]["Wins"] += 1
            stats[pid]["Points"] += 2
            if bool(clean):
                stats[pid]["Clean Wins (2-0)"] += 1
                stats[pid]["Points"] += 1
        for pid in losers:
            stats[pid]["Losses"] += 1
            stats[pid]["Points"] -= 1
        for pid in team_a:
            stats[pid]["Bagels For"] += bagels_a
            stats[pid]["Bagels Against"] += bagels_b
            stats[pid]["Points"] += bagels_a
            stats[pid]["Points"] -= bagels_b
        for pid in team_b:
            stats[pid]["Bagels For"] += bagels_b
            stats[pid]["Bagels Against"] += bagels_a
            stats[pid]["Points"] += bagels_b
            stats[pid]["Points"] -= bagels_a

df = pd.DataFrame(stats).T
df = df[["Player","Matches Played","Wins","Losses","Clean Wins (2-0)","Bagels For","Bagels Against","Points"]]
df = df.sort_values(by=["Points","Wins","Bagels For"], ascending=[False, False, False]).reset_index(drop=True)

st.subheader(f"League standings — {league_name}")
st.dataframe(df, hide_index=True, use_container_width=True)

st.markdown("### ⬇️ Download standings")
c1, c2 = st.columns(2)
csv_bytes = df.to_csv(index=False).encode("utf-8")
c1.download_button("Download CSV", data=csv_bytes, file_name=f"{league_name}_standings.csv", mime="text/csv")
output = BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as w:
    df.to_excel(w, sheet_name="Standings", index=False)
c2.download_button("Download Excel (.xlsx)", data=output.getvalue(),
                   file_name=f"{league_name}_standings.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")