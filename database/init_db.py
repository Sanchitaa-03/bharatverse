"""
init_db.py
-----------
This script creates the BharatVerse SQLite database and fills it with
starting data (realms, levels, choices, sites, timeline, treasures,
achievements). Run this once before starting the app, or any time you
want to reset the database to a fresh state.

BEGINNER NOTE:
A "database" is just an organized file where we store information that
needs to survive between visits - like user accounts and game progress.
SQLite stores the whole database in a single file: bharatverse.db
"""


import json
import os
import sqlite3


# Figure out where this script lives, so paths work no matter where
# you run the script from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Vercel's filesystem is read-only except /tmp. DATABASE_PATH can override
# this for local testing or a mounted persistent volume.
DB_PATH = os.environ.get(
    "DATABASE_PATH",
    "/tmp/bharatverse.db" if os.environ.get("VERCEL") else os.path.join(BASE_DIR, "database", "bharatverse.db"),
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS player_stats (
    user_id INTEGER PRIMARY KEY,
    water INTEGER DEFAULT 0,
    food INTEGER DEFAULT 0,
    settlement INTEGER DEFAULT 0,
    infrastructure INTEGER DEFAULT 0,
    wellbeing INTEGER DEFAULT 0,
    knowledge_xp INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS realms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    icon TEXT,
    description TEXT,
    period TEXT,
    status TEXT DEFAULT 'locked',
    order_index INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    realm_id INTEGER NOT NULL,
    level_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    scenario TEXT,
    description TEXT,
    resources TEXT,
    xp_reward INTEGER DEFAULT 100,
    treasure_id INTEGER,
    achievement_id INTEGER,
    historical_context TEXT,
    key_learning TEXT,
    source TEXT,
    FOREIGN KEY (realm_id) REFERENCES realms(id)
);

CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level_id INTEGER NOT NULL,
    choice_text TEXT NOT NULL,
    effects_json TEXT NOT NULL,
    consequence_message TEXT,
    order_index INTEGER DEFAULT 0,
    FOREIGN KEY (level_id) REFERENCES levels(id)
);

CREATE TABLE IF NOT EXISTS player_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    level_id INTEGER NOT NULL,
    status TEXT DEFAULT 'locked',  -- locked, unlocked, completed
    chosen_choice_id INTEGER,
    completed_at TEXT,
    UNIQUE(user_id, level_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (level_id) REFERENCES levels(id)
);

CREATE TABLE IF NOT EXISTS treasures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    icon TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS player_treasures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    treasure_id INTEGER NOT NULL,
    unlocked_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, treasure_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (treasure_id) REFERENCES treasures(id)
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    icon TEXT,
    description TEXT,
    criteria TEXT
);

CREATE TABLE IF NOT EXISTS player_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

CREATE TABLE IF NOT EXISTS civilization_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    realm_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    region TEXT,
    importance TEXT,
    fact TEXT,
    x REAL,
    y REAL,
    FOREIGN KEY (realm_id) REFERENCES realms(id)
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    realm_id INTEGER NOT NULL,
    period TEXT,
    event TEXT,
    explanation TEXT,
    order_index INTEGER DEFAULT 0,
    FOREIGN KEY (realm_id) REFERENCES realms(id)
);
"""


def get_connection():
    """Open a connection to the database file."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    conn.executescript(SCHEMA)
    conn.commit()


def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def seed_realms(conn, realms_data):
    for r in realms_data["realms"]:
        conn.execute(
            """INSERT OR IGNORE INTO realms (key, name, icon, description, period, status, order_index)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (r["key"], r["name"], r["icon"], r["description"], r["period"], r["status"], r["order_index"])
        )
    conn.commit()


def seed_treasures_and_achievements(conn, realms_data):
    for t in realms_data["treasures"]:
        conn.execute(
            "INSERT OR IGNORE INTO treasures (key, name, icon, description) VALUES (?, ?, ?, ?)",
            (t["key"], t["name"], t["icon"], t["description"])
        )
    for a in realms_data["achievements"]:
        conn.execute(
            "INSERT OR IGNORE INTO achievements (key, name, icon, description, criteria) VALUES (?, ?, ?, ?, ?)",
            (a["key"], a["name"], a["icon"], a["description"], a["criteria"])
        )
    conn.commit()


def seed_sites_and_timeline(conn, realms_data):
    for s in realms_data["civilization_sites"]:
        realm_id = conn.execute("SELECT id FROM realms WHERE key = ?", (s["realm_key"],)).fetchone()["id"]
        conn.execute(
            """INSERT INTO civilization_sites (realm_id, name, region, importance, fact, x, y)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (realm_id, s["name"], s["region"], s["importance"], s["fact"], s["x"], s["y"])
        )
    for t in realms_data["timeline_events"]:
        realm_id = conn.execute("SELECT id FROM realms WHERE key = ?", (t["realm_key"],)).fetchone()["id"]
        conn.execute(
            """INSERT INTO timeline_events (realm_id, period, event, explanation, order_index)
               VALUES (?, ?, ?, ?, ?)""",
            (realm_id, t["period"], t["event"], t["explanation"], t["order_index"])
        )
    conn.commit()


