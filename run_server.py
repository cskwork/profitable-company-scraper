"""
Flask 서버 실행 스크립트
"""

import os
import sys

from dotenv import load_dotenv

from api.index import create_app


# 가상환경 확인
def check_virtual_env():
    """가상환경이 활성화되어 있는지 확인"""
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  경고: 가상환경이 활성화되어 있지 않습니다!")
        print("👉 권장사항: 다음 명령어로 가상환경을 활성화하세요:")
        if os.name == "nt":  # Windows
            print("   .venv\\Scripts\\activate")
        else:  # Linux/Mac
            print("   source .venv/bin/activate")
        print("\n또는 run.bat 파일을 실행하세요.")

        response = input("\n그래도 계속하시겠습니까? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)
    else:
        print("✅ 가상환경이 활성화되어 있습니다.")


# api 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Flask 앱 실행
if __name__ == "__main__":
    check_virtual_env()

    load_dotenv()

    app = create_app()

    print("\n🚀 Flask 서버를 시작합니다...")
    print("📍 접속 주소: http://localhost:5000")
    print("📍 API 문서: http://localhost:5000/apidocs")
    print("📍 웹 UI: http://localhost:5000/docs/index.html")
    print("\n종료하려면 Ctrl+C를 누르세요.")

    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
