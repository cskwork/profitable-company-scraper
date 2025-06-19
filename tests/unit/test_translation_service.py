"""
번역 서비스 단위 테스트
"""

from unittest.mock import Mock

import pytest

from api.services.translation_service import (TranslationService,
                                              TranslationServiceError)


@pytest.fixture
def mock_translator():
    mock = Mock()
    mock.translate.return_value = Mock(text="번역된 텍스트")
    return mock


@pytest.fixture(autouse=True)
def clear_translation_cache():
    """매 테스트 후 번역 캐시 초기화"""
    # lru_cache가 적용된 클래스의 새 인스턴스를 만들거나,
    # 직접 캐시를 초기화합니다.
    # 여기서는 TranslationService의 translate 메소드 캐시를 초기화합니다.
    # 단, 이 방법은 lru_cache가 클래스 외부에서 함수에 적용되었을 때 더 간단합니다.
    # 클래스 내부에 적용된 경우, 인스턴스화된 후에 접근해야 할 수 있습니다.
    # TranslationService가 상태를 가지지 않으므로, 테스트별로 새로 생성하는 것이
    # 가장 깔끔한 방법일 수 있습니다. 여기서는 명시적으로 클리어합니다.
    TranslationService.translate.cache_clear()
    yield
    TranslationService.translate.cache_clear()


def test_translate(mock_translator):
    service = TranslationService(translator=mock_translator)
    result = service.translate("Test text", "ko")
    assert result == "번역된 텍스트"
    mock_translator.translate.assert_called_once_with("Test text", dest="ko")


def test_translate_cached(mock_translator):
    service = TranslationService(translator=mock_translator)
    result1 = service.translate("Test text", "ko")
    result2 = service.translate("Test text", "ko")
    assert result1 == result2 == "번역된 텍스트"
    assert mock_translator.translate.call_count == 1


def test_translate_same_language():
    service = TranslationService()
    result = service.translate("Test text", "en")
    assert result == "Test text"


def test_translate_empty_text():
    service = TranslationService()
    result = service.translate("", "ko")
    assert result == ""


def test_translate_dict(mock_translator):
    service = TranslationService(translator=mock_translator)
    data = {
        "name": "Test Company",
        "description": "Test Description",
        "nested": {"title": "Test Title"},
        "number": 123,
    }
    result = service.translate_dict(data, "ko")
    assert result["name"] == "번역된 텍스트"
    assert result["description"] == "번역된 텍스트"
    assert result["nested"]["title"] == "번역된 텍스트"
    assert result["number"] == 123


def test_translate_error():
    mock_translator = Mock()
    mock_translator.translate.side_effect = Exception("Translation Error")
    service = TranslationService(translator=mock_translator)
    with pytest.raises(TranslationServiceError) as exc_info:
        service.translate("Test text", "ko")
    assert "번역 중 오류가 발생했습니다" in str(exc_info.value)


def test_translate_dict_error():
    mock_translator = Mock()
    mock_translator.translate.side_effect = Exception("Translation Error")
    service = TranslationService(translator=mock_translator)
    with pytest.raises(TranslationServiceError) as exc_info:
        service.translate_dict({"text": "Test"}, "ko")
    assert "딕셔너리 번역 중 오류가 발생했습니다" in str(exc_info.value)
