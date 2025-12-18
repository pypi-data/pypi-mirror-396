# BigKinds MCP Server

[![PyPI version](https://badge.fury.io/py/bigkinds-mcp.svg)](https://badge.fury.io/py/bigkinds-mcp)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/seolcoding/bigkinds-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/seolcoding/bigkinds-mcp/actions/workflows/test.yml)

한국 뉴스 데이터베이스 [BigKinds](https://www.bigkinds.or.kr)를 위한 MCP(Model Context Protocol) 서버입니다.

Claude Desktop, Claude Code, Cursor 등 MCP 클라이언트에서 **한국 뉴스 검색, 분석, 대용량 데이터 처리**를 자연어로 수행할 수 있습니다.

## 주요 기능

| 기능 | 설명 | 로그인 |
|------|------|--------|
| **뉴스 검색** | 키워드, 날짜, 언론사, 카테고리 기반 검색 | 불필요 |
| **기사 상세** | 전체 본문, 메타데이터, 이미지 추출 | 불필요 |
| **기사 스크래핑** | URL에서 직접 기사 내용 추출 | 불필요 |
| **오늘의 이슈** | 일별 인기 이슈 Top 10 (지역별/AI 선정) | 불필요 |
| **키워드 트렌드** | 시계열 기사 수 추이 분석 | **필요** |
| **연관어 분석** | TF-IDF 기반 연관 키워드 추출 | **필요** |
| **키워드 비교** | 여러 키워드 트렌드 비교 분석 | 불필요 |
| **대용량 내보내기** | 최대 50,000건 JSON/CSV/JSONL 내보내기 | 불필요 |

---

## 빠른 시작

### 1단계: 설치

```bash
# uvx 사용 (권장 - 별도 설치 없이 바로 실행)
uvx bigkinds-mcp

# 또는 pip 설치
pip install bigkinds-mcp
```

### 2단계: MCP 클라이언트 설정

#### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "bigkinds": {
      "command": "uvx",
      "args": ["bigkinds-mcp"]
    }
  }
}
```

#### Claude Code

```bash
claude mcp add bigkinds -- uvx bigkinds-mcp
```

#### Cursor / VS Code

`.cursor/mcp.json` 또는 `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "bigkinds": {
      "command": "uvx",
      "args": ["bigkinds-mcp"]
    }
  }
}
```

### 3단계: 사용하기

```
사용자: 최근 AI 관련 뉴스 검색해줘

Claude: [search_news 도구 사용]
2025년 12월 AI 관련 뉴스 6,401건을 찾았습니다.

