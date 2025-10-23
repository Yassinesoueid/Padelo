import os
import psycopg2
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql://postgres:password@host:6543/postgres

def _connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is missing. Set it in Streamlit secrets or your shell.")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@contextmanager
def get_conn():
    conn = _connect()
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()

def init_tables():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
          id BIGSERIAL PRIMARY KEY,
          name TEXT UNIQUE NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
          id BIGSERIAL PRIMARY KEY,
          name TEXT UNIQUE NOT NULL
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS league_players (
          league_id BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
          player_id BIGINT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
          PRIMARY KEY (league_id, player_id)
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
          id BIGSERIAL PRIMARY KEY,
          league_id BIGINT NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
          date DATE,
          court TEXT,
          team_a_p1 BIGINT NOT NULL REFERENCES players(id),
          team_a_p2 BIGINT NOT NULL REFERENCES players(id),
          team_b_p1 BIGINT NOT NULL REFERENCES players(id),
          team_b_p2 BIGINT NOT NULL REFERENCES players(id),
          winner_team TEXT CHECK (winner_team IN ('A','B')),
          clean_win BOOLEAN DEFAULT FALSE,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS match_sets (
          id BIGSERIAL PRIMARY KEY,
          match_id BIGINT NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
          set_no INT NOT NULL,
          games_a INT NOT NULL,
          games_b INT NOT NULL
        );""")

def fetchall(query, params=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchall()

def execute(query, params=None, return_id=False):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query + (" RETURNING id" if return_id else ""), params or ())
        if return_id:
            return cur.fetchone()[0]

def create_league(name: str) -> int:
    init_tables()
    return execute("INSERT INTO leagues(name) VALUES (%s)", (name,), return_id=True)

def delete_league(league_id: int):
    init_tables()
    execute("DELETE FROM leagues WHERE id=%s", (league_id,))

def get_leagues():
    init_tables()
    return fetchall("SELECT id, name, created_at FROM leagues ORDER BY created_at DESC")

def add_player(name: str) -> int:
    init_tables()
    try:
        return execute("INSERT INTO players(name) VALUES (%s)", (name,), return_id=True)
    except Exception:
        row = fetchall("SELECT id FROM players WHERE name=%s", (name,))
        return row[0][0]

def get_all_players():
    init_tables()
    return fetchall("SELECT id, name FROM players ORDER BY name COLLATE \"C\"")

def add_player_to_league(league_id: int, player_id: int):
    init_tables()
    execute("INSERT INTO league_players(league_id, player_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (league_id, player_id))

def get_league_players(league_id: int):
    init_tables()
    return fetchall("""
        SELECT p.id, p.name
        FROM league_players lp
        JOIN players p ON p.id = lp.player_id
        WHERE lp.league_id = %s
        ORDER BY p.name COLLATE "C"
    """, (league_id,))

def insert_match(league_id:int, date:str, court:str, a1:int, a2:int, b1:int, b2:int, winner_team:str, clean_win:int):
    init_tables()
    return execute("""
        INSERT INTO matches(league_id, date, court, team_a_p1, team_a_p2, team_b_p1, team_b_p2, winner_team, clean_win)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (league_id, date, court, a1, a2, b1, b2, winner_team, bool(clean_win)), return_id=True)

def insert_match_set(match_id:int, set_no:int, games_a:int, games_b:int):
    init_tables()
    execute("INSERT INTO match_sets(match_id, set_no, games_a, games_b) VALUES (%s,%s,%s,%s)", (match_id, set_no, games_a, games_b))

def get_matches(league_id:int):
    init_tables()
    return fetchall("""
        SELECT m.id, m.date, m.court, 
               pa1.name AS team_a_p1, pa2.name AS team_a_p2,
               pb1.name AS team_b_p1, pb2.name AS team_b_p2,
               m.winner_team, m.clean_win, m.created_at
        FROM matches m
        JOIN players pa1 ON pa1.id = m.team_a_p1
        JOIN players pa2 ON pa2.id = m.team_a_p2
        JOIN players pb1 ON pb1.id = m.team_b_p1
        JOIN players pb2 ON pb2.id = m.team_b_p2
        WHERE m.league_id = %s
        ORDER BY m.created_at DESC
    """, (league_id,))

def get_match_sets(match_id:int):
    init_tables()
    return fetchall("SELECT set_no, games_a, games_b FROM match_sets WHERE match_id=%s ORDER BY set_no", (match_id,))

def delete_match(match_id:int):
    init_tables()
    execute("DELETE FROM matches WHERE id=%s", (match_id,))