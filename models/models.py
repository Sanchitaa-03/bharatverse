"""
models.py
----------
This file contains helper functions that talk to the database.

BEGINNER NOTE:
Rather than writing raw SQL everywhere in our routes, we collect the
common database operations here as small, well-named functions
(e.g. get_user_by_id). This keeps our route files clean and readable.
"""

import sqlite3
import os
import json

from config import Config

DB_PATH = Config.DATABASE_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------- USERS ----------

def create_user(username, email, password_hash):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    user_id = cur.lastrowid
    conn.execute(
        "INSERT INTO player_stats (user_id, water, food, settlement, infrastructure, wellbeing, knowledge_xp) "
        "VALUES (?, 50, 50, 50, 50, 50, 0)",
        (user_id,)
    )
    conn.commit()
    conn.close()
    return user_id


def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


# ---------- STATS ----------

def get_player_stats(user_id):
    conn = get_db()
    stats = conn.execute("SELECT * FROM player_stats WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return stats


def update_player_stats(user_id, effects, xp_gained):
    """effects is a dict like {'water': 10, 'wellbeing': -5}"""
    conn = get_db()
    stats = conn.execute("SELECT * FROM player_stats WHERE user_id = ?", (user_id,)).fetchone()

    new_values = {}
    for key in ["water", "food", "settlement", "infrastructure", "wellbeing"]:
        current = stats[key] if stats else 0
        change = effects.get(key, 0)
        new_val = max(0, min(100, current + change))  # keep stats between 0-100
        new_values[key] = new_val

    new_xp = (stats["knowledge_xp"] if stats else 0) + xp_gained

    conn.execute(
        """UPDATE player_stats SET water=?, food=?, settlement=?, infrastructure=?, wellbeing=?, knowledge_xp=?
           WHERE user_id=?""",
        (new_values["water"], new_values["food"], new_values["settlement"],
         new_values["infrastructure"], new_values["wellbeing"], new_xp, user_id)
    )
    conn.commit()
    conn.close()
    return new_values, new_xp


def civilization_score(stats):
    """A simple combined score used for the leaderboard and result screens."""
    if not stats:
        return 0
    total = stats["water"] + stats["food"] + stats["settlement"] + stats["infrastructure"] + stats["wellbeing"]
    return round(total / 5)


# ---------- REALMS ----------

def get_all_realms():
    conn = get_db()
    realms = conn.execute("SELECT * FROM realms ORDER BY order_index").fetchall()
    conn.close()
    return realms


def get_realm_by_key(key):
    conn = get_db()
    realm = conn.execute("SELECT * FROM realms WHERE key = ?", (key,)).fetchone()
    conn.close()
    return realm


# ---------- LEVELS & CHOICES ----------

def get_levels_for_realm(realm_id):
    conn = get_db()
    levels = conn.execute(
        "SELECT * FROM levels WHERE realm_id = ? ORDER BY level_number", (realm_id,)
    ).fetchall()
    conn.close()
    return levels


def get_level_by_id(level_id):
    conn = get_db()
    level = conn.execute("SELECT * FROM levels WHERE id = ?", (level_id,)).fetchone()
    conn.close()
    return level


def get_choices_for_level(level_id):
    conn = get_db()
    choices = conn.execute(
        "SELECT * FROM choices WHERE level_id = ? ORDER BY order_index", (level_id,)
    ).fetchall()
    conn.close()
    return choices


def get_choice_by_id(choice_id):
    conn = get_db()
    choice = conn.execute("SELECT * FROM choices WHERE id = ?", (choice_id,)).fetchone()
    conn.close()
    return choice


# ---------- PROGRESS ----------

def ensure_progress_initialized(user_id, realm_id):
    """Make sure the player has a progress row for every level in a realm.
    The first level starts 'unlocked'; all others start 'locked'."""
    conn = get_db()
    levels = conn.execute(
        "SELECT * FROM levels WHERE realm_id = ? ORDER BY level_number", (realm_id,)
    ).fetchall()

    for level in levels:
        existing = conn.execute(
            "SELECT * FROM player_progress WHERE user_id = ? AND level_id = ?",
            (user_id, level["id"])
        ).fetchone()
        if not existing:
            status = "unlocked" if level["level_number"] == 1 else "locked"
            conn.execute(
                "INSERT INTO player_progress (user_id, level_id, status) VALUES (?, ?, ?)",
                (user_id, level["id"], status)
            )
    conn.commit()
    conn.close()


def get_progress_for_realm(user_id, realm_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT pp.*, l.level_number, l.title FROM player_progress pp
           JOIN levels l ON pp.level_id = l.id
           WHERE pp.user_id = ? AND l.realm_id = ?
           ORDER BY l.level_number""",
        (user_id, realm_id)
    ).fetchall()
    conn.close()
    return rows


def get_progress_for_level(user_id, level_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM player_progress WHERE user_id = ? AND level_id = ?",
        (user_id, level_id)
    ).fetchone()
    conn.close()
    return row


def complete_level(user_id, level_id, choice_id):
    conn = get_db()
    conn.execute(
        """UPDATE player_progress SET status='completed', chosen_choice_id=?, completed_at=datetime('now')
           WHERE user_id=? AND level_id=?""",
        (choice_id, user_id, level_id)
    )
    conn.commit()
    conn.close()


def unlock_next_level(user_id, realm_id, current_level_number):
    conn = get_db()
    next_level = conn.execute(
        "SELECT * FROM levels WHERE realm_id = ? AND level_number = ?",
        (realm_id, current_level_number + 1)
    ).fetchone()
    if next_level:
        conn.execute(
            "UPDATE player_progress SET status='unlocked' WHERE user_id=? AND level_id=? AND status='locked'",
            (user_id, next_level["id"])
        )
        conn.commit()
    conn.close()
    return next_level


def is_realm_completed(user_id, realm_id):
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) c FROM levels WHERE realm_id=?", (realm_id,)).fetchone()["c"]
    completed = conn.execute(
        """SELECT COUNT(*) c FROM player_progress pp JOIN levels l ON pp.level_id=l.id
           WHERE pp.user_id=? AND l.realm_id=? AND pp.status='completed'""",
        (user_id, realm_id)
    ).fetchone()["c"]
    conn.close()
    return total > 0 and total == completed


# ---------- TREASURES & ACHIEVEMENTS ----------

def award_treasure(user_id, treasure_id):
    if not treasure_id:
        return None
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO player_treasures (user_id, treasure_id) VALUES (?, ?)",
        (user_id, treasure_id)
    )
    conn.commit()
    treasure = conn.execute("SELECT * FROM treasures WHERE id=?", (treasure_id,)).fetchone()
    conn.close()
    return treasure


def award_achievement(user_id, achievement_id):
    if not achievement_id:
        return None
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO player_achievements (user_id, achievement_id) VALUES (?, ?)",
        (user_id, achievement_id)
    )
    conn.commit()
    achievement = conn.execute("SELECT * FROM achievements WHERE id=?", (achievement_id,)).fetchone()
    conn.close()
    return achievement


def get_player_treasures(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT t.* FROM player_treasures pt JOIN treasures t ON pt.treasure_id = t.id
           WHERE pt.user_id = ? ORDER BY pt.unlocked_at""",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def get_player_achievements(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT a.* FROM player_achievements pa JOIN achievements a ON pa.achievement_id = a.id
           WHERE pa.user_id = ? ORDER BY pa.unlocked_at""",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


# ---------- MAP & TIMELINE ----------

def get_sites_for_realm(realm_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM civilization_sites WHERE realm_id=?", (realm_id,)).fetchall()
    conn.close()
    return rows


def get_timeline_for_realm(realm_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM timeline_events WHERE realm_id=? ORDER BY order_index", (realm_id,)
    ).fetchall()
    conn.close()
    return rows


# ---------- LEADERBOARD ----------

def get_leaderboard(limit=20):
    conn = get_db()
    rows = conn.execute(
        """SELECT u.username, ps.knowledge_xp,
                  ps.water, ps.food, ps.settlement, ps.infrastructure, ps.wellbeing,
                  (SELECT COUNT(*) FROM player_achievements pa WHERE pa.user_id = u.id) as achievement_count
           FROM users u JOIN player_stats ps ON u.id = ps.user_id
           ORDER BY ps.knowledge_xp DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return rows
