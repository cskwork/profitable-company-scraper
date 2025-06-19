"""
회사 서비스 단위 테스트
"""

import os
from unittest.mock import patch

import pytest
import requests

from api.services.company_service import CompanyService, CompanyServiceError

# Set a dummy API key for testing
os.environ["FMP_API_KEY"] = "test_key"


@pytest.fixture
def mock_fmp_api():
    """Financial Modeling Prep API 모의(mock) 객체에 대한 Fixture"""
    with patch("requests.get") as mock_get:
        # search_companies 모의 객체 설정
        mock_search_response = [
            {"symbol": "TEST", "name": "Test Company"},
            {"symbol": "TEST2", "name": "Test Company 2"},
        ]

        # get_company_info 모의 객체 설정
        mock_profile_response = [
            {
                "symbol": "TEST",
                "price": 150.0,
                "beta": 1.1,
                "volAvg": 5000000,
                "mktCap": 1000000000,
                "lastDiv": 5.0,
                "range": "100-200",
                "changes": 1.5,
                "companyName": "Test Company",
                "currency": "USD",
                "cik": "12345",
                "isin": "US1234567890",
                "cusip": "123456789",
                "exchange": "NASDAQ",
                "exchangeShortName": "NASDAQ",
                "industry": "Technology",
                "website": "https://test.com",
                "description": "A test company.",
                "ceo": "Mr. Test",
                "sector": "Software",
                "country": "US",
                "fullTimeEmployees": "1000",
                "phone": "123-456-7890",
                "address": "123 Test St",
                "city": "Testville",
                "state": "TS",
                "zip": "12345",
                "dcfDiff": 10,
                "dcf": 160,
                "image": "https://test.com/logo.png",
                "ipoDate": "2020-01-01",
                "defaultImage": False,
                "isEtf": False,
                "isActivelyTrading": True,
                "isAdr": False,
                "isFund": False,
            }
        ]

        mock_key_metrics_response = [
            {
                "peRatio": 15,
                "priceToSalesRatio": 10,  # Used as Forward P/E
                "dividendYield": 0.02,
                "netProfitMargin": 0.10,
                "operatingMargin": 0.12,
            }
        ]

        mock_history_response = {
            "historical": [
                {"date": "2023-01-02", "adjClose": 155.0},
                {"date": "2023-01-01", "adjClose": 150.0},
            ]
        }

        def mock_router(*args, **kwargs):
            if "search-ticker" in args[0]:
                mock_resp = requests.Response()
                mock_resp.status_code = 200
                mock_resp.json = lambda: mock_search_response
                return mock_resp
            if "profile" in args[0]:
                mock_resp = requests.Response()
                mock_resp.status_code = 200
                mock_resp.json = lambda: mock_profile_response
                return mock_resp
            if "key-metrics-ttm" in args[0]:
                mock_resp = requests.Response()
                mock_resp.status_code = 200
                mock_resp.json = lambda: mock_key_metrics_response
                return mock_resp
            if "historical-price-full" in args[0]:
                mock_resp = requests.Response()
                mock_resp.status_code = 200
                mock_resp.json = lambda: mock_history_response
                return mock_resp
            return requests.Response()

        mock_get.side_effect = mock_router
        yield mock_get


@pytest.fixture
def company_service():
    """CompanyService에 대한 Fixture"""
    service = CompanyService()
    # 테스트 실행 전 캐시 클리어
    service.search_companies.cache_clear()
    service.get_company_info.cache_clear()
    service.analyze_company.cache_clear()
    return service


def test_search_companies_success(company_service, mock_fmp_api):
    """회사 검색 성공 테스트"""
    results = company_service.search_companies("Test")
    assert len(results) == 2
    assert results[0]["symbol"] == "TEST"
    assert results[0]["name"] == "Test Company"


def test_get_company_info_success(company_service, mock_fmp_api):
    """회사 정보 조회 성공 테스트"""
    data = company_service.get_company_info("TEST")
    assert data["info"]["symbol"] == "TEST"
    assert "history" in data


def test_analyze_company_success(company_service, mock_fmp_api):
    """회사 분석 성공 테스트"""
    analysis = company_service.analyze_company("TEST")
    assert analysis["Market Cap"] == 1000000000
    assert analysis["Trailing P/E"] == 15
    assert "Price Change" in analysis
    assert "Stock History" in analysis
    assert len(analysis["Stock History"]) == 2


def test_search_companies_error(company_service, mock_fmp_api):
    """회사 검색 에러 테스트"""
    mock_fmp_api.side_effect = requests.exceptions.RequestException("API Error")
    with pytest.raises(CompanyServiceError):
        company_service.search_companies("TEST")


def test_get_company_info_error(company_service, mock_fmp_api):
    """회사 정보 조회 에러 테스트"""
    mock_fmp_api.side_effect = requests.exceptions.RequestException("API Error")
    with pytest.raises(CompanyServiceError):
        company_service.get_company_info("TEST")


def test_analyze_company_error(company_service, mock_fmp_api):
    """회사 분석 에러 테스트"""
    mock_fmp_api.side_effect = requests.exceptions.RequestException("API Error")
    with pytest.raises(CompanyServiceError):
        company_service.analyze_company("TEST")


def test_search_companies_cached(company_service, mock_fmp_api):
    """회사 검색 캐시 테스트"""
    company_service.search_companies("TEST")
    company_service.search_companies("TEST")
    mock_fmp_api.assert_called_once()


def test_get_company_info_cached(company_service, mock_fmp_api):
    """회사 정보 조회 캐시 테스트"""
    company_service.get_company_info("TEST")
    company_service.get_company_info("TEST")
    assert mock_fmp_api.call_count == 3  # profile, key-metrics, history
    company_service.get_company_info("TEST")
    assert mock_fmp_api.call_count == 3


def test_analyze_company_cached(company_service, mock_fmp_api):
    """회사 분석 캐시 테스트"""
    company_service.analyze_company("TEST")
    info = company_service.analyze_company.cache_info()
    assert info.hits == 0  # First call
    company_service.analyze_company("TEST")
    info = company_service.analyze_company.cache_info()
    assert info.hits == 1  # Second call is a cache hit


def test_analyze_company_get_info_error(company_service, mock_fmp_api):
    """회사 분석 시 get_company_info 에러 테스트"""
    with patch.object(company_service, "get_company_info") as mock_get_info:
        mock_get_info.side_effect = CompanyServiceError("Get Info Error")
        with pytest.raises(CompanyServiceError) as exc_info:
            company_service.analyze_company("TEST")
        assert "회사 분석 실패" in str(exc_info.value)
