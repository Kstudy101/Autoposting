import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

import config
from job import run_posting_job


def setup_logging() -> None:
    log_path = Path(config.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=== 韓国語学習SNS自動投稿ボット 起動 ===")

    scheduler = BlockingScheduler(timezone="Asia/Tokyo")
    scheduler.add_job(
        run_posting_job,
        trigger=IntervalTrigger(hours=config.POST_INTERVAL_HOURS),
        id="hourly_korean_post",
        misfire_grace_time=300,
    )

    # 시작하자마자 1회 즉시 실행 (그 다음부터 지정된 간격으로 반복)
    try:
        run_posting_job()
    except Exception as e:
        logger.error(f"初回実行でエラーが発生しました: {e}")

    logger.info(f"{config.POST_INTERVAL_HOURS}時間ごとの自動投稿を開始します。(Ctrl+Cで終了)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("スケジューラーを終了します。")


if __name__ == "__main__":
    main()
