@echo off
chcp 65001 > nul
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║   Profitable Company Scraper - 서버 실행           ║
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

:: 서버 실행
echo 🚀 Flask 서버를 시작합니다...
echo ════════════════════════════════════════════════════
echo.
echo 📍 접속 주소:
echo   - 웹 UI: http://localhost:5000/docs/index.html
echo   - API 문서: http://localhost:5000/apidocs
echo.
echo 💡 서버를 종료하려면 Ctrl+C를 누르세요.
echo ════════════════════════════════════════════════════
echo.

:: 서버 실행 (가상환경 내에서)
python run_server.py

:: 서버 종료 후 메시지
echo.
echo 서버가 종료되었습니다.
pause 