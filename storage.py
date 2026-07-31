import json
import logging
import random
from pathlib import Path
from typing import List, Optional

from models import Phrase

logger = logging.getLogger(__name__)


class PhraseStorage:
    """JSON 파일 기반으로 한국어 표현과 게시 상태(is_published)를 관리한다."""

    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self._phrases: List[Phrase] = []
        self._load()

    def _load(self) -> None:
        if not self.data_file.exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {self.data_file}")
        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self._phrases = [Phrase.from_dict(item) for item in raw]

    def save(self) -> None:
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self._phrases], f, ensure_ascii=False, indent=2)

    def pick_random_unpublished(self) -> Optional[Phrase]:
        unpublished = [p for p in self._phrases if not p.is_published]
        if not unpublished:
            return None
        return random.choice(unpublished)

    def mark_published(self, phrase_id: int, published_at: str) -> None:
        for p in self._phrases:
            if p.id == phrase_id:
                p.is_published = True
                p.published_at = published_at
                break

    def reset_all(self) -> None:
        """모든 표현의 게시 상태를 초기화한다. 데이터베이스를 전부 소진했을 때 호출."""
        for p in self._phrases:
            p.is_published = False
            p.published_at = None

    def stats(self) -> dict:
        total = len(self._phrases)
        published = sum(1 for p in self._phrases if p.is_published)
        return {"total": total, "published": published, "remaining": total - published}
