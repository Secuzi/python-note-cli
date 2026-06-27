from pydantic import BaseModel
from datetime import datetime


class Entry(BaseModel):
    entry_id: str
    summary: str
    action_item: str
    created_at: datetime


class EntryWithTagName(BaseModel):
    entry_id: str
    tag_name: str
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
