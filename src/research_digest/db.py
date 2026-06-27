import sqlite3
import os
import uuid
from datetime import datetime, date
from .model import Entry
from .error_models.db_error import EntryErrorException
import json


def adapt_datetime_iso(val: datetime):
    return val.isoformat()


def adapt_date_iso(val: date):
    return val.isoformat()


# Tell sqlite3 to use these rules whenever it sees a datetime or date object
sqlite3.register_adapter(datetime, adapt_datetime_iso)
sqlite3.register_adapter(date, adapt_date_iso)


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
    return (str(uuid.uuid4()), tag)


def add_entry(entry, db_path="awesome-cli.db"):
    # 1. Handle empty tags gracefully so the SQL 'IN' clause doesn't crash
    if not entry.tags:
        print("Warning: No tags provided.")
        # Depending on your app, you might want to return early here,
        # or just skip the tag logic and only insert the entry.

    entry_id = str(uuid.uuid4())
    date_now = datetime.now().isoformat()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        found_tags = []
        if entry.tags:
            placeholders = ", ".join(["?"] * len(entry.tags))
            query = f"SELECT tag_id, name FROM tag WHERE name IN ({placeholders})"
            cursor.execute(query, entry.tags)

            found_tags = cursor.fetchall()

            found_names = {row[1] for row in found_tags}
            missing_names = [name for name in entry.tags if name not in found_names]

            new_tags = []
            if missing_names:
                new_tags = [create_tuple(name) for name in missing_names]
                cursor.executemany(
                    "INSERT INTO tag (tag_id, name) VALUES (?, ?)", new_tags
                )

        entry_list = (entry_id, entry.summary, entry.action_item, date_now)
        cursor.execute(
            "INSERT INTO entry (entry_id, summary, action_item, created_at) VALUES (?, ?, ?, ?)",
            entry_list,
        )

        if entry.tags:
            all_tags = found_tags + new_tags
            entry_tags_links = [(row[0], entry_id) for row in all_tags]

            cursor.executemany(
                "INSERT INTO entry_tag (tag_id, entry_id) VALUES (?, ?)",
                entry_tags_links,
            )


def get_list(limit):

    with sqlite3.connect("awesome-cli.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ENTRY LIMIT ?", (limit,))

        cursor.execute(
            "SELECT json_object('entry_id', CAST(e.entry_id as TEXT), 'tags', json_group_array(t.name), 'summary', CAST(e.summary AS TEXT), 'action_item', CAST(e.action_item AS TEXT), 'created_at', CAST(e.created_at AS TEXT) ) FROM entry AS e JOIN entry_tag AS et ON e.entry_id = et.entry_id JOIN tag AS t ON t.tag_id = et.tag_id GROUP BY e.entry_id LIMIT ?",
            (limit,),
        )
        # rows = cursor.fetchall()

        # for row in rows:
        # print(row[0])
        entries = [Entry(**(json.loads(row[0]))) for row in cursor.fetchall()]
        print(entries)
        return entries


def search_entry(entry_id, db_path="awesome-cli.db"):

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # row = cursor.execute(
        #     "SELECT * FROM entry WHERE entry_id = ?", (entry_id,)
        # ).fetchone()
        row = cursor.execute(
            "SELECT json_object('entry_id', CAST(e.entry_id as TEXT), 'tags', json_group_array(t.name), 'summary', CAST(e.summary AS TEXT), 'action_item', CAST(e.action_item AS TEXT), 'created_at', CAST(e.created_at AS TEXT) ) FROM entry AS e JOIN entry_tag AS et ON e.entry_id = et.entry_id JOIN tag AS t ON t.tag_id = et.tag_id WHERE e.entry_id = ? GROUP BY e.entry_id",
            (entry_id,),
        ).fetchone()
        if row is None:
            raise EntryErrorException(
                message=f"ID: {entry_id} does not exist", error_code="404"
            )
        entry = json.loads(row[0])
        found_entry = Entry(**entry)

        return found_entry


def search_by_tag(tag_name, db_path="awesome-cli.db"):

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute(
            "SELECT json_object('entry_id', CAST(e.entry_id as TEXT), 'tags', json_group_array(t.name), 'summary', CAST(e.summary AS TEXT), 'action_item', CAST(e.action_item AS TEXT), 'created_at', CAST(e.created_at AS TEXT) ) FROM entry AS e JOIN entry_tag AS et ON e.entry_id = et.entry_id JOIN tag AS t ON t.tag_id = et.tag_id WHERE t.name = ? GROUP BY e.entry_id",
            (tag_name,),
        ).fetchall()
        entries = [Entry(**(json.loads(row[0]))) for row in rows]
        return entries


def search_by_summary(text, db_path="awesome-cli.db"):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute(
            "SELECT json_object('entry_id', CAST(e.entry_id as TEXT), 'tags', json_group_array(t.name), 'summary', CAST(e.summary AS TEXT), 'action_item', CAST(e.action_item AS TEXT), 'created_at', CAST(e.created_at AS TEXT) ) FROM entry AS e JOIN entry_tag AS et ON e.entry_id = et.entry_id JOIN tag AS t ON t.tag_id = et.tag_id WHERE e.summary LIKE ? GROUP BY e.entry_id",
            (f"%{text}%",),
        ).fetchall()

        entries = [Entry(**(json.loads(row[0]))) for row in rows]
        return entries
