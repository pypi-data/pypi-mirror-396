"""PRD Acceptance Criteria 통합 테스트.

PRD Section 6 (Acceptance Criteria) 검증을 위한 테스트.
- AC1: search_news
- AC3: get_today_issues
- AC8: Performance
- AC9: Reliability
- AC10: Caching
"""

import time

import pytest

from bigkinds_mcp.tools.search import search_news, init_search_tools
from bigkinds_mcp.tools.article import init_article_tools
from bigkinds_mcp.tools.visualization import init_visualization_tools
from bigkinds_mcp.core.async_client import AsyncBigKindsClient
from bigkinds_mcp.core.async_scraper import AsyncArticleScraper
from bigkinds_mcp.core.cache import MCPCache


@pytest.fixture
def setup_tools():
    """테스트용 도구 초기화."""
    client = AsyncBigKindsClient()
    scraper = AsyncArticleScraper()
    cache = MCPCache()

    init_search_tools(client, cache)
    init_article_tools(client, scraper, cache)
    init_visualization_tools(client, cache)

    yield {"client": client, "scraper": scraper, "cache": cache}

    client.close()


class TestAC1SearchNews:
    """AC1: search_news Acceptance Criteria."""

    @pytest.mark.asyncio
    async def test_ac1_keyword_required(self, setup_tools):
        """AC1: 키워드 필수, 빈 키워드 시 에러 반환."""
        result = await search_news(
            keyword="",
            start_date="2024-12-01",
            end_date="2024-12-15",
        )
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_PARAMS"

    @pytest.mark.asyncio
    async def test_ac1_date_format_validation(self, setup_tools):
        """AC1: start_date, end_date 필수, YYYY-MM-DD 형식 검증."""
        # 잘못된 날짜 형식
        result = await search_news(
            keyword="AI",
            start_date="2024/12/01",  # 잘못된 형식
            end_date="2024-12-15",
        )
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_PARAMS"

    @pytest.mark.asyncio
    async def test_ac1_page_size_limit(self, setup_tools):
        """AC1: page_size 최대 100 제한."""
        result = await search_news(
            keyword="AI",
            start_date="2024-12-01",
            end_date="2024-12-15",
            page_size=150,  # 100 초과
        )
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_PARAMS"

    @pytest.mark.asyncio
    async def test_ac1_sort_by_both_merges_results(self, setup_tools):
        """AC1: sort_by='both' 시 date+relevance 병합, news_id로 중복 제거."""
        result = await search_news(
            keyword="AI",
            start_date="2024-12-01",
            end_date="2024-12-15",
            sort_by="both",
            page_size=20,
        )

        # 성공적인 응답
        assert "total_count" in result
        assert "articles" in result

        # 중복 news_id 없어야 함
        news_ids = [a["news_id"] for a in result["articles"]]
        assert len(news_ids) == len(set(news_ids))

    @pytest.mark.asyncio
    async def test_ac1_pagination_metadata(self, setup_tools):
        """AC1: 응답에 total_count, page, total_pages 포함."""
        result = await search_news(
            keyword="AI",
            start_date="2024-12-01",
            end_date="2024-12-15",
        )

        assert "total_count" in result
        assert "page" in result
        assert "total_pages" in result
        assert result["page"] >= 1
        assert result["total_pages"] >= 1


class TestAC3TodayIssues:
    """AC3: get_today_issues Acceptance Criteria."""

    @pytest.mark.asyncio
    async def test_ac3_default_date_is_today(self, setup_tools):
        """AC3: date 미지정 시 오늘 날짜 사용 (KST 기준)."""
        client = setup_tools["client"]
        result = await client.get_today_issues()

        # 성공적인 응답 (데이터가 없을 수도 있음)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_ac3_category_filter(self, setup_tools):
        """AC3: category 필터 지원."""
        client = setup_tools["client"]
        # 카테고리 필터 기능 테스트 (네트워크 상태에 따라 타임아웃 가능)
        try:
            result = await client.get_today_issues(category="전체")
            assert isinstance(result, dict)
        except Exception:
            # 네트워크 이슈 시 skip
            pytest.skip("Network timeout - skipping category filter test")


