from dataclasses import dataclass
from typing import Optional


@dataclass
class Record:
    date: str
    type: str     # "Доход" или "Расход"
    category: str
    amount: float


@dataclass
class Goal:
    name: str
    target: float
    saved: float = 0.0
    completed_date: Optional[str] = None
