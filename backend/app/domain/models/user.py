from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    email: str
    username: str
    createdAt: datetime | None
    favorite_platform: str | None = None