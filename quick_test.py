"""
빠른 기능 테스트 스크립트
"""

import sys

import requests


def check_virtual_env():
    """가상환경이 활성화되어 있는지 확인"""
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  경고: 가상환경이 활성화되어 있지 않습니다!")
        print("👉 test.bat을 사용하거나 가상환경을 활성화 후 실행하세요.")
        sys.exit(1)


def test_api():
    """API 엔드포인트 테스트"""
    base_url = "http://localhost:5000"

    print("🔍 API 테스트 시작...\n")

    # 1. 서버 상태 확인
    print("1️⃣ 서버 상태 확인...")
    try:
        response = requests.get(f"{base_url}/api/search?query=test", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 정상 작동 중입니다.\n")
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}\n")
            return
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}\n")
        print("💡 서버를 먼저 실행하세요: python run_server.py")
        return

    # 2. 회사 검색 테스트
    print("2️⃣ 회사 검색 테스트 (Apple)...")
    response = requests.get(f"{base_url}/api/search?query=Apple&lang=ko")
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            print(f"✅ 검색 성공: {len(data['data'])}개 결과")
            for company in data["data"][:3]:
                print(f"   - {company.get('symbol')}: {company.get('name')}")
        else:
            print("⚠️ 검색 결과가 없습니다.")
    else:
        print(f"❌ 검색 실패: {response.status_code}")
    print()

    # 3. 회사 분석 테스트
    print("3️⃣ 회사 분석 테스트 (AAPL)...")
    response = requests.get(f"{base_url}/api/analyze/AAPL?lang=ko&period=1mo")
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            analysis = data["data"]
            print("✅ 분석 성공:")
            print(f"   - 시가총액: {analysis.get('Market Cap', 'N/A')}")
            print(f"   - 이익률: {analysis.get('Profit Margin', 'N/A')}")
            print(f"   - PER: {analysis.get('Trailing P/E', 'N/A')}")
            print(f"   - 주가 변동: {analysis.get('Price Change', 'N/A')}")

            history = analysis.get("Stock History", [])
            if history:
                print(f"   - 주가 히스토리: {len(history)}개 데이터 포인트")
        else:
            print("⚠️ 분석 데이터가 없습니다.")
    else:
        print(f"❌ 분석 실패: {response.status_code}")
    print()

    # 4. 멀티 기업 비교 테스트
    print("4️⃣ 멀티 기업 비교 테스트 (AAPL, MSFT, GOOGL)...")
    payload = {"symbols": ["AAPL", "MSFT", "GOOGL"], "period": "1mo"}
    response = requests.post(
        f"{base_url}/api/analyze-multi",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            print(f"✅ 비교 분석 성공: {len(data['data'])}개 기업")
            for company in data["data"]:
                print(
                    f"   - {company.get('symbol')}: "
                    f"시가총액 {company.get('Market Cap', 'N/A')}, "
                    f"PER {company.get('Trailing P/E', 'N/A')}"
                )
        else:
            print("⚠️ 비교 데이터가 없습니다.")
    else:
        print(f"❌ 비교 분석 실패: {response.status_code}")
    print()

    # 5. UI 접근성 테스트
    print("5️⃣ 웹 UI 접근성 테스트...")
    response = requests.get(f"{base_url}/docs/index.html")
    if response.status_code == 200:
        print("✅ 웹 UI 접근 가능")
        print(f"   🌐 브라우저에서 열기: {base_url}/docs/index.html")
    else:
        print(f"❌ 웹 UI 접근 실패: {response.status_code}")

    # 6. Swagger API 문서 테스트
    print("\n6️⃣ API 문서 접근성 테스트...")
    response = requests.get(f"{base_url}/apidocs")
    if response.status_code == 200:
        print("✅ Swagger API 문서 접근 가능")
        print(f"   📚 브라우저에서 열기: {base_url}/apidocs")
    else:
        print(f"❌ API 문서 접근 실패: {response.status_code}")

    print("\n✨ 테스트 완료!")


if __name__ == "__main__":
    check_virtual_env()
    test_api()