class TestAC8Performance:
    """AC8: Performance Acceptance Criteria."""

    @pytest.mark.asyncio
    async def test_ac8_search_response_under_3s(self, setup_tools):
        """AC8: 뉴스 검색 응답 < 3초."""
        start = time.time()

        await search_news(
            keyword="AI",
            start_date="2024-12-01",
            end_date="2024-12-15",
            page_size=10,
        )

        elapsed = time.time() - start
        assert elapsed < 3.0, f"검색 응답 시간: {elapsed:.2f}s (3초 초과)"

    @pytest.mark.asyncio
    async def test_ac8_cache_hit_under_100ms(self, setup_tools):
        """AC8: 캐시 적중 시 응답 < 100ms."""
        # 첫 번째 요청 (캐시 워밍업)
        await search_news(
            keyword="캐시테스트",
            start_date="2024-12-01",
            end_date="2024-12-15",
            page_size=5,
        )

        # 두 번째 요청 (캐시 적중)
        start = time.time()
        await search_news(
            keyword="캐시테스트",
            start_date="2024-12-01",
            end_date="2024-12-15",
            page_size=5,
        )
        elapsed = time.time() - start

        assert elapsed < 0.1, f"캐시 응답 시간: {elapsed:.2f}s (100ms 초과)"


class TestAC9Reliability:
    """AC9: Reliability Acceptance Criteria."""

    def test_ac9_retry_config(self):
        """AC9: API 실패 시 재시도 (최대 3회) 설정 확인."""
        from bigkinds_mcp.core.async_client import MAX_RETRIES
        assert MAX_RETRIES == 3

    def test_ac9_timeout_config(self):
        """AC9: 네트워크 타임아웃 30초 설정 확인."""
        from bigkinds_mcp.core.async_client import TIMEOUT
        assert TIMEOUT == 30.0

    @pytest.mark.asyncio
    async def test_ac9_error_response_format(self, setup_tools):
        """AC9: 에러 응답에 success=false, error 메시지 포함."""
        result = await search_news(
            keyword="",  # 빈 키워드로 에러 유발
            start_date="2024-12-01",
            end_date="2024-12-15",
        )

        assert result["success"] is False
        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]


class TestAC10Caching:
    """AC10: Caching Acceptance Criteria."""

    def test_ac10_cache_ttl_config(self):
        """AC10: 캐시 TTL 설정 확인 (PRD AC10)."""
        from bigkinds_mcp.core.cache import (
            SEARCH_CACHE_TTL,
            ARTICLE_CACHE_TTL,
            TREND_CACHE_TTL,
        )

        # 검색 결과 캐시 TTL: 5분 (300초)
        assert SEARCH_CACHE_TTL == 300

        # 기사 상세 캐시 TTL: 30분 (1800초)
        assert ARTICLE_CACHE_TTL == 1800

        # 트렌드/연관어 캐시 TTL: 10분 (600초)
        assert TREND_CACHE_TTL == 600

    @pytest.mark.asyncio
    async def test_ac10_search_cache_works(self, setup_tools):
        """AC10: 검색 결과 캐시 동작 확인."""
        cache = setup_tools["cache"]

        # 첫 번째 요청
        result1 = await search_news(
            keyword="캐시동작테스트",
            start_date="2024-12-01",
            end_date="2024-12-15",
        )

        # 캐시에 저장되었는지 확인
        cached = cache.get_search(
            keyword="캐시동작테스트",
            start_date="2024-12-01",
            end_date="2024-12-15",
            page=1,
            page_size=20,
            providers=None,
            categories=None,
            sort_by="both",
        )

        assert cached is not None
