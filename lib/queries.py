# lib/queries.py (exemple)
import streamlit as st
from lib.db import get_conn

@st.cache_data(ttl=5)  # 5s pour rester “frais” mais éviter les reruns coûteux
def list_leagues():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, created_at FROM leagues ORDER BY created_at DESC;")
        return cur.fetchall()

# Quand tu crées / modifies des données, invalide juste le cache concerné:
# st.cache_data.clear()  -> global
# ou utilise une clé: list_leagues.clear()
