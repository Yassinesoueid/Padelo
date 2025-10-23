import os
import streamlit as st

st.set_page_config(page_title="Padel League", page_icon="🎾", layout="wide")
st.title("🎾 Padel League Manager — Cloud (Supabase)")
st.markdown("""
Use the pages in the left sidebar:

- **Leagues** — create/delete leagues
- **Players** — add players and assign them to a league
- **New Match** — record results
- **Standings** — live classification (download CSV/Excel)
- **Matches** — history (delete any match)
- **Rules** — points system

ℹ️ Data is stored in **Supabase Postgres** (set `DATABASE_URL` in Streamlit secrets).
""")

# small check to help users
if not os.getenv("DATABASE_URL"):
    st.warning("DATABASE_URL is not set. Set it in Streamlit secrets before deploying.")