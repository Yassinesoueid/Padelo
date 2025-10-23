import streamlit as st

st.title("📘 Points System (Rules)")

st.markdown("""
- **Match Win:** +2 pts  
- **Match Loss:** −1 pt  
- **Clean Win (2–0 in sets):** +1 pt to each winner  
- **Bagel Set (6–0):** +1 pt to each winner and −1 pt to each loser
""")
st.caption("Applied automatically when you save a match.")