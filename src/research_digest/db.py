import sqlite3
import os
import uuid
from datetime import datetime


def init_db():
    conn = sqlite3.connect("awesome-cli.db")

    cursor = conn.cursor()

    if not os.path.isfile("awesome-cli.db"):
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS entry (
        entry_id TEXT PRIMARY KEY,
        summary TEXT NOT NULL,
        action_item TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
""")

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS tag (
        tag_id TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
""")

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS entry_tag (
        tag_id TEXT,
        entry_id TEXT,
        
        PRIMARY KEY(tag_id, entry_id)
    )
""")
    conn.close()


def create_tuple(tag):
    return (uuid.uuid4(), tag)


def add_entry(entry):
    # 1. Prepare the query
    placeholders = ", ".join(["?"] * len(entry.tags))
    query = f"SELECT tag_id, name FROM tag WHERE name IN ({placeholders})"

    with sqlite3.connect("awesome-cli.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, entry.tags)

        # 2. Extract the NAMES of the tags that already exist (row[1])
        found_tag_names = [row[1] for row in cursor.fetchall()]

        # 3. Filter down to ONLY the tags that are missing from the database
        missing_tag_names = [name for name in entry.tags if name not in found_tag_names]

        # 4. If there are any missing tags, insert them
        if missing_tag_names:
            # Map the create_tuple function ONLY over the missing tags
            new_tags = list(map(create_tuple, missing_tag_names))

            cursor.executemany("INSERT INTO tag (tag_id, name) VALUES (?, ?)", new_tags)

        date_now = datetime.now()
        entry_list = [
            uuid.uuid4(),
            entry.summary,
            entry.action_item,
            date_now.isoformat(),
        ]

        cursor.execute(
            "INSERT INTO entry (entry_id, summary, action_item, created_at) VALUES (?, ?, ?, ?)",
            entry_list,
        )
