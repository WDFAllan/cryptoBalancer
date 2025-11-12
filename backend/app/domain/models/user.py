from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int | None
    email: str
    username: str