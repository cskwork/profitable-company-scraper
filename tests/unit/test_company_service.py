"""
회사 서비스 단위 테스트
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from api.services.company_service import CompanyService, CompanyServiceError


@pytest.fixture
def company_service():
    service = CompanyService()
    # 테스트 실행 전 캐시 클리어
    service.search_companies.cache_clear()
    service.get_company_info.cache_clear()
    service.analyze_company.cache_clear()
    return service


@pytest.fixture
def mock_ticker():
    mock = Mock()
    mock.info = {
        "longName": "Test Company",
        "shortName": "TEST",
        "marketCap": 1000000,
        "profitMargins": 0.1,
        "revenueGrowth": 0.05,
        "operatingMargins": 0.15,
        "trailingPE": 20,
        "forwardPE": 18,
        "dividendYield": 0.02,
    }
    history_mock = MagicMock()
    history_mock.__getitem__.return_value = [100, 110]
    mock.history.return_value = history_mock
    return mock


def test_search_companies(company_service):
    """회사 검색 테스트 (requests.get Mock)"""
    dummy_response = {
        "quotes": [
            {"symbol": "TEST", "shortname": "Test Company", "quoteType": "EQUITY"},
            {"symbol": "TEST2", "shortname": "Test Company2", "quoteType": "EQUITY"},
        ]
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = dummy_response
        results = company_service.search_companies("TEST")
        assert len(results) == 2
        assert results[0]["symbol"] == "TEST"
        assert results[0]["name"] == "Test Company"


def test_get_company_info(company_service, mock_ticker):
    """회사 정보 조회 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = mock_ticker
        info = company_service.get_company_info("TEST")

        assert "info" in info
        assert "history" in info
        assert info["info"]["longName"] == "Test Company"


def test_analyze_company(company_service, mock_ticker):
    """회사 분석 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = mock_ticker
        analysis = company_service.analyze_company("TEST")

        assert "Company Description" in analysis
        assert "Market Cap" in analysis
        assert "Profit Margin" in analysis
        assert "Revenue Growth" in analysis
        assert "Operating Margin" in analysis
        assert "Trailing P/E" in analysis
        assert "Forward P/E" in analysis
        assert "Dividend Yield" in analysis
        assert "Price Change" in analysis


def test_search_companies_error(company_service):
    """회사 검색 에러 테스트 (requests.get Mock)"""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("API Error")
        with pytest.raises(CompanyServiceError):
            company_service.search_companies("TEST")


def test_get_company_info_error(company_service):
    """회사 정보 조회 에러 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_ticker_class.side_effect = Exception("API Error")
        with pytest.raises(CompanyServiceError):
            company_service.get_company_info("TEST")


def test_analyze_company_error(company_service):
    """회사 분석 에러 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_ticker_class.side_effect = Exception("API Error")
        with pytest.raises(CompanyServiceError):
            company_service.analyze_company("TEST")


def test_search_companies_cached(company_service):
    """회사 검색 캐시 테스트"""
    dummy_response = {
        "quotes": [
            {"symbol": "TEST", "shortname": "Test Company", "quoteType": "EQUITY"}
        ]
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = dummy_response
        company_service.search_companies("TEST")
        company_service.search_companies("TEST")
        mock_get.assert_called_once()


def test_get_company_info_cached(company_service, mock_ticker):
    """회사 정보 조회 캐시 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = mock_ticker
        company_service.get_company_info("TEST")
        company_service.get_company_info("TEST")
        mock_ticker_class.assert_called_once_with("TEST")


def test_analyze_company_cached(company_service, mock_ticker):
    """회사 분석 캐시 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_ticker_class.return_value = mock_ticker
        company_service.analyze_company("TEST")
        company_service.analyze_company("TEST")
        assert company_service.analyze_company.cache_info().hits >= 1


def test_get_company_info_retry(company_service, mock_ticker):
    """회사 정보 조회 재시도 로직 테스트"""
    with patch("yfinance.Ticker") as mock_ticker_class, patch(
        "time.sleep"
    ) as mock_sleep:
        # 첫 두번은 429 에러, 세번째는 성공
        mock_ticker_class.side_effect = [
            Exception("429 Client Error"),
            Exception("429 Client Error"),
            mock_ticker,
        ]
        company_service.get_company_info("TEST")
        assert mock_ticker_class.call_count == 3
        mock_sleep.assert_called_with(2)


def test_analyze_company_get_info_error(company_service):
    """회사 분석 시 get_company_info 에러 테스트"""
    with patch.object(company_service, "get_company_info") as mock_get_info:
        mock_get_info.side_effect = CompanyServiceError("Get Info Error")
        with pytest.raises(CompanyServiceError) as exc_info:
            company_service.analyze_company("TEST")
        assert "회사 분석 실패" in str(exc_info.value)