주요 기사:
1. "삼성전자, AI 반도체 투자 확대" - 매일경제
2. "네이버, 하이퍼클로바X 성능 대폭 개선" - 한국경제
...
```

---

## 상세 기능 가이드

### 뉴스 검색 (search_news)

키워드, 날짜, 언론사, 카테고리를 조합하여 뉴스를 검색합니다.

```
예시 질문:
- "인공지능 관련 뉴스 검색해줘"
- "경향신문과 한겨레에서 경제 뉴스 찾아줘"
- "지난 한 달간 반도체 관련 기사 검색"
```

**파라미터:**

| 파라미터 | 필수 | 설명 | 예시 |
|---------|------|------|------|
| `keyword` | O | 검색 키워드 | `"AI"`, `"반도체"` |
| `start_date` | O | 시작일 (YYYY-MM-DD) | `"2025-01-01"` |
| `end_date` | O | 종료일 (YYYY-MM-DD) | `"2025-12-15"` |
| `page` | X | 페이지 번호 (기본: 1) | `1` |
| `page_size` | X | 페이지당 결과 수 (기본: 10, 최대: 100) | `20` |
| `providers` | X | 언론사 필터 | `["경향신문", "한겨레"]` |
| `categories` | X | 카테고리 필터 | `["경제", "IT_과학"]` |
| `sort_by` | X | 정렬 방식 | `"date"`, `"relevance"`, `"both"` |

**정렬 방식:**
- `"both"` (기본값): 날짜순 + 관련도순 병합, 중복 제거
- `"date"`: 최신순
- `"relevance"`: 관련도순

---

### 기사 수 집계 (get_article_count)

키워드별 기사 수를 일별/주별/월별로 집계합니다.

```
예시 질문:
- "올해 AI 관련 기사가 몇 건이나 있어?"
- "반도체 기사 수 월별로 보여줘"
```

**파라미터:**

| 파라미터 | 필수 | 설명 | 예시 |
|---------|------|------|------|
| `keyword` | O | 검색 키워드 | `"AI"` |
| `start_date` | O | 시작일 | `"2025-01-01"` |
| `end_date` | O | 종료일 | `"2025-12-15"` |
| `group_by` | X | 집계 단위 | `"total"`, `"day"`, `"week"`, `"month"` |
| `providers` | X | 언론사 필터 | `["경향신문"]` |

---

### 기사 상세 조회 (get_article)

BigKinds 기사 ID로 전체 본문을 조회합니다.

```
예시 질문:
- "이 기사 전문 보여줘"
- "기사 ID가 02100101.20251215174513002인 기사 내용"
```

**파라미터:**

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| `news_id` | △ | BigKinds 기사 ID |
| `url` | △ | 기사 URL (news_id 없을 때) |
| `include_full_content` | X | 전문 포함 여부 (기본: True) |

> **Note**: BigKinds detailView API를 통해 전체 본문을 가져옵니다. 실패 시 URL 스크래핑으로 폴백합니다.

---

### 기사 스크래핑 (scrape_article_url)

URL에서 직접 기사 내용을 추출합니다.

```
예시 질문:
- "이 URL의 기사 내용 가져와줘: https://n.news.naver.com/..."
- "네이버 뉴스 기사 스크래핑해줘"
```

**파라미터:**

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| `url` | O | 기사 URL |
| `extract_images` | X | 이미지 추출 여부 (기본: False) |

---

### 오늘의 이슈 (get_today_issues)

일별 인기 이슈 Top 10을 조회합니다.

```
예시 질문:
- "오늘 인기 뉴스 뭐야?"
- "서울 지역 이슈 보여줘"
- "AI가 선정한 오늘의 이슈"
```

**파라미터:**

| 파라미터 | 필수 | 설명 | 값 |
|---------|------|------|-----|
| `date` | X | 조회 날짜 (기본: 오늘) | `"2025-12-15"` |
| `category` | X | 카테고리 필터 | `"전체"`, `"서울"`, `"경인강원"`, `"충청"`, `"경상"`, `"전라제주"`, `"AI"` |

---

### 키워드 비교 (compare_keywords)

여러 키워드의 기사 수를 비교 분석합니다.

```
예시 질문:
- "AI, 반도체, 전기차 기사 수 비교해줘"
- "올해 가장 많이 언급된 키워드가 뭐야?"
```

**파라미터:**

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| `keywords` | O | 비교할 키워드 목록 (2-10개) |
| `start_date` | O | 시작일 |
| `end_date` | O | 종료일 |
| `group_by` | X | 집계 단위 (`"total"`, `"day"`, `"week"`, `"month"`) |

---

### 대용량 샘플링 (smart_sample)

대용량 검색 결과에서 대표 샘플을 추출합니다.

```
예시 질문:
- "이재명 관련 기사 100건만 샘플링해줘"
- "균등하게 분포된 샘플 뽑아줘"
```

**파라미터:**

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| `keyword` | O | 검색 키워드 |
| `start_date` | O | 시작일 |
| `end_date` | O | 종료일 |
| `sample_size` | X | 샘플 수 (기본: 100, 최대: 500) |
| `strategy` | X | 샘플링 전략 |

**샘플링 전략:**
- `"stratified"` (기본값): 기간별 균등 분포
- `"latest"`: 최신 기사 우선
- `"random"`: 무작위 샘플링

---

### 전체 내보내기 (export_all_articles)

검색 결과를 파일로 내보냅니다.

```
예시 질문:
- "AI 관련 기사 전체 JSON으로 저장해줘"
- "분석용 데이터 CSV로 내보내줘"
```

**파라미터:**

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| `keyword` | O | 검색 키워드 |
| `start_date` | O | 시작일 |
| `end_date` | O | 종료일 |
| `output_format` | X | 출력 형식 (`"json"`, `"csv"`, `"jsonl"`) |
| `output_path` | X | 저장 경로 (기본: 자동 생성) |
| `max_articles` | X | 최대 기사 수 (기본: 10,000, 최대: 50,000) |
| `include_content` | X | 전문 포함 여부 (기본: False) |

> **Note**: 100건 이상의 데이터 분석 시 `export_all_articles`로 로컬 파일 저장 후 Python 스크립트로 분석하는 것을 권장합니다.

---

### 키워드 트렌드 (get_keyword_trends) - 로그인 필요

키워드별 기사 수 추이를 시계열로 분석합니다.

```
예시 질문:
- "AI 키워드 트렌드 보여줘"
- "올해 반도체 기사 추이 분석"
```

**환경변수 설정 필요:**

```bash
export BIGKINDS_USER_ID=your_email@example.com
export BIGKINDS_USER_PASSWORD=your_password
```

---

### 연관어 분석 (get_related_keywords) - 로그인 필요

검색 키워드와 연관된 키워드를 TF-IDF 기반으로 추출합니다.

```
예시 질문:
- "AI와 연관된 키워드가 뭐야?"
- "반도체 관련 연관어 분석해줘"
```

---

## 지원 언론사 및 카테고리

### 언론사 (72개)

**종합일간지:** 경향신문, 국민일보, 동아일보, 문화일보, 서울신문, 세계일보, 조선일보, 중앙일보, 한겨레, 한국일보

**경제지:** 매일경제, 머니투데이, 서울경제, 아시아경제, 아주경제, 파이낸셜뉴스, 한국경제, 헤럴드경제

**방송사:** KBS, MBC, SBS, YTN, 연합뉴스TV

**전문지:** 디지털타임스, 전자신문 등

### 카테고리 (8개)

`정치`, `경제`, `사회`, `문화`, `국제`, `지역`, `스포츠`, `IT_과학`

---

## MCP Resources

| URI | 설명 |
|-----|------|
| `stats://providers` | 전체 언론사 코드 목록 |
| `stats://categories` | 전체 카테고리 코드 목록 |
| `news://{keyword}/{date}` | 특정 날짜 뉴스 검색 결과 |
| `article://{news_id}` | 개별 기사 정보 |

