# 계획 — 게시 콘텐츠 전면 개편 + LINE 친구추가 링크 (작업 A+B)

> 상태: **승인 대기**. 이 문서가 승인되기 전에는 코드를 커밋하지 않는다.
> 작업지시서 §5(작업 A)·§6(작업 B) 기준. 둘 다 `content.py` 템플릿을 건드리므로 한 계획·한 커밋으로 묶는다.

## 1. 목표

1. 상황별 교과서 표현 45건을 폐기하고, **SNS·젊은층이 실제로 쓰는 표현 + 한/일 뉘앙스 차이**로 재구성한다.
2. 각 표현에 `nuance` 필드를 신설해 「한국어는 이런데 일본어는 이렇다」를 한 줄로 노출한다.
3. 모든 게시물 본문에 **LINE 친구추가 링크**(`https://lin.ee/8Rz047O`)를 상시 노출한다.

게시 골격(`run_once.py` → `job.run_posting_job()` → 미게시 1건 랜덤 → 전 플랫폼 게시 → `is_published` 커밋)은 **유지**한다.

---

## 2. ⚠️ 먼저 결정해야 할 것 — X 글자수

이번 리서치에서 **작업지시서 §3-3의 전제와 다른 사실**이 나왔다. 구현 전에 방침을 정해야 한다.

### 2-1. 실측 (X 공식 `twitter-text` 라이브러리, 45건 전수)

한글·가나·한자 = 2, URL = 23 고정임을 먼저 확인했다(`안녕하세요` → 10, `https://...` → 23).

| 대상 | 최소 | 중앙값 | 최대 | 280 초과 |
|---|---|---|---|---|
| **현행** 템플릿 | 264 | 308 | 355 | **43 / 45** |
| 제안 템플릿 (nuance 실제 예시) | 367 | 412 | 458 | **45 / 45** |
| 제안 템플릿 (nuance 45자 = 권장 상한) | 375 | 419 | 466 | **45 / 45** |
| 제안 템플릿, description·nuance를 **각 10자까지 축약** (= 축약 로직의 바닥값) | 253 | 286 | 319 | **30 / 45** |
| 제안 템플릿에서 description·nuance **통째로 삭제** | 200 | 233 | 266 | 0 / 45 |

고정 골격만으로 현행 164 → 제안 **185**(URL 2개가 46을 차지).

### 2-2. 핵심 — 280은 이미 이 계정의 상한이 아니다

`content.py`는 `len(text) <= 280`으로 비교한다. 일본어·한국어는 `len()`에서 1로 세지므로
**실제보다 약 40% 적게 센다.** 그래서 축약 로직은 사실상 한 번도 발동하지 않는다.

그런데 결정적으로, **2026-08-06에 실제 게시에 성공한 id=40의 weighted length는 298** 이었다.
저장소 코드로 직접 렌더해 대조했고, `twitter-text`는 이 텍스트를 `valid=false`(280 초과)로 판정한다.

> 즉 280을 넘긴 글이 그대로 게시되었다. **이 계정의 실제 상한은 280보다 높다.**

### 2-3. 그래서 DoD §8의 한 항목이 현재 상태로는 성립하지 않는다

작업지시서 §8은 ⑴ 4요소(💡·🇰🇷→🇯🇵·홈페이지·LINE) 모두 출력 ⑵ X(280) 렌더 시 잘리지 않음 —
두 가지를 동시에 요구한다. 그러나 위 표에서 보듯 **description·nuance를 하한(10자)까지 줄여도
30/45가 280을 넘는다.** 280을 하드 캡으로 두는 한 두 조건은 동시에 만족될 수 없다.

### 2-4. 선택지

| 안 | 내용 | 결과 |
|---|---|---|
| **A (권장)** | 280을 하드 캡으로 취급하지 않는다. `MAX_LENGTH`는 안전망으로만 두고 nuance를 온전히 노출 | 지시서 의도대로 구현 가능 |
| B | 280을 지킨다 → 템플릿에서 요소를 뺀다(URL 1개만 / 해시태그 삭제 / 発音 줄 삭제 등) | nuance 도입이 사실상 무산 |
| C | weighted length 계산기 도입 | **§9에서 scope 밖으로 명시됨** — 배제 |

