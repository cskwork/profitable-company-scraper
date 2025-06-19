import pytest

from api.index import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_search_company_success(client, mocker):
    """회사 검색 API 정상 동작 테스트"""
    mock_search_results = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
    ]
    mocker.patch(
        "api.index.company_service.search_companies", return_value=mock_search_results
    )
    mocker.patch(
        "api.index.translation_service.translate_dict",
        side_effect=lambda d, lang: {**d, "name": d["name"] + f" ({lang})"},
    )

    response = client.get("/api/search?query=Apple&lang=ko")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 2
    assert data["data"][0]["name"] == "Apple Inc. (ko)"


def test_search_company_empty_query(client):
    """빈 검색어 처리 테스트"""
    response = client.get("/api/search?query=&lang=ko")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"] == []


def test_analyze_company_success(client, mocker):
    """회사 분석 API 정상 동작 테스트"""
    mock_analysis_result = {
        "Company Description": "An amazing company.",
        "Market Cap": "2T",
    }
    mocker.patch(
        "api.index.company_service.analyze_company", return_value=mock_analysis_result
    )
    mocker.patch(
        "api.index.translation_service.translate_dict",
        side_effect=lambda d, lang: {k: f"{v} ({lang})" for k, v in d.items()},
    )

    response = client.get("/api/analyze/AAPL?lang=ko")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], dict)
    assert data["data"]["Company Description"] == "An amazing company. (ko)"


def test_analyze_company_invalid_symbol(client, mocker):
    """존재하지 않는 심볼 처리 테스트"""
    from api.services.company_service import CompanyServiceError

    mocker.patch(
        "api.index.company_service.analyze_company",
        side_effect=CompanyServiceError("Invalid symbol"),
    )
    response = client.get("/api/analyze/INVALIDSYM?lang=ko")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Invalid symbol" in data["error"]


def test_analyze_multi_success(client, mocker):
    """여러 기업 분석 API 정상 동작 테스트"""
    mock_analysis_result = {
        "Company Description": "An amazing company.",
        "Market Cap": "2T",
    }
    mocker.patch(
        "api.index.company_service.analyze_company", return_value=mock_analysis_result
    )

    response = client.post("/api/analyze-multi", json={"symbols": ["AAPL", "MSFT"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 2
    assert data["data"][0]["symbol"] == "AAPL"


def test_analyze_multi_empty_symbols(client):
    """여러 기업 분석 API 빈 심볼 리스트 테스트"""
    response = client.post("/api/analyze-multi", json={"symbols": []})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_search_company_company_service_error(client, mocker):
    """회사 검색 API, CompanyServiceError 발생 테스트"""
    from api.services.company_service import CompanyServiceError

    mocker.patch(
        "api.index.company_service.search_companies",
        side_effect=CompanyServiceError("Service Error"),
    )
    response = client.get("/api/search?query=Apple")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Service Error" in data["error"]


def test_search_company_translation_service_error(client, mocker):
    """회사 검색 API, TranslationServiceError 발생 테스트"""
    from api.services.translation_service import TranslationServiceError

    mocker.patch(
        "api.index.company_service.search_companies",
        return_value=[{"name": "Apple"}],
    )
    mocker.patch(
        "api.index.translation_service.translate_dict",
        side_effect=TranslationServiceError("Translation Error"),
    )
    response = client.get("/api/search?query=Apple&lang=ko")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Translation Error" in data["error"]


def test_search_company_resource_exhausted(client, mocker):
    """회사 검색 API, 자원 고갈 에러 테스트"""
    mocker.patch(
        "api.index.company_service.search_companies",
        side_effect=Exception("resource_exhausted"),
    )
    response = client.get("/api/search?query=Apple")
    assert response.status_code == 429
    data = response.get_json()
    assert "error" in data
    assert "Service is temporarily unavailable" in data["error"]


def test_analyze_company_translation_service_error(client, mocker):
    """회사 분석 API, TranslationServiceError 발생 테스트"""
    from api.services.translation_service import TranslationServiceError

    mocker.patch(
        "api.index.company_service.analyze_company",
        return_value={"desc": "description"},
    )
    mocker.patch(
        "api.index.translation_service.translate_dict",
        side_effect=TranslationServiceError("Translation Error"),
    )
    response = client.get("/api/analyze/AAPL?lang=ko")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Translation Error" in data["error"]


def test_analyze_company_resource_exhausted(client, mocker):
    """회사 분석 API, 자원 고갈 에러 테스트"""
    mocker.patch(
        "api.index.company_service.analyze_company",
        side_effect=Exception("resource_exhausted"),
    )
    response = client.get("/api/analyze/AAPL")
    assert response.status_code == 429
    data = response.get_json()
    assert "error" in data
    assert "Service is temporarily unavailable" in data["error"]


def test_analyze_company_generic_error_translated(client, mocker):
    """회사 분석 API, 일반 에러 번역 테스트"""
    mocker.patch(
        "api.index.company_service.analyze_company",
        side_effect=Exception("Generic Error"),
    )
    mocker.patch(
        "api.index.translation_service.translate",
        return_value="번역된 에러",
    )
    response = client.get("/api/analyze/AAPL?lang=ko")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "번역된 에러"


def test_analyze_multi_company_service_error(client, mocker):
    """여러 기업 분석 API, 개별 기업 분석 에러 테스트"""
    mocker.patch(
        "api.index.company_service.analyze_company",
        side_effect=[{"desc": "description"}, Exception("Service Error")],
    )
    response = client.post("/api/analyze-multi", json={"symbols": ["AAPL", "GOOG"]})
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) == 2
    assert "error" not in data["data"][0]
    assert "error" in data["data"][1]
    assert "Service Error" in data["data"][1]["error"]


def test_analyze_multi_bad_request(client):
    """여러 기업 분석 API, 잘못된 요청 테스트"""
    response = client.post(
        "/api/analyze-multi", data="not json", content_type="application/json"
    )
    assert response.status_code == 500


def test_search_company_generic_error(client, mocker):
    """회사 검색 API, 일반 에러 테스트"""
    mocker.patch(
        "api.index.company_service.search_companies",
        side_effect=Exception("Generic Error"),
    )
    response = client.get("/api/search?query=Apple")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Generic Error" in data["error"]
