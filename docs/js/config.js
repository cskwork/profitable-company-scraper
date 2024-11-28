const CONFIG = {
    // API endpoints - replace [YOUR-VERCEL-URL] with your actual Vercel deployment URL
    API_BASE_URL: 'https://[YOUR-VERCEL-URL]',
    ENDPOINTS: {
        SEARCH: '/api/search',
        ANALYZE: '/api/analyze'
    },
    
    // Chart configuration
    CHART_CONFIG: {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    },
    
    // Language settings
    DEFAULT_LANGUAGE: 'en',
    TRANSLATIONS: {
        en: {
            CHART_TITLE: 'Stock Price History',
            DATE_LABEL: 'Date',
            PRICE_LABEL: 'Price ($)',
            METRIC_LABEL: 'Metric',
            VALUE_LABEL: 'Value',
            LOADING: 'Loading...',
            ERROR: 'Error fetching data',
            NO_DATA: 'Chart data not available'
        },
        ko: {
            CHART_TITLE: '주가 기록',
            DATE_LABEL: '날짜',
            PRICE_LABEL: '가격 ($)',
            METRIC_LABEL: '지표',
            VALUE_LABEL: '값',
            LOADING: '로딩 중...',
            ERROR: '데이터를 가져오는 중 오류가 발생했습니다',
            NO_DATA: '차트 데이터를 사용할 수 없습니다'
        }
    }
};
