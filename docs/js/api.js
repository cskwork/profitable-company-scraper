// API 통신을 위한 클래스
class API {
  constructor() {
    this.baseUrl = CONFIG.API_BASE_URL;
  }

  async searchCompany(query, language = "en") {
    try {
      const response = await fetch(
        `${this.baseUrl}${CONFIG.ENDPOINTS.SEARCH}?query=${encodeURIComponent(
          query
        )}&lang=${language}`
      );
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error("Search error:", error);
      return [];
    }
  }

  async analyzeCompany(symbol, language = "en") {
    try {
      const response = await fetch(
        `${this.baseUrl}${CONFIG.ENDPOINTS.ANALYZE}/${encodeURIComponent(
          symbol
        )}?lang=${language}`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Analysis failed");
      }

      // 데이터 구조 변환
      return {
        company_data: data.data,
        stock_history: data.data["Stock History"] || [],
        summary: this.generateSummary(data.data),
      };
    } catch (error) {
      console.error("Analysis error:", error);
      throw error;
    }
  }

  generateSummary(data) {
    const insights = [];

    // 수익성 분석
    const profitMargin = parseFloat(data["Profit Margin"]);
    if (!isNaN(profitMargin)) {
      if (profitMargin > 0.2) {
        insights.push("높은 수익성을 보이고 있습니다 (이익률 20% 이상)");
      } else if (profitMargin > 0.1) {
        insights.push("양호한 수익성을 유지하고 있습니다");
      }
    }

    // PER 분석
    const trailingPE = parseFloat(data["Trailing P/E"]);
    if (!isNaN(trailingPE)) {
      if (trailingPE < 15) {
        insights.push("저평가 가능성이 있습니다 (PER 15 미만)");
      } else if (trailingPE > 30) {
        insights.push("성장주 특성을 보입니다 (PER 30 이상)");
      }
    }

    // 성장성 분석
    const revenueGrowth = parseFloat(data["Revenue Growth"]);
    if (!isNaN(revenueGrowth) && revenueGrowth > 0.1) {
      insights.push("매출 성장세가 양호합니다 (10% 이상)");
    }

    return {
      insights: insights,
      summary:
        insights.length > 0 ? insights.join(". ") : "추가 분석이 필요합니다.",
    };
  }
}
