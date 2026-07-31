import logging
from typing import List

from .base import SNSPoster
from .line_client import LinePoster
from .threads_client import ThreadsPoster
from .twitter_client import TwitterPoster

logger = logging.getLogger(__name__)


def get_enabled_posters(settings) -> List[SNSPoster]:
    """.env 설정을 기반으로 활성화된 SNS 플랫폼 클라이언트 목록을 생성한다."""
    posters: List[SNSPoster] = []

    if settings.ENABLE_TWITTER:
        if all(
            [
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET,
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET,
            ]
        ):
            posters.append(
                TwitterPoster(
                    settings.TWITTER_API_KEY,
                    settings.TWITTER_API_SECRET,
                    settings.TWITTER_ACCESS_TOKEN,
                    settings.TWITTER_ACCESS_TOKEN_SECRET,
                )
            )
        else:
            logger.warning("X(Twitter)가 활성화되어 있지만 인증 정보가 부족합니다. 건너뜁니다.")

    if settings.ENABLE_THREADS:
        if settings.THREADS_USER_ID and settings.THREADS_ACCESS_TOKEN:
            posters.append(ThreadsPoster(settings.THREADS_USER_ID, settings.THREADS_ACCESS_TOKEN))
        else:
            logger.warning("Threads가 활성화되어 있지만 인증 정보가 부족합니다. 건너뜁니다.")

    if settings.ENABLE_LINE:
        if settings.LINE_CHANNEL_ACCESS_TOKEN:
            posters.append(LinePoster(settings.LINE_CHANNEL_ACCESS_TOKEN))
        else:
            logger.warning("LINE이 활성화되어 있지만 인증 정보가 부족합니다. 건너뜁니다.")

    return posters
