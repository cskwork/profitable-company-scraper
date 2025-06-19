# agent/services/finance_service.py

import pandas as pd
import yfinance as yf


class FinanceService:
    """
    A service to fetch financial data using the yfinance library.
    """

    def get_company_info(self, symbol: str) -> dict:
        """
        Get comprehensive company information for a given stock symbol.
        """
        print(f"🕵️  Fetching company info for {symbol}...")
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            if not info or "symbol" not in info:
                raise ValueError(
                    f"Could not find data for symbol: {symbol}. It might be "
                    "delisted or an incorrect ticker."
                )
            print(f"✅  Successfully fetched info for {info.get('shortName', symbol)}.")
            return info
        except Exception as e:
            print(f"❌  Error fetching company info for {symbol}: {e}")
            raise

    def get_stock_history(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Get historical stock price data.
        """
        print(f"📈  Fetching {period} stock history for {symbol}...")
        try:
            stock = yf.Ticker(symbol)
            history = stock.history(period=period)
            if history.empty:
                print(
                    f"⚠️  No historical data found for {symbol} for the period '{period}'."
                )
                return pd.DataFrame()
            print(
                f"✅  Successfully fetched {len(history)} data points for stock history."
            )
            return history
        except Exception as e:
            print(f"❌  Error fetching stock history for {symbol}: {e}")
            raise

    def get_financial_statements(self, symbol: str) -> dict:
        """
        Get major financial statements: income statement, balance sheet, and cash flow.
        """
        print(f"📄  Fetching financial statements for {symbol}...")
        try:
            stock = yf.Ticker(symbol)
            financials = {
                "income_statement": stock.income_stmt,
                "balance_sheet": stock.balance_sheet,
                "cash_flow": stock.cash_flow,
            }
            print("✅  Successfully fetched financial statements.")
            return financials
        except Exception as e:
            print(f"❌  Error fetching financial statements for {symbol}: {e}")
            raise
