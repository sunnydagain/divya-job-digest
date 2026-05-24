from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    description: str
    posted: str
    source: str
    tier: Optional[str] = None
    score: int = 0
    signals: list = field(default_factory=list)
