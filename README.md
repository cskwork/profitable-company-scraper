# Profitable Company Scraper

## 프로젝트 개요

- 다양한 기업의 재무/성장성/수익성/시장지표를 분석하고, 시각화 및 번역 기능을 제공하는 통합 플랫폼
- Flask + Vue3 + Plotly.js 기반 REST API 및 웹 클라이언트
- SOLID 원칙, TDD, 자동화, 최신 개발환경 적용

## 폴더 구조

```
profitable-company-scraper/
├── api/                    # Main application backend
│   └── index.py           # Flask API endpoints and business logic
├── docs/                  # Frontend assets and documentation
│   └── js/               # JavaScript files for frontend
├── templates/            # HTML templates
│   └── index.html        # Main application page
├── data/                 # Data storage directory
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment configuration
└── vercel.json          # Vercel configuration (alternative deployment)
```

## 주요 기능

- **회사 검색/분석 API**: 심볼/이름으로 검색, 상세 재무분석, 기간별 주가 히스토리 제공
- **다국어 번역**: 결과를 한국어/영어/일본어/중국어 등으로 변환
- **시각화**: Plotly.js 기반 주가/재무지표 차트, 멀티 기업 비교, 인사이트 자동 생성
- **CSV 다운로드**: 분석/비교 결과 표를 CSV로 저장
- **Swagger UI**: `/apidocs`에서 API 문서 및 테스트
- **테스트 자동화**: 단위/통합/브라우저(E2E) 테스트, 코드 린트/포맷터 적용

## 설치 및 실행 방법

### 1. Python 환경 준비

```bash
python -m venv .venv
.venv\Scripts\activate  # (Windows)
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
cd api
python index.py  # 기본 5000번 포트
```

### 3. 웹 클라이언트 접속

- 브라우저에서 `http://localhost:5000/docs/index.html` 접속

### 4. API 문서(Swagger)

- 브라우저에서 `http://localhost:5000/apidocs` 접속

### 5. 테스트 실행

```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
# E2E: 서버 실행 후
pytest tests/e2e/test_ui.py
```

### 6. 코드 품질 자동화

```bash
black . && isort .
flake8 .
```

## 개선/고도화 내역

- SOLID 기반 서비스 분리, 의존성 주입, 캐싱 최적화
- 번역/회사 서비스 단위테스트 및 통합테스트 완비
- Swagger 기반 API 문서 자동화
- Plotly.js 기반 시각화(주가, 재무지표, 멀티 비교, 인사이트)
- 기간별 주가 차트, 멀티 기업 비교, CSV 다운로드 등 프론트 고도화
- Playwright 기반 E2E 테스트 자동화
- black/isort/flake8 등 코드 스타일 자동화

## 기여 및 문의

- Pull Request/이슈 환영
- 문의: [your-email@example.com]

## Technology Stack

- Backend: Python Flask
- Frontend: HTML, JavaScript
- APIs: Yahoo Finance (yfinance)
- Translation: Google Translate
- Deployment: Render

## Dependencies

```
flask==3.0.0
flask-cors==4.0.0
yfinance==0.2.31
googletrans==3.1.0a0
numpy==1.24.3
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/cskwork/profitable-company-scraper.git
cd profitable-company-scraper
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python api/index.py
```

## Usage

1. Access the application through your web browser
2. Enter a company stock symbol or name in the search bar
3. View detailed financial analysis and metrics
4. Toggle between languages using the language selector

## Live Demo

The application is deployed and accessible at:
[Render Deployment](https://profitable-company-scraper.onrender.com)

## Development

The main application code is in `api/index.py`, which handles:

- Company search and data retrieval
- Financial analysis and calculations
- Multi-language support
- API endpoints for frontend interaction

## Archive

Previous versions and unused components are stored in the `archive/` directory for reference.

## License

MIT License
