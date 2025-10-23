# 🎾 Padel League — Streamlit Cloud + Supabase (Mobile friendly)

This version uses **Supabase Postgres** so everyone can access the same data from their phones.

## 1) Create a free Supabase project
- https://supabase.com/ → New project → copy the **Database connection string** (URI)
- It looks like: `postgresql://postgres:YOUR-PASSWORD@YOUR-HOST:6543/postgres`
- Keep it safe.

## 2) Push this code to GitHub

## 3) Deploy to Streamlit Community Cloud (free)
- https://share.streamlit.io/ → “New app” → point to your GitHub repo
- In **Advanced settings → Secrets**, add:
```
DATABASE_URL = "postgresql://postgres:YOUR-PASSWORD@YOUR-HOST:6543/postgres"
```
- Deploy. You’ll get a public URL you can open on your phone.

## 4) Use the app
- Create a league, add players, record matches, and see standings.
- You can **delete matches** and **download the standings** (CSV/Excel).

## Notes
- Tables are auto-created at first request.
- For auth/roles later, add Supabase Auth and gate “write” operations by role/token.