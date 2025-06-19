"""
회사 정보 조회 서비스 모듈
"""

import os
from functools import lru_cache
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


class CompanyServiceError(Exception):
    """회사 서비스 관련 예외"""

    pass


class CompanyService:
    """회사 서비스 클래스"""

    def __init__(self):
        self.api_key = os.getenv("FMP_API_KEY")
        if not self.api_key:
            raise CompanyServiceError("FMP_API_KEY 환경 변수를 설정해주세요.")
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Helper function to make requests to FMP API."""
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise CompanyServiceError(f"API 요청 실패: {e}")

    @lru_cache(maxsize=100)
    def search_companies(self, query: str) -> List[Dict[str, Any]]:
        """
        회사명/심볼 검색 (Financial Modeling Prep API 사용)
        """
        try:
            search_results = self._request(
                "search-ticker", {"query": query, "limit": 5}
            )
            return [{"symbol": r["symbol"], "name": r["name"]} for r in search_results]
        except Exception as e:
            raise CompanyServiceError(f"회사 검색 실패: {str(e)}")

    @lru_cache(maxsize=100)
    def get_company_info(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        회사 상세 정보 조회
        """
        try:
            # FMP provides most data in separate endpoints
            profile_data = self._request(f"profile/{symbol}")
            key_metrics_data = self._request(f"key-metrics-ttm/{symbol}")
            history_data = self._request(f"historical-price-full/{symbol}")

            if not profile_data:
                raise CompanyServiceError(f"유효하지 않은 심볼: {symbol}")

            # Combine info from different endpoints
            info = profile_data[0]
            if key_metrics_data:
                info.update(key_metrics_data[0])

            # The history data is in a dictionary key "historical"
            history = history_data.get("historical", [])

            return {"info": info, "history": history}
        except Exception as e:
            raise CompanyServiceError(f"회사 정보 조회 실패: {str(e)}")

    @lru_cache(maxsize=100)
    def analyze_company(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        try:
            data = self.get_company_info(symbol, period=period)
            info = data["info"]
            history = data["history"]

            current_price = history[0]["adjClose"] if history else 0
            price_change = 0
            if history and len(history) > 1:
                price_change = (
                    (current_price - history[-1]["adjClose"]) / history[-1]["adjClose"]
                ) * 100
                stock_history = [
                    {"date": item["date"], "close": item["adjClose"]}
                    for item in history
                ]
            else:
                stock_history = []

            # FMP has different naming conventions
            result = {
                "Company Description": info.get("description", ""),
                "Market Cap": info.get("mktCap", "N/A"),
                "Profit Margin": info.get("netProfitMargin", "N/A"),
                "Revenue Growth": "N/A",  # Not directly available, would need historical financials
                "Operating Margin": info.get("operatingMargin", "N/A"),
                "Trailing P/E": info.get("peRatio", "N/A"),
                "Forward P/E": info.get(
                    "priceToSalesRatio", "N/A"
                ),  # Using priceToSalesRatio as a proxy
                "Dividend Yield": info.get("dividendYield", "N/A"),
                "Price Change": f"{price_change:.1f}%",
                "Stock History": stock_history,
            }
            return result
        except Exception as e:
            raise CompanyServiceError(f"회사 분석 실패: {str(e)}")
