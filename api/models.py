"""
data models
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tournament:
    id: int
    created: datetime
    start: datetime
    size: int
    seed: int
