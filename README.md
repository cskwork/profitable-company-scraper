# Financial Research Agent

## 프로젝트 개요

- `yfinance` 라이브러리를 사용하여 기업의 재무 데이터를 가져오고, Ollama (`deepseek-r1:1.5b` 모델)를 활용하여 분석 보고서를 생성하는 헤드리스 에이전트입니다.
- 기존의 웹 API 기반 구조에서 명령줄에서 실행되는 에이전트 중심 아키텍처로 완전히 전환되었습니다.

## 🚀 원클릭 실행 (Windows)

### 처음 사용자를 위한 가장 쉬운 방법

```batch
# 1. 의존성 설치
install.bat

# 2. 에이전트 실행
run.bat
```

### 배치 파일 설명

- **`install.bat`** - 📦 가상 환경을 만들고 필요한 패키지를 설치합니다.
- **`run.bat`** - 🚀 가상 환경에서 에이전트를 실행합니다. 실행 시 분석할 회사의 티커 심볼을 입력하라는 메시지가 표시됩니다.

## 폴더 구조

```
profitable-company-scraper/
├── agent/                  # 메인 애플리케이션
│   └── run.py              # 데이터 수집, 분석 및 보고서 생성을 수행하는 에이전트
├── docs/                   # 문서
├── output/                 # 생성된 분석 보고서가 저장되는 위치
├── tests/                  # 테스트 스위트
├── .venv/                  # Python 가상 환경
├── install.bat             # 설치 스크립트
├── run.bat                 # 실행 스크립트
└── requirements.txt        # Python 의존성
```

## 수동 실행 방법

### 1. Python 환경 준비

```bash
# 가상 환경 생성
python -m venv .venv

# 가상 환경 활성화
.venv\Scripts\activate  # (Windows)
source .venv/bin/activate  # (Linux/Mac)

# 의존성 설치
pip install -r requirements.txt
```

### 2. Ollama 준비

Ollama가 로컬에서 실행 중인지 확인하세요. 또한 `deepseek-r1:1.5b` 모델을 내려받아야 합니다.

```bash
# 모델 내려받기
ollama pull deepseek-r1:1.5b
```

### 3. 에이전트 실행

```bash
# <SYMBOL>을 분석하려는 티커 심볼로 바꾸세요 (예: AAPL, MSFT)
python agent/run.py <SYMBOL>
```

생성된 보고서는 콘솔에 출력되고 `output/` 디렉터리에 마크다운 파일로 저장됩니다.

## 기술 스택

- **Core**: Python 3
- **Data**: yfinance
- **AI/LLM**: Ollama (`deepseek-r1:1.5b`)
- **Data Handling**: Pandas
- **Testing**: pytest

## 기여 및 문의

- Pull Request/이슈 환영
- 문의: [your-email@example.com]

## 라이선스

MIT 라이선스
