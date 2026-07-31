from typing import Optional

from models import Phrase

POST_TEMPLATE = """[今日の韓国語 🇰🇷 - {category}]

- 韓国語: {korean}
- 発音: {katakana}
- 意味: {meaning}

💡 {description}

👉 もっと詳しい韓国語学習はこちら！
🔗 {homepage_url}

#韓国語 #韓国語勉強 #韓国旅行 #韓国語講座 #{category_tag}"""


def build_post_text(phrase: Phrase, homepage_url: str) -> str:
    return POST_TEMPLATE.format(
        category=phrase.category,
        korean=phrase.korean,
        katakana=phrase.katakana,
        meaning=phrase.meaning,
        description=phrase.description,
        homepage_url=homepage_url,
        category_tag=phrase.category_tag,
    )


def build_post_text_for_platform(
    phrase: Phrase, homepage_url: str, max_length: Optional[int] = None
) -> str:
    """플랫폼별 글자수 제한(예: X는 280자)에 맞춰 설명(description)을 줄여서 반환한다.

    URL과 해시태그, 필수 정보(한국어/발음/의미)는 항상 유지하고,
    초과분이 있을 때만 💡 설명 문구를 점진적으로 축약한다.
    """
    text = build_post_text(phrase, homepage_url)
    if max_length is None or len(text) <= max_length:
        return text

    description = phrase.description
    while len(text) > max_length and len(description) > 10:
        description = description[: len(description) - 10].rstrip() + "…"
        trimmed = Phrase(**{**phrase.to_dict(), "description": description})
        text = build_post_text(trimmed, homepage_url)
    return text
