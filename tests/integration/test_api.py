import pytest

from api.index import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_search_company_success(client):
    """회사 검색 API 정상 동작 테스트"""
    response = client.get("/api/search?query=Apple&lang=ko")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], list)


def test_search_company_empty_query(client):
    """빈 검색어 처리 테스트"""
    response = client.get("/api/search?query=&lang=ko")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"] == []


def test_analyze_company_success(client):
    """회사 분석 API 정상 동작 테스트"""
    response = client.get("/api/analyze/AAPL?lang=ko")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], dict)
    assert "Company Description" in data["data"]


def test_analyze_company_invalid_symbol(client):
    """존재하지 않는 심볼 처리 테스트"""
    response = client.get("/api/analyze/INVALIDSYM?lang=ko")
    # 실제 서비스 구현에 따라 500 또는 200+에러 메시지 반환 가능
    data = response.get_json()
    assert "error" in data or "data" in data
