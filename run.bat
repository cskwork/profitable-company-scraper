@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Financial Research Agent - 실행기              ║
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

:: 사용자에게 Ticker 심볼 입력받기
set /p symbol="📈 분석할 회사의 Ticker 심볼을 입력하세요 (예: AAPL, MSFT): "

if not defined symbol (
    echo ❌ 심볼이 입력되지 않았습니다. 스크립트를 종료합니다.
    pause
    exit /b 1
)

:: Agent 실행
echo 🚀 Agent를 시작합니다...
echo ════════════════════════════════════════════════════
echo.

python agent/run.py %symbol%

echo.
echo ════════════════════════════════════════════════════
echo ✅ 분석이 완료되었습니다.
pause 