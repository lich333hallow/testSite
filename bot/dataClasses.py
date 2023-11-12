from dataclasses import dataclass


@dataclass
class Question:
    name: str
    corr_ans: str
    other_ans: tuple


@dataclass
class Form:
    id: str
    question: list
    type: str
    time_limit: int | None

# ((name, corr_ans, other_ans), ...)
