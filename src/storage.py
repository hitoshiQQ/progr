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
