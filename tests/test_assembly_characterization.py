"""리팩토링 중 assembly.py의 실제 콘솔 동작이 원본과 동일하게 유지되는지 검증하는
캐릭터라이제이션(characterization) 테스트. 실제 서브프로세스로 assembly.py를 실행해
표준입력을 흘려보내고 표준출력을 검사한다 - 리팩토링 각 단계마다 이 파일을 돌려
회귀가 없는지 확인한다."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_cli(inputs):
    stdin_text = "\n".join(inputs) + "\n"
    proc = subprocess.run(
        [sys.executable, "assembly.py"],
        input=stdin_text,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.stdout


def test_normal_run_sedan_gm_mando_mobis():
    output = run_cli(["1", "1", "1", "2", "1", "exit"])
    assert "Car Type : Sedan" in output
    assert "Engine   : GM" in output
    assert "Brake    : Mando" in output
    assert "Steering : Mobis" in output
    assert "자동차가 동작됩니다." in output


def test_run_incompatible_sedan_continental():
    output = run_cli(["1", "1", "2", "2", "1", "exit"])
    assert "자동차가 동작되지 않습니다" in output


def test_test_incompatible_sedan_continental_reports_fail():
    output = run_cli(["1", "1", "2", "2", "2", "exit"])
    assert "FAIL" in output
    assert "Sedan에는 Continental제동장치 사용 불가" in output


def test_test_suv_toyota_incompatible():
    output = run_cli(["2", "2", "1", "2", "2", "exit"])
    assert "FAIL" in output
    assert "SUV에는 TOYOTA엔진 사용 불가" in output


def test_test_truck_wia_incompatible():
    output = run_cli(["3", "3", "3", "2", "2", "exit"])
    assert "FAIL" in output
    assert "Truck에는 WIA엔진 사용 불가" in output


def test_test_truck_mando_incompatible():
    output = run_cli(["3", "1", "1", "2", "2", "exit"])
    assert "FAIL" in output
    assert "Truck에는 Mando제동장치 사용 불가" in output


def test_test_bosch_brake_requires_bosch_steering():
    output = run_cli(["1", "1", "3", "2", "2", "exit"])
    assert "FAIL" in output
    assert "Bosch제동장치에는 Bosch조향장치 이외 사용 불가" in output


def test_test_bosch_brake_with_bosch_steering_passes():
    output = run_cli(["1", "1", "3", "1", "2", "exit"])
    assert "PASS" in output


def test_run_broken_engine():
    output = run_cli(["1", "4", "1", "2", "1", "exit"])
    assert "엔진이 고장나있습니다." in output
    assert "자동차가 움직이지 않습니다." in output


def test_test_broken_engine_still_passes():
    # 원본 test_produced_car()는 엔진 고장 여부를 검사하지 않는다 - 동작 보존 대상 quirk
    output = run_cli(["1", "4", "1", "2", "2", "exit"])
    assert "PASS" in output


def test_back_navigation_returns_to_car_type_menu():
    output = run_cli(["1", "0", "exit"])
    assert output.count("어떤 차량 타입을 선택할까요?") == 2


def test_back_navigation_from_run_test_screen_returns_to_car_type_menu():
    output = run_cli(["1", "1", "1", "2", "0", "exit"])
    assert output.count("어떤 차량 타입을 선택할까요?") == 2


def test_invalid_car_type_range_shows_error():
    output = run_cli(["9", "1", "1", "1", "2", "1", "exit"])
    assert "ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능" in output


def test_invalid_engine_range_shows_error():
    output = run_cli(["1", "9", "1", "1", "2", "1", "exit"])
    assert "ERROR :: 엔진은 1 ~ 4 범위만 선택 가능" in output


def test_non_numeric_input_shows_error():
    output = run_cli(["abc", "1", "1", "1", "2", "1", "exit"])
    assert "ERROR :: 숫자만 입력 가능" in output


def test_exit_prints_goodbye():
    output = run_cli(["exit"])
    assert "바이바이" in output
