# 韓国語 SNS 自動投稿ボット

일본인을 대상으로 하루 2회 상황별 유용한 한국어 표현(한국어 문장 + カタカナ 발음 + 일본어 뜻 + 사용 설명)을
중복 없이 랜덤으로 SNS(X, Threads, LINE)에 자동 포스팅하면서 홈페이지 링크도 함께 홍보하는 프로그램입니다.

## 1. 프로젝트 구조

```
클로드/
├── autoposting.py          # 로컬/서버에서 계속 실행하는 스케줄러 (APScheduler, 18:37 / 21:37 JST)
├── run_once.py              # 1회만 실행하는 스크립트 (GitHub Actions 등 stateless 환경용)
├── job.py                   # 표현 선택 → 포스팅 → 게시 상태 저장까지의 핵심 로직
├── models.py                # Phrase 데이터 모델
├── storage.py                # JSON 기반 저장소 (중복 게시 방지)
├── content.py                # 포스트 템플릿 렌더링 + 플랫폼별 글자수 제한 처리
├── config.py                 # .env 값 로딩
├── platforms/                 # SNS 플랫폼별 클라이언트 (모듈화 구조)
│   ├── base.py                # 공통 인터페이스 (SNSPoster)
│   ├── twitter_client.py       # X(Twitter) API v2
│   ├── threads_client.py       # Threads API (Meta Graph API)
│   └── line_client.py          # LINE Messaging API (확장/선택)
├── data/
│   └── phrases.json            # 한국어 표현 데이터베이스 (is_published로 중복 방지)
├── logs/                        # 실행 로그 (자동 생성)
├── .github/workflows/hourly_post.yml  # GitHub Actions 무료 스케줄링
├── .env.example                  # 환경변수 템플릿
├── requirements.txt
└── .gitignore
```

새 플랫폼(Instagram 등)을 추가하고 싶다면 `platforms/base.py`의 `SNSPoster`를 상속받아
`post(text) -> bool` 메서드만 구현하고 `platforms/__init__.py`의 `get_enabled_posters()`에 등록하면 됩니다.

## 2. 설치

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

`.env.example`을 복사해 `.env` 파일을 만들고 값을 채워 넣으세요.

```bash
copy .env.example .env
```

`.env`는 `.gitignore`에 포함되어 있어 git에 커밋되지 않습니다. **API 키/토큰은 절대 코드에 직접 쓰지 말고 항상 .env를 통해서만 관리하세요.**

## 3. SNS 플랫폼 연동 준비

### X (Twitter) API v2
1. https://developer.twitter.com 에서 개발자 계정 및 앱 생성
2. 앱 권한을 **Read and Write**로 설정 (트윗 작성에 필요)
3. Consumer Key/Secret, Access Token/Secret 발급 → `.env`의 `TWITTER_*` 값에 입력
4. 본문에 URL을 넣지 않는다. URL 포함 게시는 일반 게시보다 약 13배 과금된다. 하루 2회면 월 약 60건이다.

### Threads API
1. https://developers.facebook.com/docs/threads 문서를 참고해 Meta 개발자 앱을 생성
2. 앱에 Threads API 사용 사례를 추가하고 본인 계정으로 로그인/권한 승인
3. 장기(long-lived) 액세스 토큰과 Threads 사용자 ID를 발급받아 `.env`의 `THREADS_*` 값에 입력
4. `ENABLE_THREADS=true`로 변경

### LINE Messaging API (확장, 선택사항)
1. https://developers.line.biz 에서 Messaging API 채널 생성
2. Channel Access Token 발급 → `.env`의 `LINE_CHANNEL_ACCESS_TOKEN`에 입력
3. `ENABLE_LINE=true`로 변경 (공식 계정 친구 전체에게 브로드캐스트로 전송됩니다)

## 4. 로컬/서버에서 실행 (계속 켜두는 방식)

```bash
python autoposting.py
```

