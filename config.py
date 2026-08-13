import os

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None or val.strip() == "":
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# 공통 설정
HOMEPAGE_URL = os.getenv("HOMEPAGE_URL", "https://example.com")
# LINE 친구추가 링크. 비밀값이 아니므로 기본값을 코드에 두어 Secret 등록 없이도 동작한다.
LINE_ADD_URL = os.getenv("LINE_ADD_URL", "https://lin.ee/8Rz047O")
DATA_FILE = os.getenv("DATA_FILE", "data/phrases.json")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", "12"))

# 플랫폼 on/off
ENABLE_TWITTER = _get_bool("ENABLE_TWITTER", True)
ENABLE_THREADS = _get_bool("ENABLE_THREADS", False)
ENABLE_LINE = _get_bool("ENABLE_LINE", False)

# X (Twitter) API v2 - OAuth1.0a User Context
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# Threads API (Meta Graph API)
THREADS_USER_ID = os.getenv("THREADS_USER_ID", "")
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "")

# LINE Messaging API (확장용)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
