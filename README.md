# ⚔️ Review Slayer

> 귀멸의 칼날 주(柱) 기반 AI 코드 리뷰 봇 — CrewAI 멀티 에이전트

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![CrewAI](https://img.shields.io/badge/CrewAI-latest-purple.svg)](https://crewai.com)

**[🇺🇸 English](./README.en.md)**

---

## 개요

Review Slayer는 **귀멸의 칼날**의 9명의 주(柱)를 AI 코드 리뷰 에이전트로 구현한 봇입니다.

각 주는 **고유한 리뷰 역할**과 **성격/말투**를 가지고 있으며, PR이 올라오면 선택된 주들이 각자의 관점에서 코드를 리뷰하고, 당주(産屋敷)가 최종 결과를 종합하여 PR 코멘트로 게시합니다.

### 주(柱) 리뷰어

각 리뷰 역할마다 **주역(🥇)**과 **차역(🥈)** 중 선택할 수 있습니다.

| 리뷰 역할 | 🥇 주역 | 🥈 차역 |
|:---------|:--------|:--------|
| 🔒 **Security** — 보안 취약점 | 🦋 코쵸 시노부 | 🐍 이구로 오바나이 |
| ⚡ **Performance** — 성능/복잡도 | 🌫️ 토키토 무이치로 | 💧 토미오카 기유 |
| ✨ **Code Quality** — 클린코드/SOLID | 🐍 이구로 오바나이 | 🦋 코쵸 시노부 |
| 🏛️ **Architecture** — 설계/구조 | 🪨 히메지마 교메이 | 🎵 우즈이 텐겐 |
| 🐛 **Bug Detection** — 버그 탐지 | 🔥 렌고쿠 쿄쥬로 | 💨 시나즈가와 사네미 |
| 🌊 **Logic & Flow** — 논리 흐름 | 💧 토미오카 기유 | 🌫️ 토키토 무이치로 |
| ⚔️ **Edge Cases** — 경계값/예외 | 💨 시나즈가와 사네미 | 🔥 렌고쿠 쿄쥬로 |
| 📖 **Readability** — 가독성/문서화 | 💕 카나로지 미츠리 | 🪨 히메지마 교메이 |
| 🎨 **Style** — 코드 스타일/컨벤션 | 🎵 우즈이 텐겐 | 💕 카나로지 미츠리 |

### 리뷰 예시

> 🔥 **렌고쿠 쿄쥬로 (Bug Detection)**: "우마이! 이 함수 구조는 훌륭하다! 하지만 여기! null 체크가 빠졌다! 마음을 불태워서 고쳐라! 🔥"
>
> 💨 **시나즈가와 사네미 (Edge Cases)**: "야!! 여기 timeout 안 걸어놨잖아!? 서버 죽으면 어쩔 건데!! 당장 30초 timeout 넣어! 💨"
>
> 💕 **카나로지 미츠리 (Readability)**: "이 변수명 정말 직관적이에요! 너무 좋아요~💕 근데 이 함수에 JSDoc 주석을 달면 더 완벽할 것 같아요!"

---

## 아키텍처

```
GitHub PR → Webhook → FastAPI → CrewAI Engine → GitHub Comment
                                     │
                          ┌──────────┼──────────┐
                          │          │          │
                       🦋 보안    ⚡ 성능    🐍 품질   ...
                          │          │          │
                          └──────────┼──────────┘
                                     │
                              📋 당주(産屋敷) 종합
                                     │
                               PR Comment ⚔️
```

---

## 빠른 시작

### 사전 요구사항

- Python 3.12+
- OpenAI API key
- GitHub App ([설정 가이드](#github-app-설정) 참고)

### 로컬 개발

```bash
# 1. 클론 & 설치
git clone https://github.com/your-org/review-slayer.git
cd review-slayer
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 2. 환경 설정
cp .env.example .env
# .env 파일에 API 키 및 GitHub App 설정 입력

# 3. 서버 실행
uvicorn app.main:app --reload --port 8000

# 4. API 문서 확인
open http://localhost:8000/docs
```

### Docker

```bash
docker compose up --build

# 또는 수동 빌드
docker build -t review-slayer .
docker run -p 8000:8000 --env-file .env review-slayer
```

---

## 주(柱) 선택 설정

레포 루트에 `.review-slayer.yml` 파일을 추가하면 리뷰 팀을 커스텀할 수 있습니다:

```yaml
# .review-slayer.yml
reviewers:
  security: shinobu        # 🦋 기본값 (obanai로 변경 가능)
  performance: muichiro    # 🌫️ 기본값 (giyu로 변경 가능)
  code_quality: obanai     # 🐍 기본값
  architecture: gyomei     # 🪨 기본값
  bug_detection: sanemi    # 렌고쿠 대신 사네미로 변경!
```

> **설정 파일이 없으면?** 핵심 5개 역할(Security, Performance, Code Quality, Architecture, Bug Detection)이 주역 캐릭터로 자동 실행됩니다.

---

## GitHub App 설정

1. **GitHub Settings → Developer Settings → GitHub Apps → New GitHub App**
2. 설정:
   - **App name**: `review-slayer`
   - **Webhook URL**: `https://your-server.com/webhook`
   - **Webhook secret**: 랜덤 문자열 생성 → `GITHUB_WEBHOOK_SECRET`
3. **권한(Permissions)**:
   - Pull requests: **Read & Write**
   - Issues: **Read & Write**
   - Contents: **Read**
4. **이벤트 구독**: Pull request, Issue comment
5. **Private key** 생성 (.pem) → `private-key.pem`으로 저장
6. **App ID** 확인 → `GITHUB_APP_ID`

---

## 환경변수

| 변수 | 설명 | 필수 |
|:----|:----|:---:|
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ |
| `GITHUB_APP_ID` | GitHub App ID | ✅ |
| `GITHUB_PRIVATE_KEY_PATH` | .pem 파일 경로 | ✅ |
| `GITHUB_WEBHOOK_SECRET` | Webhook HMAC 시크릿 | ✅ |
| `ENVIRONMENT` | `development` / `production` | |
| `LOG_LEVEL` | 로깅 레벨 | |

---

## 프로젝트 구조

```
review-slayer/
├── app/
│   ├── main.py              # FastAPI 엔트리포인트
│   ├── config.py            # 환경변수 설정 (Pydantic Settings)
│   ├── webhook/
│   │   ├── handler.py       # Webhook 엔드포인트 + 서명 검증
│   │   └── events.py        # PR 이벤트 핸들러
│   ├── github/
│   │   ├── client.py        # GitHub App 인증 + REST API
│   │   ├── diff.py          # Unified diff 파서
│   │   └── comment.py       # 주(柱) 테마 코멘트 포맷터
│   └── crew/
│       ├── characters.py    # 9 주(柱) 캐릭터 정의
│       ├── roles.py         # 9 리뷰 역할 정의
│       ├── config.py        # .review-slayer.yml 설정 파서
│       ├── agents.py        # 캐릭터 × 역할 → CrewAI Agent
│       ├── tasks.py         # 리뷰 + 교차검증 태스크
│       ├── tools.py         # 커스텀 CrewAI 도구
│       └── crew.py          # 크루 조립 + 실행
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## 로드맵

- [x] **Phase 1**: Foundation MVP — 9주 에이전트 리뷰
- [ ] **Phase 2**: RAG + Knowledge — 프로젝트별 컨텍스트 학습
- [ ] **Phase 3**: `@review-slayer` 실시간 대화
- [ ] **Phase 4**: 웹 대시보드 + SaaS

---

## 라이선스

MIT
