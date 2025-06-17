"""
번역 서비스 모듈
"""

import time
from functools import lru_cache
from typing import Any, Dict, Optional, Union

from googletrans import Translator


class TranslationCache:
    """번역 결과를 캐싱하는 클래스"""

    def __init__(self, maxsize: int = 100):
        self._cache = {}
        self._maxsize = maxsize
        self._order = []

    def get(self, key: str) -> Union[str, None]:
        """캐시에서 값을 조회"""
        return self._cache.get(key)

    def set(self, key: str, value: str) -> None:
        """캐시에 값을 저장"""
        if len(self._cache) >= self._maxsize:
            # 가장 오래된 항목 제거
            oldest = self._order.pop(0)
            del self._cache[oldest]

        self._cache[key] = value
        self._order.append(key)

    def clear(self) -> None:
        """캐시 초기화"""
        self._cache.clear()
        self._order.clear()


class TranslationService:
    """번역 서비스 클래스"""

    def __init__(self, translator=None):
        self._translator = translator if translator is not None else Translator()
        self._cache = TranslationCache()

    def translate(self, text: str, target_lang: str) -> str:
        """텍스트를 대상 언어로 번역"""
        if not text:
            return text

        # 같은 언어로의 번역은 무시
        if target_lang == "en":
            return text

        # 캐시 확인
        cache_key = f"{text}:{target_lang}"
        cached_result = self._cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            # 번역 수행
            result = self._translator.translate(text, dest=target_lang)
            translated_text = result.text

            # 결과 캐싱
            self._cache.set(cache_key, translated_text)
            return translated_text
        except Exception as e:
            raise TranslationServiceError(f"번역 중 오류가 발생했습니다: {str(e)}")

    def translate_dict(self, data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """딕셔너리의 문자열 값을 번역"""
        try:
            result = {}
            for key, value in data.items():
                if isinstance(value, str):
                    result[key] = self.translate(value, target_lang)
                elif isinstance(value, dict):
                    result[key] = self.translate_dict(value, target_lang)
                else:
                    result[key] = value
            return result
        except Exception as e:
            raise TranslationServiceError(
                f"딕셔너리 번역 중 오류가 발생했습니다: {str(e)}"
            )


class TranslationServiceError(Exception):
    """번역 서비스 관련 예외"""

    pass
