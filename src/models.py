from dataclasses import dataclass


@dataclass
class Record:
    date: str
    type: str     # "Доход" или "Расход"
    category: str
    amount: float
