@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Profitable Company Scraper - 테스트 실행         ║
echo ╚════════════════════════════════════════════════════╝
echo.

:: 가상환경 확인
if not exist .venv (
    echo ❌ 가상환경이 존재하지 않습니다!
    echo 👉 먼저 install.bat을 실행하여 설치를 완료하세요.
    pause
    exit /b 1
)

:: 가상환경 활성화
echo 🔄 가상환경 활성화 중...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패!
    pause
    exit /b 1
)
echo ✅ 가상환경 활성화 완료
echo.

:: 테스트 옵션 선택
echo 실행할 테스트를 선택하세요:
echo ════════════════════════════════════════════════════
echo   1. 빠른 기능 테스트 (quick_test.py)
echo   2. 전체 테스트 (pytest)
echo   3. 단위 테스트만
echo   4. 통합 테스트만
echo   5. E2E 테스트만 (서버 실행 필요)
echo   6. 테스트 + 커버리지 리포트
echo   7. 코드 품질 검사 (Black, isort, Flake8)
echo ════════════════════════════════════════════════════
echo.
set /p choice=선택 (1-7): 

if "%choice%"=="1" goto :quick_test
if "%choice%"=="2" goto :all_tests
if "%choice%"=="3" goto :unit_tests
if "%choice%"=="4" goto :integration_tests
if "%choice%"=="5" goto :e2e_tests
if "%choice%"=="6" goto :coverage_tests
if "%choice%"=="7" goto :code_quality
echo ❌ 잘못된 선택입니다.
goto :end

:quick_test
echo.
echo 🔍 빠른 기능 테스트 실행 중...
echo ════════════════════════════════════════════════════
python quick_test.py
goto :end

:all_tests
echo.
echo 🧪 전체 테스트 실행 중...
echo ════════════════════════════════════════════════════
pytest -v
goto :end

:unit_tests
echo.
echo 🧪 단위 테스트 실행 중...
echo ════════════════════════════════════════════════════
pytest tests/unit/ -v
goto :end

:integration_tests
echo.
echo 🧪 통합 테스트 실행 중...
echo ════════════════════════════════════════════════════
pytest tests/integration/ -v
goto :end

:e2e_tests
echo.
echo 🧪 E2E 테스트 실행 중...
echo ⚠️  주의: 서버가 실행 중이어야 합니다!
echo ════════════════════════════════════════════════════
pytest tests/e2e/ -v
goto :end

:coverage_tests
echo.
echo 📊 테스트 커버리지 분석 중...
echo ════════════════════════════════════════════════════
pytest --cov=api --cov-report=html --cov-report=term
echo.
echo 📁 HTML 리포트: htmlcov/index.html
goto :end

:code_quality
echo.
echo 🎨 코드 품질 검사 중...
echo ════════════════════════════════════════════════════
echo.
echo [1/3] Black 포맷 검사...
black . --check
if errorlevel 1 (
    echo ⚠️  포맷팅이 필요합니다. 'black .'을 실행하세요.
)
echo.
echo [2/3] Import 정렬 검사...
isort . --check-only
if errorlevel 1 (
    echo ⚠️  Import 정렬이 필요합니다. 'isort .'을 실행하세요.
)
echo.
echo [3/3] Flake8 린팅...
flake8 . --exclude=.venv,archive --max-line-length=88
goto :end

:end
echo.
echo ════════════════════════════════════════════════════
echo 테스트가 완료되었습니다.
pause 