# agent/services/analysis_service.py

import json

import ollama
import pandas as pd


class AnalysisService:
    """
    A service to analyze financial data using an LLM via Ollama.
    """

    def __init__(self, model="deepseek-r1:1.5b"):
        self.model = model
        print(f"🤖  Initializing analysis service with model: {self.model}")
        try:
            # Check if the model is available
            ollama.show(self.model)
        except Exception as e:
            print(
                f"⚠️  Model '{self.model}' not found locally. Please make sure "
                "Ollama is running and the model is pulled."
            )
            print("👉 You can pull the model with: `ollama pull {self.model}`")
            raise e

    def analyze_company_data(
        self, info: dict, financials: dict, history: pd.DataFrame
    ) -> str:
        """
        Analyzes the company's financial data and generates a report.
        """
        print("🧠  Generating financial analysis...")

        # Prepare a condensed and clean version of the data for the prompt
        prompt_data = self._prepare_prompt_data(info, financials, history)

        # Create the prompt for the LLM
        prompt = self._create_prompt(prompt_data)

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
        """
        Prepares a string representation of the financial data for the LLM prompt.
        """
        # Convert dataframes to string representations
        income_stmt_str = financials["income_statement"].to_string()
        balance_sheet_str = financials["balance_sheet"].to_string()
        cash_flow_str = financials["cash_flow"].to_string()
        history_summary = history.tail().to_string()

        # Key info subset
        key_info = {
            "Company Name": info.get("shortName"),
            "Symbol": info.get("symbol"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Market Cap": f"${info.get('marketCap', 0):,}",
            "P/E Ratio": info.get("trailingPE"),
            "EPS": info.get("trailingEps"),
            "Dividend Yield": f"{info.get('dividendYield', 0) * 100:.2f}%",
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
            "Description": info.get("longBusinessSummary"),
        }

        # Combine everything into a single string
        prompt_data_str = f"""
        Company Information:
        --------------------
        {json.dumps(key_info, indent=2)}

        Recent Stock Performance (Last 5 days):
        ---------------------------------------
        {history_summary}

        Income Statement (Annual):
        --------------------------
        {income_stmt_str}

        Balance Sheet (Annual):
        -----------------------
        {balance_sheet_str}

        Cash Flow Statement (Annual):
        -----------------------------
        {cash_flow_str}
        """
        return prompt_data_str

    def _create_prompt(self, data_str: str) -> str:
        """
        Creates the full prompt for the LLM.
        """
        prompt = f"""
        As a senior financial analyst, your task is to provide a comprehensive \
analysis of the following company based on the provided data.

        **Company Data:**
        {data_str}

        **Your Analysis should include the following sections:**

        1.  **Executive Summary:** A brief, high-level overview of the \
company's financial health and market position. Is this a good investment?

        2.  **Financial Performance:**
            *   Analyze the revenue, net income, and profit margins from the \
Income Statement. Is the company growing? Is it profitable?
            *   Comment on the key trends you observe.

        3.  **Financial Position (Balance Sheet):**
            *   Assess the company's assets, liabilities, and equity.
            *   Comment on the company's debt levels (e.g., Debt-to-Equity \
ratio) and liquidity (e.g., Current Ratio). Is the company financially stable?

        4.  **Cash Flow Analysis:**
            *   Analyze the operating, investing, and financing cash flows. \
Is the company generating cash from its core operations? How is it using its cash?

        5.  **Valuation and Market Performance:**
            *   Comment on the company's valuation using metrics like P/E ratio.
            *   Briefly touch on the recent stock performance.

        6.  **Risks and Opportunities:**
            *   Based on the description and financial data, identify \
potential risks and opportunities for the company.

        **Instructions:**
        *   Be objective and data-driven.
        *   Use clear and concise language.
        *   Structure your response using markdown.
        *   Do not just list the numbers, provide insights.
        """
        return prompt
