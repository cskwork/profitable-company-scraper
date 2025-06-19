@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Profitable Company Scraper - 전체 설정 및 실행   ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo 이 스크립트는 다음 작업을 자동으로 수행합니다:
echo   1. 가상환경 생성 및 패키지 설치
echo   2. 코드 품질 검사
echo   3. 테스트 실행
echo   4. 서버 시작
echo.
echo 계속하시겠습니까? (Y/N)
set /p confirm=선택: 
if /i not "%confirm%"=="Y" (
    echo 취소되었습니다.
    exit /b 0
)

echo.
echo ════════════════════════════════════════════════════
echo 📦 STEP 1: 설치 프로세스
echo ════════════════════════════════════════════════════
call install.bat
if errorlevel 1 (
    echo ❌ 설치 실패!
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════
echo 🎨 STEP 2: 코드 품질 자동 수정
echo ════════════════════════════════════════════════════
call .venv\Scripts\activate.bat

echo Black 포맷팅 적용 중...
black .
echo ✅ 포맷팅 완료

echo Import 정렬 중...
isort .
echo ✅ Import 정렬 완료

echo.
echo ════════════════════════════════════════════════════
echo 🧪 STEP 3: 테스트 실행
echo ════════════════════════════════════════════════════
echo 단위 테스트 실행 중...
pytest tests/unit/ -v --tb=short
if errorlevel 1 (
    echo ⚠️  일부 단위 테스트 실패
)

echo.
echo 통합 테스트 실행 중...
pytest tests/integration/ -v --tb=short
if errorlevel 1 (
    echo ⚠️  일부 통합 테스트 실패
)

echo.
echo ════════════════════════════════════════════════════
echo 🚀 STEP 4: 서버 시작
echo ════════════════════════════════════════════════════
echo.
echo 모든 설정이 완료되었습니다!
echo 이제 서버를 시작합니다...
echo.
timeout /t 3 /nobreak > nul

:: 서버 실행
call run.bat 