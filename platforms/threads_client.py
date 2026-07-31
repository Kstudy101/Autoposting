import logging
import time

import requests

from .base import SNSPoster

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.threads.net/v1.0"


class ThreadsPoster(SNSPoster):
    """Meta Threads API - 컨테이너 생성 후 발행하는 2단계 방식으로 글을 게시한다."""

    name = "threads"
    MAX_LENGTH = 500  # Threads 텍스트 게시물 글자수 제한

    def __init__(self, user_id: str, access_token: str):
        self.user_id = user_id
        self.access_token = access_token

    def post(self, text: str) -> bool:
        try:
            container_id = self._create_container(text)
            if not container_id:
                logger.error("[Threads] コンテナ作成に失敗しました。")
                return False

            time.sleep(3)  # Threads API 권장 대기 시간 (컨테이너 처리 시간 확보)

            post_id = self._publish_container(container_id)
            if post_id:
                logger.info(f"[Threads] 投稿成功: post_id={post_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"[Threads] 投稿失敗: {e}")
            return False

    def _create_container(self, text: str):
        url = f"{GRAPH_API_BASE}/{self.user_id}/threads"
        params = {
            "media_type": "TEXT",
            "text": text,
            "access_token": self.access_token,
        }
        resp = requests.post(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("id")

    def _publish_container(self, container_id: str):
        url = f"{GRAPH_API_BASE}/{self.user_id}/threads_publish"
        params = {
            "creation_id": container_id,
            "access_token": self.access_token,
        }
        resp = requests.post(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("id")
