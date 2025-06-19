import pytest
from playwright.sync_api import sync_playwright

# E2E 테스트: 검색, 상세 분석, 멀티 비교, 차트/표/다운로드 버튼 노출 등


@pytest.mark.skip(reason="E2E tests require a running server, which is not set up yet.")
def test_ui_e2e():
    """회사 검색/분석/비교 UI E2E 테스트"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # 로컬 서버가 5000번 포트에서 실행 중이라고 가정
        page.goto("http://localhost:5000/docs/index.html")

        # 검색어 입력 및 검색
        page.fill('input[placeholder="예: Apple, 삼성전자, AAPL"]', "Apple")
        page.click('button:has-text("검색")')
        page.wait_for_selector(".card", timeout=5000)
        assert page.locator(".card").count() > 0

        # 첫 번째 기업 상세 분석
        page.click('.card button:has-text("상세 분석")')
        page.wait_for_selector("#stock-history-chart", timeout=5000)
        assert page.locator("#stock-history-chart").is_visible()
        assert page.locator(".table").is_visible()
        assert page.locator('button:has-text("CSV 다운로드")').is_visible()

        # 멀티 비교: 2개 이상 체크 후 비교하기
        checkboxes = page.locator('input[type="checkbox"]')
        count = checkboxes.count()
        assert count >= 2
        checkboxes.nth(0).check()
        checkboxes.nth(1).check()
        page.click('button:has-text("비교하기")')
        page.wait_for_selector("#multi-bar-chart", timeout=5000)
        assert page.locator("#multi-bar-chart").is_visible()
        assert page.locator(".table").is_visible()
        assert page.locator('button:has-text("CSV 다운로드")').is_visible()

        browser.close()
