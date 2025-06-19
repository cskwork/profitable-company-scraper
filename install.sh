#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   Profitable Company Scraper - 설치 프로그램       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Python 버전 확인
echo "[1/5] Python 버전 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되어 있지 않습니다!"
    echo "👉 https://www.python.org/downloads/ 에서 Python을 설치하세요."
    exit 1
fi
python3 --version
echo "✅ Python 확인 완료"
echo ""

# 가상환경 확인 및 생성
echo "[2/5] 가상환경 확인 중..."
if [ -d ".venv" ]; then
    echo "⚠️  기존 가상환경이 존재합니다. 삭제하고 새로 생성하시겠습니까? (y/n)"
    read -r choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        echo "기존 가상환경 삭제 중..."
        rm -rf .venv
    else
        echo "기존 가상환경을 사용합니다."
    fi
fi

if [ ! -d ".venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ 가상환경 생성 실패!"
        exit 1
    fi
    echo "✅ 가상환경 생성 완료"
fi
echo ""

# 가상환경 활성화
echo "[3/5] 가상환경 활성화 중..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화 실패!"
    exit 1
fi
echo "✅ 가상환경 활성화 완료"
echo ""

# pip 업그레이드
echo "[4/5] pip 업그레이드 중..."
python -m pip install --upgrade pip
echo "✅ pip 업그레이드 완료"
echo ""

# 의존성 설치
echo "[5/5] 의존성 패키지 설치 중..."
echo ""
echo "📦 프로덕션 패키지 설치 중..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 프로덕션 패키지 설치 실패!"
    exit 1
fi
echo ""
echo "📦 개발 패키지 설치 중..."
pip install -r requirements-dev.txt
if [ $? -ne 0 ]; then
    echo "⚠️  개발 패키지 설치 실패 (선택사항)"
fi
echo ""
echo "✅ 모든 패키지 설치 완료"
echo ""

# 설치 완료
echo "╔════════════════════════════════════════════════════╗"
echo "║              🎉 설치가 완료되었습니다! 🎉           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "다음 명령어로 서버를 실행할 수 있습니다:"
echo "  👉 ./run.sh"
echo ""
echo "또는 수동으로 실행:"
echo "  1. source .venv/bin/activate"
echo "  2. python run_server.py"
echo "" 