**A를 권장하는 근거**는 298 게시 성공 실측이다. 다만 298이 되고 466도 된다는 보장은 아니다.
X Premium 가입 계정이면 상한이 25,000자라 전부 여유롭지만, 그렇지 않다면 298이 통과한 이유가 설명되지 않는다.

> **결정 요청 ②** A / B 중 무엇으로 갑니까?
> A를 고르실 경우, 구현 전에 **가장 긴 표현 1건을 수동 실행으로 시험 게시**해 실제 상한을 확정하기를 제안합니다
> (실패해도 `is_published`가 안 바뀌어 데이터 손상 없음). 이 시험 게시를 진행해도 되겠습니까?

---

## 3. 스키마 — `nuance` 필드 신설

```python
# models.py
@dataclass
class Phrase:
    id: int
    category: str
    category_tag: str
    korean: str
    katakana: str
    meaning: str
    description: str
    nuance: str            # 신설: 한/일 차이·뉘앙스 포인트(일본어)
    is_published: bool = False
    published_at: Optional[str] = None
```

`to_dict`/`from_dict`는 `asdict`·`**data` 기반이라 자동 반영된다.
**단 `data/phrases.json` 전 항목에 `nuance` 키가 반드시 있어야 한다** — 하나라도 빠지면
`storage.py`의 `Phrase(**item)`에서 `TypeError`로 게시 전체가 죽는다.
데이터를 전면 교체하므로 이 위험은 같은 커밋에서 해소된다.

## 4. 데이터 — `data/phrases.json` 전면 교체

- **48건** (지시서 하한 45건 이상), `id` 1부터 연속, 중복 없음, 전부 `is_published:false`·`published_at:null`.
- 카테고리는 실생활 중심으로 재편. 아래 배분을 제안한다.

| `category` (일본어) | `category_tag` | 건수 |
|---|---|---|
| リアクション | 韓国語リアクション | 8 |
| ツッコミ | 韓国語ツッコミ | 8 |
| 感情表現 | 韓国語感情表現 | 8 |
| カフェ・デリバリー | 韓国語カフェ | 8 |
| 友達との会話（タメ口） | 韓国語タメ口 | 8 |
| SNS・若者言葉 | 韓国語SNS | 8 |

- `korean`: 요즘 실제로 쓰는 자연스러운 표현. **비속어·과한 유행어는 배제**(브랜드 톤 유지).
- `katakana`: 실제 발음에 가깝게(연음·받침 반영).
- `description`(💡): 언제·누구에게 쓰는지 한 줄. 일본어, ~45자.
- `nuance`(🇰🇷→🇯🇵): 같은 상황에서 일본어와 무엇이 다른지 — 뉘앙스·사용 빈도·톤·반말/존댓말 차이 중 **하나**로 압축. 일본어, ~45자.

> **결정 요청 ③** 카테고리 6종·각 8건 배분을 승인하십니까? 조정하실 항목이 있으면 표에 메모해 주십시오.

> **확인 ④** 지시서 §5-3 예시의 `category_tag`는 `韓国語リアクション` 형식인데, 템플릿 해시태그 줄이
> `#韓国語 #リアル韓国語 #{category_tag}`라 `#韓国語`와 `#韓国語リアクション`가 나란히 붙습니다.
> 의도하신 형태가 맞습니까? (현행 데이터는 `挨拶`·`買い物` 같은 짧은 태그입니다.)

## 5. 템플릿 — `content.py`

```python
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
```

해시태그는 지시서 권장대로 5개 → 3개로 줄인다.

**축약 대상 확장** — 현재는 `description`만 줄인다. `nuance`를 뒤이어 줄이도록 확장한다.
필수 정보(한국어/발음/의미/2개 URL/해시태그)는 항상 보존하고, 각 필드는 10자에서 멈춘다(무한 축약 방지, 기존 동작 유지).

```python
def build_post_text_for_platform(
    phrase: Phrase, homepage_url: str, line_add_url: str, max_length: Optional[int] = None
) -> str:
    text = build_post_text(phrase, homepage_url, line_add_url)
    if max_length is None or len(text) <= max_length:
        return text

    fields = {"description": phrase.description, "nuance": phrase.nuance}
    for key in ("description", "nuance"):  # description 을 먼저 줄이고, 그래도 넘치면 nuance
        while len(text) > max_length and len(fields[key]) > 10:
            fields[key] = fields[key][: len(fields[key]) - 10].rstrip() + "…"
            trimmed = Phrase(**{**phrase.to_dict(), **fields})
            text = build_post_text(trimmed, homepage_url, line_add_url)
    return text
```

