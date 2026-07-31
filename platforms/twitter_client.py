import logging

import tweepy

from .base import SNSPoster

logger = logging.getLogger(__name__)


class TwitterPoster(SNSPoster):
    """X(구 Twitter) API v2 - OAuth1.0a User Context 방식으로 트윗을 작성한다."""

    name = "twitter"
    MAX_LENGTH = 280  # X의 기본 글자수 제한 (근사치, 실제 weighted-length와는 다를 수 있음)

    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

    def post(self, text: str) -> bool:
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data.get("id") if response and response.data else None
            logger.info(f"[Twitter] 投稿成功: tweet_id={tweet_id}")
            return True
        except Exception as e:
            logger.error(f"[Twitter] 投稿失敗: {e}")
            return False
