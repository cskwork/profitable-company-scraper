"""
번역 서비스 모듈
"""

from functools import lru_cache
from typing import Any, Dict

from googletrans import Translator


class TranslationServiceError(Exception):
    """번역 서비스 관련 예외"""

    pass


class TranslationService:
    """번역 서비스 클래스"""

    def __init__(self, translator=None):
        self._translator = translator if translator is not None else Translator()

    @lru_cache(maxsize=200)
    def translate(self, text: str, target_lang: str) -> str:
        """텍스트를 대상 언어로 번역"""
        if not text or target_lang == "en":
            return text

        try:
            result = self._translator.translate(text, dest=target_lang)
            return result.text
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
