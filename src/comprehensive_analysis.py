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

# 데이터 전처리 및 DataFrame 생성
df = pd.DataFrame.from_dict(data, orient='index')

# 주요 재무 지표 정리
financial_metrics = pd.DataFrame(index=df.index)
financial_metrics['시가총액'] = df['Market Cap'].apply(clean_numeric)
financial_metrics['매출액'] = df['Revenue  (ttm)'].apply(clean_numeric)
financial_metrics['영업이익률'] = df['Operating Margin  (ttm)'].apply(lambda x: clean_numeric(x.replace('%', '')))
financial_metrics['순이익률'] = df['Profit Margin'].apply(lambda x: clean_numeric(x.replace('%', '')))
financial_metrics['ROE'] = df['Return on Equity  (ttm)'].apply(lambda x: clean_numeric(x.replace('%', '')))
financial_metrics['현금성자산'] = df['Total Cash  (mrq)'].apply(clean_numeric)
financial_metrics['부채'] = df['Total Debt  (mrq)'].apply(clean_numeric)
financial_metrics['PER'] = df['Trailing P/E'].apply(clean_numeric)
financial_metrics['매출성장률'] = df['Quarterly Revenue Growth  (yoy)'].apply(lambda x: clean_numeric(x.replace('%', '')))

# 1. 종합 재무 분석 차트
plt.figure(figsize=(15, 10))
plt.subplot(2, 2, 1)
sns.barplot(x=financial_metrics.index, y=financial_metrics['시가총액']/1e12)
plt.title('시가총액 (조 달러)')
plt.xticks(rotation=45)

plt.subplot(2, 2, 2)
sns.barplot(x=financial_metrics.index, y=financial_metrics['매출성장률'])
plt.title('매출 성장률 (%)')
plt.xticks(rotation=45)

plt.subplot(2, 2, 3)
sns.barplot(x=financial_metrics.index, y=financial_metrics['영업이익률'])
plt.title('영업이익률 (%)')
plt.xticks(rotation=45)

plt.subplot(2, 2, 4)
sns.barplot(x=financial_metrics.index, y=financial_metrics['ROE'])
plt.title('자기자본이익률 (%)')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('comprehensive_financial_analysis.png')
plt.close()

# 2. 효율성 및 수익성 분석
plt.figure(figsize=(15, 5))
x = np.arange(len(financial_metrics.index))
width = 0.35

