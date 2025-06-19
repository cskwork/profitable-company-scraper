import time

import pytest
import requests
from playwright.sync_api import sync_playwright

# E2E 테스트: 검색, 상세 분석, 멀티 비교, 차트/표/다운로드 버튼 노출 등


def wait_for_server(url="http://localhost:5000/api/search?query=test", timeout=10):
    """서버가 준비될 때까지 대기"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


@pytest.mark.e2e
def test_ui_e2e():
    """회사 검색/분석/비교 UI E2E 테스트"""
    # 서버 준비 확인
    if not wait_for_server():
        pytest.skip("서버가 실행되지 않아 E2E 테스트를 건너뜁니다")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 로컬 서버가 5000번 포트에서 실행 중이라고 가정
            page.goto("http://localhost:5000/docs/index.html")

            # 페이지 로드 대기
            page.wait_for_load_state("networkidle")

            # 검색어 입력 및 검색
            search_input = page.locator(
                'input[placeholder="예: Apple, 삼성전자, AAPL"]'
            )
            search_input.fill("Apple")

            search_button = page.locator('button:has-text("검색")')
            search_button.click()

            # 검색 결과 대기
            page.wait_for_selector(".card", timeout=10000)
            assert page.locator(".card").count() > 0, "검색 결과가 없습니다"

            # 첫 번째 기업 상세 분석
            analyze_button = page.locator('.card button:has-text("상세 분석")').first
            analyze_button.click()

            # 차트 로드 대기
            page.wait_for_selector("#stock-history-chart", timeout=10000)
            assert page.locator(
                "#stock-history-chart"
            ).is_visible(), "주가 차트가 표시되지 않습니다"

            # 테이블 확인
            assert page.locator(
                ".table"
            ).is_visible(), "데이터 테이블이 표시되지 않습니다"

            # CSV 다운로드 버튼 확인
            assert page.locator(
                'button:has-text("CSV 다운로드")'
            ).is_visible(), "CSV 다운로드 버튼이 없습니다"

            # 멀티 비교 테스트
            # 다시 검색하여 여러 결과 얻기
            search_input.fill("Tech")
            search_button.click()
            page.wait_for_selector(".card", timeout=10000)

            # 체크박스 선택
            checkboxes = page.locator('input[type="checkbox"]')
            count = checkboxes.count()

            if count >= 2:
                # 2개 이상 체크
                checkboxes.nth(0).check()
                checkboxes.nth(1).check()

                # 비교하기 버튼 클릭
                compare_button = page.locator('button:has-text("비교하기")')
                compare_button.click()

                # 비교 차트 대기
                page.wait_for_selector("#multi-bar-chart", timeout=10000)
                assert page.locator(
                    "#multi-bar-chart"
                ).is_visible(), "비교 차트가 표시되지 않습니다"

                # 비교 테이블 확인
                assert (
                    page.locator(".table").count() >= 2
                ), "비교 테이블이 표시되지 않습니다"

            print("✅ E2E 테스트 성공!")

        except Exception as e:
            print(f"❌ E2E 테스트 실패: {e}")
            # 스크린샷 저장 (디버깅용)
            page.screenshot(path="e2e_test_failure.png")
            raise

        finally:
            browser.close()


if __name__ == "__main__":
    # 직접 실행 시
    test_ui_e2e()
