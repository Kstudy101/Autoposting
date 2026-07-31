"""GitHub Actions 등 스케줄러가 프로세스를 계속 띄워두지 않는 환경을 위한 단발 실행 스크립트.

crontab, GitHub Actions schedule, 클라우드 스케줄러(Cloud Scheduler) 등에서
`python run_once.py` 형태로 1회 실행하도록 호출하면 된다.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

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


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=== 1回分の投稿ジョブを実行 (run_once) ===")
    success = run_posting_job()
    sys.exit(0 if success else 1)
