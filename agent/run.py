# agent/run.py

import argparse
import json
import re
import sys
import time

# import yfinance as yf # No longer needed
import ollama
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ==============================================================================
#  Finance Service (Web Scraping Edition)
# ==============================================================================


class FinanceService:
    """
    A service to fetch financial data by scraping the Yahoo Finance website.
    """

    BASE_URL = "https://finance.yahoo.com/quote"

    def _get_page_content(self, url: str) -> str:
        """Fetches page content using a headless browser."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                # Set a realistic user agent
                page.set_extra_http_headers(
                    {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/91.0.4472.124 Safari/537.36"
                        )
                    }
                )
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                content = page.content()
            finally:
                browser.close()
        return content

    def get_company_info(self, symbol: str) -> dict:
        print(f"🕵️  Scraping company info for {symbol}...")
        info = {"symbol": symbol}

        # --- Scraping Key Statistics Page ---
        url = f"{self.BASE_URL}/{symbol}/key-statistics"
        try:
            content = self._get_page_content(url)
            soup = BeautifulSoup(content, "html.parser")

            # Find all data tables
            tables = soup.find_all("table")
            for table in tables:
                for row in table.find_all("tr"):
                    cols = row.find_all("td")
                    if len(cols) == 2:
                        key = cols[0].text.strip()
                        value = cols[1].text.strip()
                        info[key] = value

            # --- Scraping Profile Page for Description ---
            profile_url = f"{self.BASE_URL}/{symbol}/profile"
            profile_content = self._get_page_content(profile_url)
            profile_soup = BeautifulSoup(profile_content, "html.parser")

            info["shortName"] = profile_soup.find("h1").text.strip()

            # Find description
            desc_p = profile_soup.find("p", class_=re.compile(r"Mt\(15px\) Lh\(1\.6\)"))
            if desc_p:
                info["longBusinessSummary"] = desc_p.text.strip()

            print(f"✅  Successfully scraped info for {info.get('shortName', symbol)}.")

        except Exception as e:
            print(f"❌  Error scraping company info for {symbol}: {e}")
            raise

        return info

    def get_financial_statements(self, symbol: str) -> dict:
        print(f"📄  Scraping financial statements for {symbol}...")
        financials = {}
        statement_urls = {
            "income_statement": f"{self.BASE_URL}/{symbol}/financials",
            "balance_sheet": f"{self.BASE_URL}/{symbol}/balance-sheet",
            "cash_flow": f"{self.BASE_URL}/{symbol}/cash-flow",
        }
        try:
            for key, url in statement_urls.items():
                print(f"  -> Scraping {key}...")
                content = self._get_page_content(url)
                soup = BeautifulSoup(content, "html.parser")

                # The data is within a complex div structure
                table_div = soup.find("div", class_="D(tbrg)")

                if not table_div:
                    financials[key] = (
                        pd.DataFrame()
                    )  # Return empty df if table not found
                    continue

                # Extract headers
                headers_div = table_div.find("div", class_="D(tbr)")
                headers = [h.text for h in headers_div.find_all("div", class_="D(ib)")]

                # Extract rows
                data_rows = []
                rows_div = table_div.find_all("div", class_=re.compile(r"D\(tbr\)"))[
                    1:
                ]  # Skip header row
                for row_div in rows_div:
                    row_data = [
                        d.text for d in row_div.find_all("div", class_="D(tbc)")
                    ]
                    data_rows.append(row_data)

                df = pd.DataFrame(data_rows, columns=headers)
                df = df.set_index(df.columns[0])  # Set first column as index
                financials[key] = df

            print("✅  Successfully scraped financial statements.")

        except Exception as e:
            print(f"❌  Error scraping financial statements for {symbol}: {e}")
            raise

        return financials

    def get_stock_history(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        # Note: Scraping historical data is complex due to dynamic loading and date pickers.
        # This functionality is temporarily disabled to remove the yfinance dependency.
        print(
            "⚠️  Stock history fetching is temporarily disabled. "
            "Returning empty data."
        )
        return pd.DataFrame()


# ==============================================================================
#  Analysis Service
# ==============================================================================


class AnalysisService:
    """
    A service to analyze financial data using an LLM via Ollama.
    """

    def __init__(self, model="deepseek-r1:1.5b"):
        self.model = model
        print(f"🤖  Initializing analysis service with model: {self.model}")
        try:
            ollama.show(self.model)
        except Exception:
            print(
                f"⚠️  Model '{self.model}' not found. Please ensure Ollama "
                "is running and you have pulled the model."
            )
            print(f"👉 You can pull the model with: `ollama pull {self.model}`")
            raise

    def analyze_company_data(
        self, info: dict, financials: dict, history: pd.DataFrame
    ) -> str:
        print("🧠  Generating financial analysis... (this may take a moment)")
        prompt_data = self._prepare_prompt_data(info, financials, history)
        prompt = self._create_prompt(prompt_data, info.get("shortName"))
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )
            analysis = response["message"]["content"]
            print("✅  Analysis generated successfully.")
            return analysis
        except Exception as e:
            print(f"❌  Error during Ollama API call: {e}")
            return "Could not generate analysis due to an error."

    def _prepare_prompt_data(
        self, info: dict, financials: dict, history: pd.DataFrame
    ) -> str:
        # Clean and stringify dataframes
        income_stmt_str = (
            financials["income_statement"].head().to_string()
            if not financials["income_statement"].empty
            else "Not Available"
        )
        balance_sheet_str = (
            financials["balance_sheet"].head().to_string()
            if not financials["balance_sheet"].empty
            else "Not Available"
        )
        cash_flow_str = (
            financials["cash_flow"].head().to_string()
            if not financials["cash_flow"].empty
            else "Not Available"
        )
        history_summary = (
            history.tail().to_string() if not history.empty else "Not Available"
        )

        key_info = {
            "Company Name": info.get("shortName"),
            "Symbol": info.get("symbol"),
            "Sector": info.get("Sector"),
            "Industry": info.get("Industry"),
            "Market Cap": info.get("Market Cap (intraday) 5"),
            "P/E Ratio": info.get("Trailing P/E"),
            "EPS": info.get("Diluted EPS (ttm)"),
            "Dividend Yield": info.get("Forward Annual Dividend Yield 4"),
            "52 Week High": info.get("52-Week High 3"),
            "52 Week Low": info.get("52-Week Low 3"),
            "Description": info.get("longBusinessSummary"),
        }

        # Remove None values
        key_info = {k: v for k, v in key_info.items() if v is not None}

        return f"""
        Company Information:
        {json.dumps(key_info, indent=2)}

        Recent Stock Performance (Last 5 days):
        {history_summary}

        Income Statement (Annual, recent years):
        {income_stmt_str}

        Balance Sheet (Annual, recent years):
        {balance_sheet_str}

        Cash Flow Statement (Annual, recent years):
        {cash_flow_str}
        """

    def _create_prompt(self, data_str: str, company_name: str) -> str:
        return f"""
        You are a top-tier financial analyst AI. Your task is to provide a \
