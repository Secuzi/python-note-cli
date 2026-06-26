import pytest
from src.research_digest.db import add_entry, search_entry
from src.research_digest.model import EntryCreate
import sqlite3
from datetime import datetime
from src.research_digest.error_models.db_error import EntryErrorException


def create_dummy_entry():
    created_at = datetime.fromisoformat("2026-06-26 17:11:23")

    entry = {
        "entry_id": "123",
        "summary": "Fixture allows you to setup configurations",
        "action_item": "Create a small project with fixture",
        "created_at": created_at,
    }

    return entry


# Fixture Setup
@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    conn = sqlite3.connect(path)

    cursor = conn.cursor()

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
    return path


def test_add_entry_with_no_tags(db_path):

    entry = EntryCreate(
        summary="Pytest is a testing library",
        tags=["python", "testing"],
        action_item="Create a small project with testing",
    )

    add_entry(entry, db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # returns an array of single tuple
    tags = cursor.execute("SELECT name FROM tag").fetchall()

    assert {tag[0] for tag in tags} == {"python", "testing"}

    # Check if entry_tags table has it as well

    entry_tags = cursor.execute("SELECT * FROM entry_tag").fetchall()
    assert len(entry_tags) == 2
    conn.close()


def test_show_entry(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        entry = create_dummy_entry()

        entry_tuple = tuple(entry.values())

        cursor.execute(
            "INSERT INTO entry (entry_id, summary, action_item, created_at) VALUES (?, ?, ?, ?)",
            entry_tuple,
        )
        conn.commit()

        found_entry = search_entry("123", db_path).model_dump()

        assert found_entry == entry


def test_show_entry_with_no_entry(db_path):
    entry = create_dummy_entry()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        entry_tuple = tuple(entry.values())

        cursor.execute(
            "INSERT INTO entry (entry_id, summary, action_item, created_at) VALUES (?, ?, ?, ?)",
            entry_tuple,
        )
        with pytest.raises(EntryErrorException) as error_info:
            search_entry(entry_id="321", db_path=db_path)

        assert "321 does not exist" in str(error_info.value)