실행 즉시 포스팅하지 않고, 매일 18:37 / 21:37 JST에만 게시합니다.
Ctrl+C로 종료할 수 있습니다. 로그는 콘솔과 `logs/app.log`에 함께 기록되며, 포스팅 실패 시에도
에러만 로그로 남기고 다음 회차로 넘어갑니다 (다음 실행 시 같은 표현이 다시 선택되어 재시도됨).

VPS 등에서 재부팅 후에도 계속 실행되게 하려면 systemd 서비스나 `pm2`, `nssm`(Windows) 등으로
데몬화하는 것을 추천합니다.

## 5. 24시간 무료/저비용 실행 — GitHub Actions (추천)

서버를 따로 띄우지 않고 **GitHub Actions의 스케줄 트리거**로 하루 2회 `run_once.py`를 실행하는 방식입니다.

1. 이 프로젝트를 GitHub 저장소에 push
2. 저장소 **Settings → Secrets and variables → Actions**에서 아래 값을 등록:
   - `HOMEPAGE_URL`, `ENABLE_TWITTER`, `ENABLE_THREADS`, `ENABLE_LINE`
   - `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`
   - (사용 시) `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN`, `LINE_CHANNEL_ACCESS_TOKEN`
3. `.github/workflows/hourly_post.yml`이 하루 2회(cron `37 9,12 * * *` = 18:37 / 21:37 JST) 자동 실행됩니다.
4. 실행 후 `data/phrases.json`의 게시 상태 변경분을 워크플로우가 자동으로 커밋/푸시하여
   다음 실행에서도 중복 게시 없이 이어집니다.

**장점**: Public 저장소는 Actions 실행 시간이 사실상 무료이고, 서버 관리가 전혀 필요 없습니다.
**주의**: GitHub Actions의 cron은 부하 상황에 따라 실제 실행이 정각보다 몇 분 늦어질 수 있습니다(엄밀한 정시 보장은 아님). Actions 탭에서 `workflow_dispatch`로 수동 실행/테스트도 가능합니다.

### 다른 무료/저비용 대안
- **Railway / Render Cron Jobs**: 계정 생성 후 `python run_once.py`를 cron 스케줄로 등록 (일부 무료 크레딧 제공)
- **자체 VPS + cron/systemd timer**: 저렴한 VPS 한 대에서 `run_once.py`를 crontab(`0 * * * *`)으로 등록
- **소규모 클라우드 함수 + 스케줄러**: AWS Lambda + EventBridge, GCP Cloud Functions + Cloud Scheduler 등

## 6. 중복 방지 / 데이터 소진 시 동작

`data/phrases.json`의 각 표현은 `is_published` 필드로 게시 여부를 관리합니다.
모든 표현이 소진되면(`remaining == 0`) 자동으로 전체를 초기화(`reset_all`)하고 처음부터 다시 순환합니다.
새로운 표현을 추가하고 싶다면 `data/phrases.json`에 다음 형식으로 항목을 추가하세요.

```json
{
  "id": 46,
  "category": "카테고리(일본어)",
  "category_tag": "해시태그용 짧은 태그",
  "korean": "한국어 문장",
  "katakana": "カタカナ 발음",
  "meaning": "일본어 뜻",
  "description": "일본어로 된 간단한 사용 상황 설명",
  "nuance": "일본어로 된 한/일 뉘앙스 차이 한 줄",
  "is_published": false,
  "published_at": null
}
```

## 7. 문제 해결

- **X 포스팅 실패**: 앱 권한이 Read/Write인지, 액세스 토큰이 앱 권한 변경 후 재발급된 것인지 확인
- **Threads 포스팅 실패**: 액세스 토큰 만료 여부, `THREADS_USER_ID`가 Threads용 사용자 ID인지 확인
- **길이 초과 에러**: `content.py`의 `build_post_text_for_platform()`이 플랫폼별 `MAX_LENGTH`에 맞춰
  설명(💡) 부분을 자동으로 줄여준다. X 본문에는 URL을 넣지 않는다(URL 포함 게시 과금 회피).
- **GitHub Actions에서 커밋 실패**: 저장소 Settings → Actions → General → Workflow permissions를
  "Read and write permissions"로 설정해야 `git push`가 가능합니다.
