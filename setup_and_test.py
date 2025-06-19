"""
프로젝트 설정 및 테스트 자동화 스크립트
"""

import subprocess
import sys
import time
from pathlib import Path

import requests


def print_status(message, status="INFO"):
    """상태 메시지 출력"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')}[{status}] {message}{reset}")


def run_command(command, description, check=True):
    """명령 실행 및 결과 반환"""
    print_status(f"{description}...", "INFO")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=check
        )
        if result.returncode == 0:
            print_status(f"{description} 완료", "SUCCESS")
        return result
    except subprocess.CalledProcessError as e:
        print_status(f"{description} 실패: {e}", "ERROR")
        if check:
            raise
        return e


def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status("Python 3.8 이상이 필요합니다", "ERROR")
        sys.exit(1)
    print_status(f"Python {version.major}.{version.minor} 확인", "SUCCESS")


def setup_virtual_env():
    """가상환경 설정"""
    if not Path(".venv").exists():
        run_command("python -m venv .venv", "가상환경 생성")

    # 가상환경 활성화 명령 (OS별)
    if sys.platform == "win32":
        activate_cmd = ".venv\\Scripts\\activate"
    else:
        activate_cmd = "source .venv/bin/activate"

    print_status(f"가상환경 활성화: {activate_cmd}", "INFO")


def install_dependencies():
    """의존성 설치"""
    run_command("pip install --upgrade pip", "pip 업그레이드")
    run_command("pip install -r requirements.txt", "프로덕션 의존성 설치")
    run_command("pip install -r requirements-dev.txt", "개발 의존성 설치")


def run_code_quality_checks():
    """코드 품질 검사"""
    print_status("코드 품질 검사 시작", "INFO")

    # Black 포맷팅
    run_command("black . --check", "Black 포맷 검사", check=False)

    # isort 정렬
    run_command("isort . --check-only", "Import 정렬 검사", check=False)

    # Flake8 린팅
    run_command(
        "flake8 . --exclude=.venv,archive --max-line-length=88",
        "Flake8 린팅",
        check=False,
    )


def run_tests():
    """테스트 실행"""
    print_status("테스트 실행", "INFO")

    # 단위 테스트
    run_command("pytest tests/unit/ -v", "단위 테스트")

    # 통합 테스트
    run_command("pytest tests/integration/ -v", "통합 테스트")

    # 커버리지 리포트
    run_command(
        "pytest --cov=api --cov-report=html --cov-report=term", "테스트 커버리지 생성"
    )


def start_server():
    """서버 시작 (백그라운드)"""
    print_status("Flask 서버 시작", "INFO")

    # 서버 프로세스 시작
    if sys.platform == "win32":
        subprocess.Popen(
            ["python", "api/index.py"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        subprocess.Popen(["python", "api/index.py"])

    # 서버 시작 대기
    time.sleep(3)

    # 서버 상태 확인
    try:
        response = requests.get("http://localhost:5000/api/search?query=test")
        if response.status_code == 200:
            print_status("서버 정상 작동 확인", "SUCCESS")
            return True
    except Exception:
        pass

    print_status("서버 시작 실패", "WARNING")
    return False


def run_e2e_tests():
    """E2E 테스트 실행"""
    if not start_server():
        print_status("E2E 테스트 건너뜀 (서버 시작 실패)", "WARNING")
        return

    print_status("E2E 테스트 실행", "INFO")

    # Playwright 설치
    run_command("playwright install chromium", "Playwright 브라우저 설치")

    # E2E 테스트 실행
    run_command("pytest tests/e2e/ -v", "E2E 테스트", check=False)


def generate_report():
    """최종 리포트 생성"""
    print_status("프로젝트 상태 리포트", "INFO")

    # 파일 통계
    py_files = len(list(Path(".").rglob("*.py")))
    js_files = len(list(Path(".").rglob("*.js")))
    test_files = len(list(Path("tests").rglob("test_*.py")))

    print("\n📊 프로젝트 통계:")
    print(f"  - Python 파일: {py_files}개")
    print(f"  - JavaScript 파일: {js_files}개")
    print(f"  - 테스트 파일: {test_files}개")

    # 커버리지 확인
    if Path("htmlcov/index.html").exists():
        print("\n📈 테스트 커버리지 리포트: htmlcov/index.html")

    print("\n✅ 프로젝트 설정 및 테스트 완료!")


def main():
    """메인 실행 함수"""
    print_status("프로젝트 설정 및 테스트 시작", "INFO")

    try:
        check_python_version()
        setup_virtual_env()
        install_dependencies()
        run_code_quality_checks()
        run_tests()
        # run_e2e_tests()  # 선택적
        generate_report()

    except Exception as e:
        print_status(f"오류 발생: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
