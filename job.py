import logging
from datetime import datetime, timezone

import config
from content import build_post_text_for_platform
from platforms import get_enabled_posters
from storage import PhraseStorage

logger = logging.getLogger(__name__)


def run_posting_job() -> bool:
    """미게시 표현 하나를 랜덤 선택하여 활성화된 모든 SNS 플랫폼에 게시하고,
    한 곳이라도 성공하면 게시 완료로 표시한다."""
    storage = PhraseStorage(config.DATA_FILE)

    stats = storage.stats()
    logger.info(
        f"表現データベース状況: 総数={stats['total']} 済={stats['published']} 残り={stats['remaining']}"
    )

    if stats["remaining"] == 0:
        logger.warning("すべての表現を投稿済みです。is_publishedをリセットして最初から再開します。")
        storage.reset_all()
        storage.save()

    phrase = storage.pick_random_unpublished()
    if phrase is None:
        logger.error("投稿可能な表現がありません。データベースを確認してください。")
        return False

    logger.info(f"選択された表現: id={phrase.id} category={phrase.category} korean={phrase.korean}")

    posters = get_enabled_posters(config)
    if not posters:
        logger.error(
            "有効なSNSプラットフォームがありません。.envのENABLE_*設定と認証情報を確認してください。"
        )
        return False

    any_success = False
    for poster in posters:
        try:
            text = build_post_text_for_platform(
                phrase, config.HOMEPAGE_URL, config.LINE_ADD_URL, poster.MAX_LENGTH
            )
            success = poster.post(text)
            any_success = any_success or success
        except Exception as e:
            logger.error(f"[{poster.name}] 予期しないエラー: {e}")

    if any_success:
        storage.mark_published(phrase.id, datetime.now(timezone.utc).isoformat())
        storage.save()
        logger.info(f"id={phrase.id} を投稿済みとしてマークしました。")
    else:
        logger.error(f"id={phrase.id} はすべてのプラットフォームで投稿に失敗しました。次回再試行します。")

    return any_success
