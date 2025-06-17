"""
회사 정보 조회 서비스 모듈
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf
import requests


class CompanyServiceError(Exception):
    """회사 서비스 관련 예외"""

    pass


class SimpleLRUCache:
    """간단한 LRU 캐시 구현 (최대 100개)"""

    def __init__(self, maxsize=100):
        self._cache = {}
        self._order = []
        self._maxsize = maxsize

    def get(self, key):
        if key in self._cache:
            self._order.remove(key)
            self._order.append(key)
            return self._cache[key]
        return None

    def set(self, key, value):
        if key in self._cache:
            self._order.remove(key)
        elif len(self._cache) >= self._maxsize:
            oldest = self._order.pop(0)
            del self._cache[oldest]
        self._cache[key] = value
        self._order.append(key)

    def clear(self):
        self._cache.clear()
        self._order.clear()


class CompanyService:
    """회사 서비스 클래스"""

    def __init__(self):
        self._search_cache = SimpleLRUCache()
        self._analyze_cache = SimpleLRUCache()

    def search_companies(self, query: str) -> List[Dict[str, Any]]:
        """
        회사명/심볼 검색 (Yahoo Finance 검색 API 사용)
        """
        cache_key = query.strip().lower()
        cached = self._search_cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            # Yahoo Finance 검색 API 호출
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            results = []
            for quote in data.get("quotes", []):
                # EQUITY(주식)만 필터링
                if quote.get("quoteType") == "EQUITY":
                    results.append({
                        "symbol": quote.get("symbol", ""),
                        "name": quote.get("shortname", "") or quote.get("longname", "")
                    })
            # 최대 5개만 캐싱 및 반환
            self._search_cache.set(cache_key, results[:5])
            return results[:5]
        except Exception as e:
            # 한국어 주석: 검색 API 호출 실패 시 예외 처리
            raise CompanyServiceError(f"회사 검색 실패: {str(e)}")

    def get_company_info(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """
        회사 상세 정보 조회

        Args:
            symbol (str): 회사 심볼

        Returns:
            Dict: 회사 정보
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period=period)

            return {"info": info, "history": history}
        except Exception as e:
            raise CompanyServiceError(f"Failed to get company info: {str(e)}")

    def analyze_company(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        cache_key = f"{symbol.strip().upper()}_{period}"
        cached = self._analyze_cache.get(cache_key)
        if cached is not None:
            return cached
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
            self._analyze_cache.set(cache_key, result)
            return result
        except Exception as e:
            raise CompanyServiceError(f"Failed to analyze company: {str(e)}")

    def _search_companies_impl(self, query: str) -> List[Dict[str, Any]]:
        # 실제 데이터베이스/외부 API 연동 로직이 들어가는 부분
        # 아래는 예시 데이터
        return [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "marketCap": 2500000000000,
                "profitMargins": 0.25,
                "revenueGrowth": 0.12,
                "operatingMargins": 0.30,
                "trailingPE": 28.5,
                "forwardPE": 25.1,
                "dividendYield": 0.006,
            }
        ]

    def _analyze_company_impl(self, symbol: str) -> Dict[str, Any]:
        # 실제 데이터베이스/외부 API 연동 로직이 들어가는 부분
        # 아래는 예시 데이터
        return {
            "Company Description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            "Market Cap": 2500000000000,
            "Profit Margin": 0.25,
            "Revenue Growth": 0.12,
            "Operating Margin": 0.30,
            "Trailing P/E": 28.5,
            "Forward P/E": 25.1,
            "Dividend Yield": 0.006,
            "Price Change": 1.5,
        }