comprehensive, yet easy-to-understand, financial analysis for {company_name}.

        **Company Data:**
        {data_str}

        **Your Analysis must include the following sections (use markdown formatting):**

        1.  **Executive Summary:** A concise overview of the company's \
financial health and market position. Conclude with a clear investment thesis \
(e.g., "Good for long-term growth," "Risky but high potential," "Stable dividend income").

        2.  **Financial Performance (Income Statement):**
            *   Analyze revenue, net income, and profit margins. Is the company growing profitably?
            *   Identify and explain key trends over the last few years.

        3.  **Financial Health (Balance Sheet):**
            *   Assess assets, liabilities, and equity.
            *   Evaluate debt levels (Debt-to-Equity) and liquidity \
(Current Ratio). Is the balance sheet strong?

        4.  **Cash Flow:**
            *   Analyze operating, investing, and financing cash flows. \
Is the company generating cash from its core business? How is it deploying capital?

        5.  **Valuation & Market View:**
            *   Comment on the company's valuation using the P/E ratio \
and other available metrics. Does it seem overvalued, undervalued, or fairly priced?
            *   Briefly mention recent stock performance as context.

        6.  **Risks & Opportunities:**
            *   Identify key potential risks (e.g., competition, debt, market shifts).
            *   Identify key opportunities (e.g., new products, market growth, strong financials).

        **Final Instruction:** Write the analysis as if you were presenting \
it to an intelligent retail investor. Be insightful and avoid simply restating the data.
        """


# ==============================================================================
#  Main Application
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(description="Headless financial research agent.")
    parser.add_argument(
        "symbol",
        type=str,
        help="The stock symbol of the company to analyze (e.g., AAPL, MSFT).",
    )
    args = parser.parse_args()

    symbol = args.symbol.upper()

    print(f"\n🚀  Starting analysis for symbol: {symbol}\n")

    try:
        # Initialize services
        finance_service = FinanceService()
        analysis_service = AnalysisService()

        # Fetch data
        company_info = finance_service.get_company_info(symbol)
        financial_statements = finance_service.get_financial_statements(symbol)
        stock_history = finance_service.get_stock_history(symbol)

        # Generate analysis
        analysis_report = analysis_service.analyze_company_data(
            info=company_info, financials=financial_statements, history=stock_history
        )

        # Print report
        print("\n\n" + "=" * 80)
        print(
            f"📊  Financial Analysis Report for "
            f"{company_info.get('shortName', symbol)} ({symbol})"
        )
        print("=" * 80 + "\n")
        print(analysis_report)

        # Save report to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"output/{symbol}_analysis_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(analysis_report)
        print("\n" + "=" * 80)
        print(f"📄  Report saved to {filename}")
        print("=" * 80)

    except Exception as e:
        print(f"\n\n❌  An unexpected error occurred: {e}", file=sys.stderr)
        print(
            "👉  Please check the stock symbol and your internet connection. "
            "If using Ollama, ensure it is running.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    import os

    if not os.path.exists("output"):
        os.makedirs("output")

    main()