def seed_indus_valley_levels(conn, indus_data):
    realm_id = conn.execute("SELECT id FROM realms WHERE key = ?", ("indus_valley",)).fetchone()["id"]

    for lvl in indus_data["levels"]:
        treasure_id = None
        if lvl.get("treasure_key"):
            row = conn.execute("SELECT id FROM treasures WHERE key = ?", (lvl["treasure_key"],)).fetchone()
            treasure_id = row["id"] if row else None

        achievement_id = None
        if lvl.get("achievement_key"):
            row = conn.execute("SELECT id FROM achievements WHERE key = ?", (lvl["achievement_key"],)).fetchone()
            achievement_id = row["id"] if row else None

        cur = conn.execute(
            """INSERT INTO levels (realm_id, level_number, title, scenario, description, resources,
                                    xp_reward, treasure_id, achievement_id,
                                    historical_context, key_learning, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (realm_id, lvl["level_number"], lvl["title"], lvl["scenario"], lvl["description"],
             lvl["resources"], lvl["xp_reward"], treasure_id, achievement_id,
             lvl["historical_context"], lvl["key_learning"], lvl["source"])
        )
        level_id = cur.lastrowid

        for idx, choice in enumerate(lvl["choices"]):
            conn.execute(
                """INSERT INTO choices (level_id, choice_text, effects_json, consequence_message, order_index)
                   VALUES (?, ?, ?, ?, ?)""",
                (level_id, choice["text"], json.dumps(choice["effects"]), choice["consequence"], idx)
            )
    conn.commit()


def seed_demo_leaderboard(conn):
    """Insert a few clearly-labeled demo accounts so the leaderboard isn't
    empty before real students have played. Passwords are not usable for
    real login (they are marked as demo)."""
    from werkzeug.security import generate_password_hash

    demo_users = [
        ("Arya (Demo)", "arya_demo@example.com", 2450),
        ("Veer (Demo)", "veer_demo@example.com", 2200),
        ("Kavya (Demo)", "kavya_demo@example.com", 1980),
    ]
    for username, email, xp in demo_users:
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            continue
        pw_hash = generate_password_hash("demo-account-not-a-real-login")
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, pw_hash)
        )
        user_id = cur.lastrowid
        conn.execute(
            "INSERT INTO player_stats (user_id, water, food, settlement, infrastructure, wellbeing, knowledge_xp) "
            "VALUES (?, 50, 50, 50, 50, 50, ?)",
            (user_id, xp)
        )
    conn.commit()


def ensure_student_demo_account():
    """Ensure the login-page student demo account exists on every app start."""
    from werkzeug.security import generate_password_hash

    conn = get_connection()
    username = "Student Demo"
    email = "student_demo@example.com"
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if not existing:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, generate_password_hash("student123"))
        )
        conn.execute(
            "INSERT INTO player_stats (user_id, water, food, settlement, infrastructure, wellbeing, knowledge_xp) "
            "VALUES (?, 50, 50, 50, 50, 50, 0)",
            (cur.lastrowid,)
        )
        conn.commit()
    conn.close()


def initialize_database():
    fresh = not os.path.exists(DB_PATH)
    conn = get_connection()
    create_tables(conn)

    realms_data = load_json("realms.json")
    indus_data = load_json("indus_valley.json")

    seed_realms(conn, realms_data)
    seed_treasures_and_achievements(conn, realms_data)
    seed_sites_and_timeline(conn, realms_data)

    # Only seed levels once (avoid duplicate levels on re-run)
    count = conn.execute("SELECT COUNT(*) as c FROM levels").fetchone()["c"]
    if count == 0:
        seed_indus_valley_levels(conn, indus_data)

    seed_demo_leaderboard(conn)

    conn.close()
    print("Database ready at:", DB_PATH, "(fresh install)" if fresh else "(existing db updated)")


if __name__ == "__main__":
    initialize_database()