---

## MCP Prompts

| Prompt | 설명 |
|--------|------|
| `news_analysis` | 뉴스 분석 (요약/감성/트렌드/비교) |
| `trend_report` | 트렌드 리포트 생성 |
| `issue_briefing` | 일일 이슈 브리핑 |
| `large_scale_analysis` | 대용량 분석 워크플로우 가이드 |

---

## 환경변수

| 변수 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `BIGKINDS_USER_ID` | △ | BigKinds 로그인 이메일 | - |
| `BIGKINDS_USER_PASSWORD` | △ | BigKinds 로그인 비밀번호 | - |
| `BIGKINDS_TIMEOUT` | X | API 타임아웃 (초) | `30` |
| `BIGKINDS_MAX_RETRIES` | X | 최대 재시도 횟수 | `3` |
| `BIGKINDS_RETRY_DELAY` | X | 재시도 간격 (초) | `1.0` |

> **Note**: 로그인이 필요한 기능(키워드 트렌드, 연관어 분석)을 사용하려면 `BIGKINDS_USER_ID`와 `BIGKINDS_USER_PASSWORD`를 설정하세요.

---

## 개발

### 소스에서 설치

```bash
git clone https://github.com/seolcoding/bigkinds-mcp.git
cd bigkinds-mcp
uv sync
```

### 서버 실행

```bash
uv run bigkinds-mcp
```

### 테스트

```bash
# 전체 테스트
uv run pytest

# 단위 테스트만
uv run pytest tests/unit/ -v

# 통합 테스트 (실제 API 호출)
uv run pytest tests/integration/ -v
```

### 린트 및 포맷

```bash
uv run ruff check .
uv run ruff format .
```

---

## 프로젝트 구조

```
bigkinds/
├── src/bigkinds_mcp/           # MCP 서버
│   ├── server.py               # 엔트리포인트
│   ├── tools/                  # MCP Tools (14개)
│   │   ├── search.py           # 검색 도구
│   │   ├── article.py          # 기사 도구
│   │   ├── analysis.py         # 분석 도구
│   │   └── metadata.py         # 메타데이터 도구
│   ├── resources/              # MCP Resources (4개)
│   ├── prompts/                # MCP Prompts (4개)
│   ├── core/                   # 핵심 모듈
│   │   ├── async_client.py     # 비동기 API 클라이언트
│   │   ├── async_scraper.py    # 비동기 스크래퍼
│   │   └── cache.py            # 인메모리 캐시
│   ├── models/                 # Pydantic 스키마
│   └── utils/                  # 유틸리티
├── tests/                      # 테스트
│   ├── unit/                   # 단위 테스트
│   ├── integration/            # 통합 테스트
│   └── e2e/                    # E2E 테스트
└── docs/                       # 문서
```

---

## 기여하기

기여를 환영합니다! 다음 방법으로 기여할 수 있습니다:

1. **버그 리포트**: [Issues](https://github.com/seolcoding/bigkinds-mcp/issues)에 버그를 보고해주세요.
2. **기능 요청**: 새로운 기능 아이디어를 제안해주세요.
3. **Pull Request**: 코드 개선, 버그 수정, 문서 개선 등

### 개발 가이드

1. Fork 후 브랜치 생성
2. 변경사항 커밋
3. 테스트 통과 확인 (`uv run pytest`)
4. Pull Request 생성

---

## 관련 링크

- [PyPI Package](https://pypi.org/project/bigkinds-mcp/)
- [BigKinds 공식 사이트](https://www.bigkinds.or.kr)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

## 라이선스

MIT License - 자유롭게 사용, 수정, 배포할 수 있습니다.

---

## 주의사항

- 이 프로젝트는 BigKinds의 **비공식 API**를 활용합니다.
- BigKinds 이용약관을 준수하여 사용해주세요.
- 대량 요청 시 서버에 부담을 주지 않도록 적절한 딜레이를 두세요.
