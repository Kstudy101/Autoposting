from typing import Optional

from models import Phrase

POST_TEMPLATE = """[今日の韓国語 🇰🇷 - {category}]

- 韓国語: {korean}
- 発音: {katakana}
- 意味: {meaning}

💡 {description}
🇰🇷→🇯🇵 {nuance}

👉 もっと詳しくはこちら
🔗 {homepage_url}
📱 LINE友だち追加 → {line_add_url}

#韓国語 #リアル韓国語 #{category_tag}"""


def build_post_text(phrase: Phrase, homepage_url: str, line_add_url: str) -> str:
    return POST_TEMPLATE.format(
        category=phrase.category,
        korean=phrase.korean,
        katakana=phrase.katakana,
        meaning=phrase.meaning,
        description=phrase.description,
        nuance=phrase.nuance,
        homepage_url=homepage_url,
        line_add_url=line_add_url,
        category_tag=phrase.category_tag,
    )


def build_post_text_for_platform(
    phrase: Phrase, homepage_url: str, line_add_url: str, max_length: Optional[int] = None
) -> str:
    """플랫폼별 글자수 제한에 맞춰 설명(description)과 뉘앙스(nuance)를 줄여서 반환한다.

    2개 URL과 해시태그, 필수 정보(한국어/발음/의미)는 항상 유지하고,
    초과분이 있을 때만 💡 설명을 먼저, 그래도 넘치면 🇰🇷→🇯🇵 뉘앙스를 점진적으로 축약한다.

    주의: max_length 비교는 len() 기준이라 X의 weighted length(한글·가나 2배, URL 23 고정)와
    다르다. 하드 캡이 아니라 안전망으로 둔 값이다 — CLAUDE.md의 «조심할 것» 참고.
    """
    text = build_post_text(phrase, homepage_url, line_add_url)
    if max_length is None or len(text) <= max_length:
        return text

    fields = {"description": phrase.description, "nuance": phrase.nuance}
    for key in ("description", "nuance"):
        while len(text) > max_length and len(fields[key]) > 10:
            fields[key] = fields[key][: len(fields[key]) - 10].rstrip() + "…"
            trimmed = Phrase(**{**phrase.to_dict(), **fields})
            text = build_post_text(trimmed, homepage_url, line_add_url)
    return text
