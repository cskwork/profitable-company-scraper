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


def test_translation_cache():
    from api.services.translation_service import TranslationCache

    cache = TranslationCache(maxsize=2)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    cache.set("key3", "value3")
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
