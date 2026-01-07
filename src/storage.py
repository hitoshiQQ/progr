import json
import os
from models import Record


DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
        return [Record(**r) for r in raw]


def save_data(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [r.__dict__ for r in records], f,
            ensure_ascii=False, indent=2)


ARCHIVE_FILE = "goals_archive.json"


def load_archived_goals():
    if not os.path.exists(ARCHIVE_FILE):
        return []
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        return [Goal(**g) for g in json.load(f)]


def save_archived_goals(goals):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump([g.__dict__ for g in goals], f, ensure_ascii=False, indent=2)
