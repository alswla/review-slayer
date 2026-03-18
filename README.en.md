# ⚔️ Review Slayer

> Demon Slayer (Kimetsu no Yaiba) Hashira-powered AI Code Review Bot — CrewAI Multi-Agent

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![CrewAI](https://img.shields.io/badge/CrewAI-latest-purple.svg)](https://crewai.com)

**[🇰🇷 한국어](./README.md)**

---

## Overview

Review Slayer brings the 9 Hashira (Pillars) from **Demon Slayer (Kimetsu no Yaiba)** to life as AI code review agents.

Each Hashira has a **unique review domain** and **character personality**. When a PR is opened, the selected Hashira review the code from their respective perspectives, and the Oyakata-sama (Master) synthesizes the final consolidated report as a PR comment.

### Hashira Reviewers

Each review role has a **primary (🥇)** and **secondary (🥈)** Hashira option:

| Review Role | 🥇 Primary | 🥈 Secondary |
|:-----------|:-----------|:-------------|
| 🔒 **Security** — Vulnerabilities | 🦋 Kocho Shinobu | 🐍 Iguro Obanai |
| ⚡ **Performance** — Complexity | 🌫️ Tokito Muichiro | 💧 Tomioka Giyu |
| ✨ **Code Quality** — Clean Code | 🐍 Iguro Obanai | 🦋 Kocho Shinobu |
| 🏛️ **Architecture** — Design | 🪨 Himejima Gyomei | 🎵 Uzui Tengen |
| 🐛 **Bug Detection** — Bug Hunting | 🔥 Rengoku Kyojuro | 💨 Shinazugawa Sanemi |
| 🌊 **Logic & Flow** — Control Flow | 💧 Tomioka Giyu | 🌫️ Tokito Muichiro |
| ⚔️ **Edge Cases** — Boundary Values | 💨 Shinazugawa Sanemi | 🔥 Rengoku Kyojuro |
| 📖 **Readability** — Documentation | 💕 Kanroji Mitsuri | 🪨 Himejima Gyomei |
| 🎨 **Style** — Code Convention | 🎵 Uzui Tengen | 💕 Kanroji Mitsuri |

### Review Examples

> 🔥 **Rengoku (Bug Detection)**: "UMAI! This function structure is splendid! But look here! A null check is missing! Set your heart ablaze and fix it! 🔥"
>
> 💨 **Sanemi (Edge Cases)**: "Hey!! No timeout set here!? What happens when the server dies!! Add a 30s timeout NOW! 💨"
>
> 💕 **Mitsuri (Readability)**: "This variable name is so intuitive! I love it~ 💕 But adding a JSDoc comment would make it absolutely perfect!"

---

## Architecture

```
GitHub PR → Webhook → FastAPI → CrewAI Engine → GitHub Comment
                                     │
                          ┌──────────┼──────────┐
                          │          │          │
                       🦋 Security ⚡ Perf   🐍 Quality  ...
                          │          │          │
                          └──────────┼──────────┘
                                     │
                            📋 Oyakata-sama Synthesis
                                     │
                               PR Comment ⚔️
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- GitHub App (see [GitHub App Setup](#github-app-setup))

### Local Development

```bash
# 1. Clone & install
git clone https://github.com/your-org/review-slayer.git
cd review-slayer
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and GitHub App config

# 3. Run the server
uvicorn app.main:app --reload --port 8000

# 4. Visit the API docs
open http://localhost:8000/docs
```

### Docker

```bash
docker compose up --build

# Or manually
docker build -t review-slayer .
docker run -p 8000:8000 --env-file .env review-slayer
```

---

## Hashira Selection (`.review-slayer.yml`)

Add a `.review-slayer.yml` file to your repo root to customize your review team:

```yaml
# .review-slayer.yml
reviewers:
  security: shinobu        # 🦋 default (can switch to obanai)
  performance: muichiro    # 🌫️ default (can switch to giyu)
  code_quality: obanai     # 🐍 default
  architecture: gyomei     # 🪨 default
  bug_detection: sanemi    # override: sanemi instead of rengoku!
```

> **No config file?** The 5 core roles (Security, Performance, Code Quality, Architecture, Bug Detection) run automatically with their primary Hashira.

---

## GitHub App Setup

1. **GitHub Settings → Developer Settings → GitHub Apps → New GitHub App**
2. Configure:
   - **App name**: `review-slayer`
   - **Webhook URL**: `https://your-server.com/webhook`
   - **Webhook secret**: generate a random string → `GITHUB_WEBHOOK_SECRET`
3. **Permissions**: Pull requests (R/W), Issues (R/W), Contents (Read)
4. **Events**: Pull request, Issue comment
5. Generate **private key** (.pem) → save as `private-key.pem`
6. Note **App ID** → `GITHUB_APP_ID`

---

## Environment Variables

| Variable | Description | Required |
|:---------|:-----------|:-------:|
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `GITHUB_APP_ID` | GitHub App ID | ✅ |
| `GITHUB_PRIVATE_KEY_PATH` | Path to .pem file | ✅ |
| `GITHUB_WEBHOOK_SECRET` | Webhook HMAC secret | ✅ |
| `ENVIRONMENT` | `development` / `production` | |
| `LOG_LEVEL` | Logging level | |

---

## Project Structure

```
review-slayer/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Env config (Pydantic Settings)
│   ├── webhook/
│   │   ├── handler.py       # Webhook endpoint + signature verification
│   │   └── events.py        # PR event handler
│   ├── github/
│   │   ├── client.py        # GitHub App auth + REST API
│   │   ├── diff.py          # Unified diff parser
│   │   └── comment.py       # Hashira-themed comment formatter
│   └── crew/
│       ├── characters.py    # 9 Hashira character definitions
│       ├── roles.py         # 9 review role definitions
│       ├── config.py        # .review-slayer.yml config parser
│       ├── agents.py        # Character × Role → CrewAI Agent
│       ├── tasks.py         # Review + cross-validation tasks
│       ├── tools.py         # Custom CrewAI tools
│       └── crew.py          # Crew assembly + kickoff
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Roadmap

- [x] **Phase 1**: Foundation MVP — 9 Hashira agent review
- [ ] **Phase 2**: RAG + Knowledge — project-aware context
- [ ] **Phase 3**: `@review-slayer` real-time conversation
- [ ] **Phase 4**: Web dashboard + SaaS

---

## License

MIT
