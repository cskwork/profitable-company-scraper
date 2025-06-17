import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# JSON 데이터 로드
with open('company_data_20241128_221849.json', 'r') as f:
    data = json.load(f)

# 데이터 전처리 함수
def clean_numeric(value):
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '').replace('%', '')
        if 'T' in value:
            value = float(value.replace('T', '')) * 1e12
        elif 'B' in value:
            value = float(value.replace('B', '')) * 1e9
        elif 'M' in value:
            value = float(value.replace('M', '')) * 1e6
        else:
            try:
                value = float(value)
            except:
                value = None
    return value

# 주요 지표 추출
metrics = {
    'Market Cap': [],
    'Revenue (TTM)': [],
    'Operating Margin': [],
    'P/E Ratio': [],
    'Total Cash': [],
    'Total Debt': [],
    'ROE': []
}

companies = []
for company, company_data in data.items():
    companies.append(company)
    metrics['Market Cap'].append(clean_numeric(company_data.get('Market Cap')))
    metrics['Revenue (TTM)'].append(clean_numeric(company_data.get('Revenue  (ttm)')))
    metrics['Operating Margin'].append(clean_numeric(company_data.get('Operating Margin  (ttm)').replace('%', '')))
    metrics['P/E Ratio'].append(clean_numeric(company_data.get('Trailing P/E')))
    metrics['Total Cash'].append(clean_numeric(company_data.get('Total Cash  (mrq)')))
    metrics['Total Debt'].append(clean_numeric(company_data.get('Total Debt  (mrq)')))
    metrics['ROE'].append(clean_numeric(company_data.get('Return on Equity  (ttm)').replace('%', '')))

df = pd.DataFrame(metrics, index=companies)

# 1. 시가총액 비교
plt.figure(figsize=(12, 6))
plt.bar(companies, df['Market Cap'] / 1e12)
plt.title('기업별 시가총액 (조 달러)')
plt.xticks(rotation=45)
plt.ylabel('시가총액 (조 달러)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('market_cap_comparison.png')
plt.close()

# 2. 주요 재무비율 비교
plt.figure(figsize=(12, 6))
metrics_to_plot = ['Operating Margin', 'ROE']
x = np.arange(len(companies))
width = 0.35

plt.bar(x - width/2, df['Operating Margin'], width, label='영업이익률 (%)')
plt.bar(x + width/2, df['ROE'], width, label='자기자본이익률 (%)')
plt.title('기업별 수익성 지표 비교')
plt.xticks(x, companies, rotation=45)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('profitability_comparison.png')
plt.close()

# 3. 현금 및 부채 비교
plt.figure(figsize=(12, 6))
width = 0.35
x = np.arange(len(companies))

plt.bar(x - width/2, df['Total Cash'] / 1e9, width, label='현금 보유액')
plt.bar(x + width/2, df['Total Debt'] / 1e9, width, label='총 부채')
plt.title('기업별 현금 및 부채 비교 (십억 달러)')
plt.xticks(x, companies, rotation=45)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('cash_debt_comparison.png')
plt.close()

# 4. P/E 비율 비교
plt.figure(figsize=(12, 6))
plt.bar(companies, df['P/E Ratio'])
plt.title('기업별 P/E 비율')
plt.xticks(rotation=45)
plt.ylabel('P/E Ratio')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('pe_ratio_comparison.png')
plt.close()

# 상세 분석 리포트 생성
report = f"""# 빅테크 기업 상세 재무 분석 리포트 ({datetime.now().strftime('%Y-%m-%d')})

## 1. 시가총액 및 기업 가치
### 시가총액 순위
{df['Market Cap'].sort_values(ascending=False).apply(lambda x: f"${x/1e12:.2f}T").to_string()}

### 매출 대비 시가총액 비율
{(df['Market Cap'] / df['Revenue (TTM)']).round(2).to_string()}

## 2. 수익성 분석
### 영업이익률 (%)
{df['Operating Margin'].round(2).to_string()}

### 자기자본이익률 (%)
{df['ROE'].round(2).to_string()}

## 3. 재무 건전성
### 현금 보유액 (십억 달러)
{(df['Total Cash'] / 1e9).round(2).to_string()}

### 부채 비율 (%)
{((df['Total Debt'] / df['Market Cap']) * 100).round(2).to_string()}

## 4. 투자 가치 지표
### P/E 비율
{df['P/E Ratio'].round(2).to_string()}

## 5. 기업별 핵심 분석

### Apple (AAPL)
- 최대 시가총액 보유 기업이나 매출 성장률 둔화 우려
- 서비스 부문 성장이 하드웨어 의존도 완화에 기여
- 높은 영업이익률과 현금 창출력이 강점

### Microsoft (MSFT)
- 클라우드와 AI 성장이 실적 개선 견인
- 기업용 소프트웨어 시장에서 독보적 위치
- 안정적인 구독형 수익 모델이 강점

### Alphabet (GOOGL)
- 광고 시장 의존도가 높으나 클라우드 사업 성장 중
- AI 기술력과 데이터 자산이 경쟁우위 요소
- 상대적으로 낮은 P/E 비율로 저평가 가능성

### NVIDIA (NVDA)
- AI 붐의 최대 수혜주이나 높은 밸류에이션
- 데이터센터 GPU 시장 독점적 지위
- 반도체 사이클 리스크 존재

### Meta (META)
- 수익성 회복과 비용 효율화 진행 중
- AI 투자와 메타버스 성과가 관건
- 합리적인 밸류에이션 대비 높은 성장성

## 6. 투자 전략 제언

### 단기 전략 (6개월-1년)
- AI 관련 수혜주 선별적 투자 (NVDA, MSFT)
- 밸류에이션 부담 큰 종목 비중 축소
- 실적 개선 모멘텀 보유 기업 관심 (META)

### 중장기 전략 (2-3년)
- 클라우드/AI 인프라 보유 기업 중심 포트폴리오 구성
- 높은 현금창출력 기업 우선 고려
- 기술 혁신 역량 보유 기업 장기 투자

### 리스크 관리
- 고평가 주식 분산 투자
- 부채비율 모니터링
- 규제 리스크 대응 능력 평가

## 7. 산업 전망

### 성장 동력
- AI/머신러닝 기술 발전
- 클라우드 컴퓨팅 수요 증가
- 디지털 전환 가속화

### 위험 요소
- 인플레이션과 금리 정책
- 기술 기업 규제 강화
- 글로벌 공급망 불확실성

### 주목할 트렌드
- 생성형 AI 발전과 응용
- 엣지 컴퓨팅 확산
- 친환경 기술 투자 증가
"""

# 리포트 저장
with open('detailed_tech_analysis_kr.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("분석 완료! 차트 이미지와 상세 분석 리포트가 생성되었습니다.")
