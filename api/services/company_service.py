"""
회사 정보 조회 서비스 모듈
"""

import time
from functools import lru_cache
from typing import Any, Dict, List

import requests
import yfinance as yf


class CompanyServiceError(Exception):
    """회사 서비스 관련 예외"""

    pass


class CompanyService:
    """회사 서비스 클래스"""

    @lru_cache(maxsize=100)
    def search_companies(self, query: str) -> List[Dict[str, Any]]:
        """
        회사명/심볼 검색 (Yahoo Finance 검색 API 사용)
        """
        try:
            url = (
                f"https://query2.finance.yahoo.com/v1/finance/search"
                f"?q={query}&quotesCount=10&newsCount=0"
            )
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            results = []
            for quote in data.get("quotes", []):
                if quote.get("quoteType") == "EQUITY":
                    results.append(
                        {
                            "symbol": quote.get("symbol", ""),
                            "name": quote.get("shortname", "")
                            or quote.get("longname", ""),
                        }
                    )
            return results[:5]
        except Exception as e:
            raise CompanyServiceError(f"회사 검색 실패: {str(e)}")

    @lru_cache(maxsize=100)
    def get_company_info(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        회사 상세 정보 조회 (429 에러 자동 재시도)
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                history = ticker.history(period=period)
                return {"info": info, "history": history}
            except Exception as e:
                # 429 에러 감지 시 재시도
                if "429" in str(e) and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                # 한국어 안내 메시지 포함
                raise CompanyServiceError(
                    f"회사 정보 조회 실패: {str(e)} (야후 파이낸스 요청 제한(429)일 수 있습니다. 잠시 후 다시 시도해 주세요.)"
                )

    @lru_cache(maxsize=100)
    def analyze_company(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        try:
            data = self.get_company_info(symbol, period=period)
            info = data["info"]
            history = data["history"]
            current_price = info.get("currentPrice", 0)
            price_change = 0
            if history is not None and not history.empty:
                price_change = (
                    (current_price - history["Close"][0]) / history["Close"][0]
                ) * 100
                # 주가 히스토리 추출 (최근 1년, 날짜/종가)
                stock_history = [
                    {"date": str(idx.date()), "close": float(row)}
                    for idx, row in history["Close"].items()
                ]
            else:
                stock_history = []
            result = {
                "Company Description": info.get("longBusinessSummary", ""),
                "Market Cap": info.get("marketCap", "N/A"),
                "Profit Margin": info.get("profitMargins", "N/A"),
                "Revenue Growth": info.get("revenueGrowth", "N/A"),
                "Operating Margin": info.get("operatingMargins", "N/A"),
                "Trailing P/E": info.get("trailingPE", "N/A"),
                "Forward P/E": info.get("forwardPE", "N/A"),
                "Dividend Yield": info.get("dividendYield", "N/A"),
                "Price Change": f"{price_change:.1f}%",
                "Stock History": stock_history,
            }
            return result
        except Exception as e:
            # 한국어 안내 메시지 포함
            raise CompanyServiceError(
                f"회사 분석 실패: {str(e)} (야후 파이낸스 요청 제한(429)일 수 있습니다. 잠시 후 다시 시도해 주세요.)"
            )