## 6. LINE 친구추가 URL — `config.py` / `job.py` / `.env.example`

비밀값이 아니므로 기본값을 코드에 두어 **GitHub Secret 등록 없이도 동작**하게 한다(지시서 §6-2).

```python
# config.py
LINE_ADD_URL = os.getenv("LINE_ADD_URL", "https://lin.ee/8Rz047O")
```

```python
# job.py — 렌더 호출에 인자 추가
text = build_post_text_for_platform(
    phrase, config.HOMEPAGE_URL, config.LINE_ADD_URL, poster.MAX_LENGTH
)
```

```bash
# .env.example (선택 항목으로 문서화)
# LINE 친구추가 링크 (게시물 본문에 노출. 미설정 시 코드 기본값 사용)
LINE_ADD_URL=https://lin.ee/8Rz047O
```

**주의(지시서 §3-2 재확인):** 이 링크는 게시물 본문에 들어가는 텍스트일 뿐이며,
`ENABLE_LINE`/`LINE_CHANNEL_ACCESS_TOKEN`(LINE 브로드캐스트 발송)과 **완전히 별개**다.
`ENABLE_LINE` 플래그와 무관하게 **모든 플랫폼의 모든 게시물**에 항상 렌더된다.

## 7. 수정 파일

| 경로 | 변경 |
|---|---|
| `models.py` | `nuance` 필드 1개 추가 |
| `data/phrases.json` | 전면 교체 (48건) |
| `content.py` | 템플릿 + 두 함수 시그니처 + 축약 대상 확장 |
| `config.py` | `LINE_ADD_URL` 추가 |
| `job.py` | 렌더 호출 인자 1개 추가 |
| `.env.example` | `LINE_ADD_URL` 문서화 |
| `README.md` | §6 스키마 예시에 `nuance` 반영 |

`platforms/*` · `storage.py` · `run_once.py` · `autoposting.py` · 워크플로는 **무변경**.

## 8. 트레이드오프

- **`build_post_text*` 시그니처가 바뀐다.** 위치 인자 하나가 늘어 기존 호출부(`job.py` 1곳)를 함께 고쳐야 한다.
  `line_add_url`을 키워드 기본값으로 두면 호환은 지키지만, 렌더에 항상 필요한 값이라 명시 인자가 낫다고 판단했다.
- **데이터 45건을 전부 버린다.** 기존 표현은 여행/식당 등 실용 상황이라 그 자체로 나쁘지 않다.
  되돌리려면 `git revert` 한 번이면 되므로 복구 비용은 낮다.
- **축약 로직은 여전히 `len()` 기준이다.** 실제 X 기준과 어긋나지만, weighted length 계산기 도입이
  §9에서 scope 밖이라 이번엔 손대지 않는다. §2의 결정에 따라 이 괴리를 감수할지 정해진다.
- **`nuance` 45자 권장은 지킬수록 좋지만 강제 수단이 없다.** 데이터 작성 시 수동으로 지킨다.

## 9. Scope 밖 (지시서 §9)

스케줄러 · `is_published`/`reset_all` 로직 · `platforms/*` 인터페이스 · X weighted-length 계산기 ·
새 SNS 플랫폼 추가 · GitHub Actions 크론/권한 구조 · 이미지/미디어 게시.

## 10. 완료 조건 (지시서 §8)

- [ ] `data/phrases.json` 전 항목이 `Phrase` 스키마와 일치(누락 키 0). 스키마 검증 **PASS**
- [ ] 48건, `id` 연속·중복 없음, 전부 `is_published:false`
- [ ] 렌더 결과에 💡 / 🇰🇷→🇯🇵 / 🔗 홈페이지 / 📱 LINE **4요소 모두** 출력
- [ ] 가장 긴 표현 렌더 시 필수 정보·2개 URL·해시태그 보존 (※ 280 기준 적용 여부는 §2 결정에 따름)
- [ ] `LINE_ADD_URL` 미설정 환경에서 기본값으로 정상 렌더
- [ ] README §6 스키마 예시에 `nuance` 반영
- [ ] `python run_once.py`가 예외 없이 완주
