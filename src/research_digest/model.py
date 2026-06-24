from pydantic import BaseModel
from datetime import datetime


class Entry(BaseModel):
    entry_id: str
    summary: str
    action_item: str
    created_at: datetime


class Tag(BaseModel):
    tag_id: str
    name: str


class EntryTag(BaseModel):
    entry_id: str
    tag_id: str


class EntryCreate(BaseModel):
    summary: str
    tags: list[str]
    action_item: str


def imagine():
    tuples = [("asd", "skribnit"), ("skid", "powerpoint")]

    for name in tuples:
        print(name[0])

    sets = {name[1] for tupe in tuples}

    print(sets)


imagine()
