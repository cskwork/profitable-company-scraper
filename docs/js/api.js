class API {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
    }

    async searchCompany(query, language = 'en') {
        try {
            const response = await fetch(`${this.baseUrl}${CONFIG.ENDPOINTS.SEARCH}?query=${encodeURIComponent(query)}&lang=${language}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    }

    async analyzeCompany(symbol, language = 'en') {
        try {
            const response = await fetch(`${this.baseUrl}${CONFIG.ENDPOINTS.ANALYZE}/${symbol}?lang=${language}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Analysis error:', error);
            throw error;
        }
    }
}
