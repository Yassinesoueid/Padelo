# lib/db.py
import os
from contextlib import contextmanager
import psycopg2

# --- NEW: pool via Streamlit cache (1 seule init) ---
try:
    import streamlit as st
    from psycopg2.pool import SimpleConnectionPool

    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is missing.")

    @st.cache_resource
    def _get_pool():
        # Ajuste maxconn si besoin (3–10 sur Streamlit Cloud)
        return SimpleConnectionPool(minconn=1, maxconn=5, dsn=DATABASE_URL)

    _POOL = _get_pool()

    @contextmanager
    def get_conn():
        conn = _POOL.getconn()
        try:
            conn.autocommit = False
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _POOL.putconn(conn)

except Exception:
    # Fallback hors Streamlit (tests locaux)
    from psycopg2.pool import SimpleConnectionPool
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is missing.")
    _POOL = SimpleConnectionPool(1, 5, dsn=DATABASE_URL)

    @contextmanager
    def get_conn():
        conn = _POOL.getconn()
        try:
            conn.autocommit = False
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            _POOL.putconn(conn)

# --- Helpers optionnels (si tu les utilises déjà, garde les tiens) ---
def execute(sql: str, params: tuple | None = None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)

def fetchall(sql: str, params: tuple | None = None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def fetchone(sql: str, params: tuple | None = None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()

# --- NEW: initialization unique des tables & index ---
def init_tables_once():
    ddl = """
    CREATE TABLE IF NOT EXISTS leagues (
      id BIGSERIAL PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS players (
      id BIGSERIAL PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS matches (
      id BIGSERIAL PRIMARY KEY,
      league_id BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    -- Index utiles
    CREATE INDEX IF NOT EXISTS ix_leagues_created_at ON leagues(created_at DESC);
    CREATE INDEX IF NOT EXISTS ix_players_name ON players(name);
    CREATE INDEX IF NOT EXISTS ix_matches_league_created ON matches(league_id, created_at DESC);
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
