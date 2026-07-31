import logging

import requests

from .base import SNSPoster

logger = logging.getLogger(__name__)


class LinePoster(SNSPoster):
    """LINE Messaging API로 공식 계정의 친구 전체에게 브로드캐스트 메시지를 보낸다.

    LINE은 타임라인형 SNS가 아니라 메시징 채널이므로 확장/선택 기능으로 제공한다.
    """

    name = "line"
    MAX_LENGTH = 5000  # LINE 텍스트 메시지 글자수 제한

    def __init__(self, channel_access_token: str):
        self.channel_access_token = channel_access_token

    def post(self, text: str) -> bool:
        try:
            url = "https://api.line.me/v2/bot/message/broadcast"
            headers = {
                "Authorization": f"Bearer {self.channel_access_token}",
                "Content-Type": "application/json",
            }
            payload = {"messages": [{"type": "text", "text": text}]}
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            logger.info("[LINE] 配信成功")
            return True
        except Exception as e:
            logger.error(f"[LINE] 配信失敗: {e}")
            return False
