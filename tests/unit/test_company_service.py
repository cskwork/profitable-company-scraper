"""
회사 서비스 단위 테스트
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from api.services.company_service import CompanyService, CompanyServiceError


@pytest.fixture
def company_service():
    return CompanyService()


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


def test_search_companies(company_service, mock_ticker):
    """회사 검색 테스트"""
    with patch("yfinance.Tickers") as mock_tickers:
        mock_tickers.return_value.tickers = {"TEST": mock_ticker}
        results = company_service.search_companies("TEST")

        assert len(results) == 1
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
    """회사 검색 에러 테스트"""
    with patch("yfinance.Tickers") as mock_tickers:
        mock_tickers.side_effect = Exception("API Error")
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