plt.bar(x - width/2, financial_metrics['영업이익률'], width, label='영업이익률')
plt.bar(x + width/2, financial_metrics['순이익률'], width, label='순이익률')
plt.title('수익성 지표 비교')
plt.xticks(x, financial_metrics.index, rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('profitability_analysis.png')
plt.close()

# 3. 밸류에이션 분석
plt.figure(figsize=(15, 5))
plt.bar(financial_metrics.index, financial_metrics['PER'])
plt.title('PER (주가수익비율) 비교')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('valuation_analysis.png')
plt.close()

# 4. 재무안정성 분석
plt.figure(figsize=(15, 5))
x = np.arange(len(financial_metrics.index))
width = 0.35

plt.bar(x - width/2, financial_metrics['현금성자산']/1e9, width, label='현금성자산')
plt.bar(x + width/2, financial_metrics['부채']/1e9, width, label='부채')
plt.title('재무안정성 지표 (십억 달러)')
plt.xticks(x, financial_metrics.index, rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('financial_stability.png')
plt.close()

# 상세 분석 리포트 생성
report = f"""# 빅테크 기업 종합 재무 분석 리포트 ({datetime.now().strftime('%Y-%m-%d')})

## 1. 기업 가치 및 시장 지위

### 시가총액 순위 (조 달러)
{(financial_metrics['시가총액']/1e12).round(2).to_string()}

### 시장 지배력 분석
- 상위 5개사 총 시가총액: ${(financial_metrics['시가총액'].sum()/1e12):.2f}조
- 시가총액 1위 대비 격차 (%)
{((1 - financial_metrics['시가총액']/financial_metrics['시가총액'].max()) * 100).round(2).to_string()}

## 2. 성장성 분석

### 매출 성장률 (전년 대비, %)
{financial_metrics['매출성장률'].round(2).to_string()}

### 매출액 규모 (십억 달러)
{(financial_metrics['매출액']/1e9).round(2).to_string()}

### 1인당 매출액 분석
{(df['Revenue Per Share  (ttm)'].astype(float)).round(2).to_string()}

## 3. 수익성 분석

### 영업이익률 (%)
{financial_metrics['영업이익률'].round(2).to_string()}

### 순이익률 (%)
{financial_metrics['순이익률'].round(2).to_string()}

### 자기자본이익률 (ROE, %)
{financial_metrics['ROE'].round(2).to_string()}

## 4. 재무안정성 분석

### 현금성자산 (십억 달러)
{(financial_metrics['현금성자산']/1e9).round(2).to_string()}

### 부채 현황 (십억 달러)
{(financial_metrics['부채']/1e9).round(2).to_string()}

### 부채비율 (%)
{((financial_metrics['부채']/financial_metrics['시가총액'])*100).round(2).to_string()}

## 5. 투자 가치 분석

### PER (주가수익비율)
{financial_metrics['PER'].round(2).to_string()}

### 매출액 대비 시가총액 비율
{(financial_metrics['시가총액']/financial_metrics['매출액']).round(2).to_string()}

## 6. 기업별 종합 분석

### Apple (AAPL)
- **강점**:
  * 최대 시가총액 보유로 시장 지배력 확보
  * 높은 영업이익률과 ROE
  * 안정적인 현금흐름
- **약점**:
  * 상대적으로 높은 PER
  * 매출 성장률 둔화
- **기회**:
  * 서비스 부문 성장
  * 신규 제품 카테고리 확장
- **위협**:
  * 공급망 리스크
  * 규제 강화 가능성

### Microsoft (MSFT)
- **강점**:
  * 높은 영업이익률
  * 안정적인 구독 수익 모델
  * 클라우드 시장 선도
- **약점**:
  * 높은 밸류에이션
  * 기업 시장 의존도
- **기회**:
  * AI 시장 선점
  * 기업용 소프트웨어 시장 확대
- **위협**:
  * 클라우드 경쟁 심화
  * 사이버보안 리스크

### Alphabet (GOOGL)
- **강점**:
  * 검색 시장 독점적 지위
  * 높은 현금보유량
  * 합리적인 밸류에이션
- **약점**:
  * 광고 수익 의존도
  * 클라우드 시장 점유율
- **기회**:
  * AI 기술 리더십
  * 유튜브 수익화 확대
- **위협**:
  * 개인정보 규제
  * 광고 시장 변화

### NVIDIA (NVDA)
- **강점**:
  * AI 칩 시장 지배력
  * 높은 수익성
  * 강력한 기술력
- **약점**:
  * 높은 밸류에이션
  * 수요 변동성
- **기회**:
  * AI 시장 확대
  * 데이터센터 수요 증가
- **위협**:
  * 경쟁사 추격
  * 반도체 사이클

### Meta (META)
- **강점**:
  * 소셜 미디어 지배력
  * 효율적인 비용 구조
  * 합리적인 밸류에이션
- **약점**:
  * 광고 수익 의존도
  * 메타버스 투자 부담
- **기회**:
  * AI 광고 최적화
  * 신규 수익원 발굴
- **위협**:
  * 프라이버시 규제
  * 젊은 층 이탈

## 7. 산업 동향 및 전망

### 주요 성장 동력
1. **AI/머신러닝**
   - 기업용 AI 솔루션 수요 증가
   - 생성형 AI 응용 확대
   - AI 인프라 투자 확대

2. **클라우드 컴퓨팅**
   - 하이브리드/멀티클라우드 도입 가속화
   - 엣지 컴퓨팅 성장
   - 보안 솔루션 수요 증가

3. **디지털 전환**
   - 기업의 디지털화 가속
   - 원격 근무 인프라 고도화
   - 데이터 분석 수요 증가

### 주요 리스크 요인
1. **거시경제 리스크**
   - 금리 정책 영향
   - 인플레이션 압박
   - 경기 침체 가능성

2. **규제 리스크**
   - 반독점 규제 강화
   - 데이터 보호 규제
   - AI 규제 도입

3. **기술 리스크**
   - 사이버보안 위협
   - 기술 변화 속도
   - 인재 확보 경쟁

## 8. 투자 전략 제언

### 단기 전략 (6개월-1년)
1. **포트폴리오 구성**
   - AI 인프라 기업 비중 확대
   - 밸류에이션 부담 기업 비중 조절
   - 현금흐름 우량 기업 선별

2. **리스크 관리**
   - 섹터별 분산 투자
   - 변동성 대비 현금 비중 조절
   - 실적 모멘텀 모니터링

### 중장기 전략 (2-3년)
1. **핵심 투자 테마**
   - AI/클라우드 인프라
   - 디지털 전환 수혜주
   - 기술 혁신 선도기업

2. **포트폴리오 관리**
   - 정기적인 리밸런싱
   - 기술 트렌드 대응
   - 규제 리스크 관리

## 9. 결론 및 시사점

### 투자 기회
- AI, 클라우드, 디지털 전환 관련 장기 성장성 유지
- 기술 혁신 통한 신규 시장 창출 지속
- 현금흐름 기반 안정적 성장 가능성

### 주의사항
- 고평가 리스크 상존
- 규제 환경 변화 대응 필요
- 경쟁 심화에 따른 수익성 관리 중요

### 모니터링 포인트
- 실적 모멘텀 변화
- 규제 동향
- 신기술 투자 현황
- 현금흐름 및 재무건전성
"""

# 리포트 저장
with open('comprehensive_tech_analysis_kr.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("종합 분석 완료! 차트 이미지와 상세 분석 리포트가 생성되었습니다.")
