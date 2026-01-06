import json
import os
from models import Goal

GOALS_FILE = "goals.json"


def load_goals():
    if not os.path.exists(GOALS_FILE):
        return []
    with open(GOALS_FILE, "r", encoding="utf-8") as f:
        return [Goal(**g) for g in json.load(f)]


def save_goals(goals):
    with open(GOALS_FILE, "w", encoding="utf-8") as f:
        json.dump([g.__dict__ for g in goals], f, ensure_ascii=False, indent=2)
