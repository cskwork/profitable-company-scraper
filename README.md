# Profitable Company Scraper

## 프로젝트 개요

- 다양한 기업의 재무/성장성/수익성/시장지표를 분석하고, 시각화 및 번역 기능을 제공하는 통합 플랫폼
- Flask + Vue3 + Plotly.js 기반 REST API 및 웹 클라이언트
- SOLID 원칙, TDD, 자동화, 최신 개발환경 적용

## 🚀 원클릭 실행 (Windows)

### 처음 사용자를 위한 가장 쉬운 방법

```batch
# 1. 전체 자동 설정 및 실행 (권장)
setup_all.bat

# 또는 개별 실행:
# 2. 설치만
install.bat

# 3. 서버 실행
run.bat

# 4. 테스트 실행
test.bat
```

### 배치 파일 설명

- **`setup_all.bat`** - 🎯 모든 것을 자동으로! (설치 → 테스트 → 서버 실행)
- **`install.bat`** - 📦 가상환경 생성 및 패키지 설치
- **`run.bat`** - 🚀 가상환경에서 서버 실행
- **`test.bat`** - 🧪 다양한 테스트 옵션 제공 (대화형 메뉴)

## 폴더 구조

```
profitable-company-scraper/
├── api/                    # Main application backend
│   ├── index.py           # Flask API endpoints and business logic
│   └── services/          # Business logic services
│       ├── company_service.py    # Yahoo Finance integration
│       └── translation_service.py # Translation service
├── docs/                  # Frontend assets and documentation
│   ├── index.html        # Main web UI
│   └── js/               # JavaScript files for frontend
│       ├── api.js        # API communication module
│       ├── config.js     # Configuration
│       └── main.js       # Main application logic
├── tests/                # Test suites
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/            # End-to-end tests
├── data/                 # Data storage directory
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Development dependencies
├── run_server.py        # Server startup script
├── quick_test.py        # Quick functionality test
├── setup_and_test.py    # Automated setup and test script
├── render.yaml          # Render deployment configuration
└── vercel.json          # Vercel configuration (alternative deployment)
```

## 주요 기능

- **회사 검색/분석 API**: 심볼/이름으로 검색, 상세 재무분석, 기간별 주가 히스토리 제공
- **다국어 번역**: 결과를 한국어/영어/일본어/중국어 등으로 변환
- **시각화**: Plotly.js 기반 주가/재무지표 차트, 멀티 기업 비교, 인사이트 자동 생성
- **CSV 다운로드**: 분석/비교 결과 표를 CSV로 저장
- **Swagger UI**: `/apidocs`에서 API 문서 및 테스트
- **테스트 자동화**: 단위/통합/브라우저(E2E) 테스트, 코드 린트/포맷터 적용

## 🚀 빠른 시작

### 가장 간단한 실행 방법

#### Windows 사용자

```batch
# 더블클릭 또는 명령어 실행
setup_all.bat
```

#### Linux/Mac 사용자

```bash
# 실행 권한 부여 (최초 1회)
chmod +x install.sh run.sh

# 설치 및 실행
./install.sh
./run.sh
```

## 설치 및 실행 방법 (상세)

### 1. Python 환경 준비

```bash
python -m venv .venv
.venv\Scripts\activate  # (Windows)
source .venv/bin/activate  # (Linux/Mac)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구
```

### 2. 자동 설정 및 테스트

```bash
# 모든 설정과 테스트를 자동으로 실행
python setup_and_test.py
```

### 3. 서버 실행

```bash
# 방법 1: 간편 실행 스크립트
python run_server.py

# 방법 2: Flask 직접 실행
cd api
python index.py

# 방법 3: Flask CLI
flask --app api.index run --host=0.0.0.0 --port=5000
```

### 4. 웹 접속

- 웹 UI: `http://localhost:5000/` 또는 `http://localhost:5000/docs/index.html`
- API 문서: `http://localhost:5000/apidocs`

### 5. 테스트 실행

```bash
# 전체 테스트
pytest -v

# 개별 테스트
pytest tests/unit/ -v         # 단위 테스트
pytest tests/integration/ -v  # 통합 테스트
pytest tests/e2e/ -v         # E2E 테스트 (서버 실행 필요)

# 커버리지 포함
pytest --cov=api --cov-report=html --cov-report=term
```

### 6. 코드 품질 관리

```bash
# 자동 포맷팅
black .
isort .

# 린팅
flake8 . --exclude=.venv,archive --max-line-length=88
```

## 최근 개선사항 (2024)

- ✅ **코드 품질**: Black/isort/Flake8 적용, 프로덕션 보안 강화 (debug 모드 제거)
- ✅ **API 개선**: Yahoo Finance API 429 에러 재시도 로직, 에러 메시지 개선
- ✅ **프론트엔드**: API 모듈 분리 (api.js), 설정 파일 개선, 정적 파일 라우팅
- ✅ **테스트**: E2E 테스트 개선, 빠른 테스트 스크립트 추가
- ✅ **자동화**: 서버 실행 스크립트, 프로젝트 설정 자동화
- ✅ **문서화**: 개선사항 문서, 프로젝트 요약 문서 추가

## 알려진 이슈 및 해결방법

- **Yahoo Finance API 속도 제한**: 429 에러 발생 시 자동 재시도 (최대 3회, 대기 시간 증가)
- **회사 분석 실패**: 잘못된 심볼이나 API 제한으로 실패할 수 있음
- **웹 UI 라우팅**: 라우트 변경 후 서버 재시작 필요

## API 엔드포인트

- `GET /api/search?query={query}&lang={lang}` - 회사 검색
- `GET /api/analyze/{symbol}?lang={lang}&period={period}` - 회사 분석
- `POST /api/analyze-multi` - 여러 회사 비교
- `GET /apidocs` - Swagger API 문서

## Technology Stack

- Backend: Python Flask 3.0.0
- Frontend: Vue.js 3, HTML, JavaScript
- Charts: Plotly.js
- APIs: Yahoo Finance (yfinance 0.2.50)
- Translation: Google Translate (googletrans 4.0.0-rc1)
- Testing: pytest, Playwright
- Code Quality: Black, isort, Flake8
- Deployment: Render, Vercel

## Dependencies

```
flask==3.0.0
flask-cors==4.0.0
yfinance==0.2.50
googletrans==4.0.0-rc1
plotly==5.18.0
pandas==2.1.3
flasgger
gunicorn==21.2.0
python-dotenv==1.0.0
```

개발 의존성은 `requirements-dev.txt` 참조

## 기여 및 문의

- Pull Request/이슈 환영
- 추가 문서: `README_IMPROVEMENTS.md`, `PROJECT_SUMMARY.md` 참조
- 문의: [your-email@example.com]

## License

MIT License
