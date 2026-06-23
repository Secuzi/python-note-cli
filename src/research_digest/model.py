from pydantic import BaseModel
from datetime import date


class Entry(BaseModel):
    entry_id: str
    summary: str
    action_item: str
    created_at: date


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
