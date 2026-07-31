from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Phrase:
    id: int
    category: str
    category_tag: str
    korean: str
    katakana: str
    meaning: str
    description: str
    is_published: bool = False
    published_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Phrase":
        return Phrase(**data)
