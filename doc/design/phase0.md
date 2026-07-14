# Phase 0: 캐릭터라이제이션 테스트 작성 (리팩토링 전 안전망)

## 목적

리팩토링 전체에 걸쳐 "동작이 바뀌지 않았다"를 사람의 눈이 아니라 자동화된 테스트로 확인하기 위해, 원본 assembly.py를 실제로 서브프로세스 실행해 표준입력을 흘려보내고 표준출력을 검증하는 캐릭터라이제이션(characterization) 테스트를 가장 먼저 작성한다. TDD(레거시 코드에 대한 TDD는 "새 기능의 red-green"이 아니라 "기존 동작을 고정하는 green -> 리팩토링 -> green" 형태를 취한다 - Michael Feathers의 characterization test 기법)를 적용하기 위한 전제 조건.

이 테스트가 있어야, Phase 1부터 시작하는 "부품 클래스를 만들자마자 assembly.py에 바로 연결"하는 점진적(strangler-fig) 통합이 각 단계마다 회귀 없이 안전하게 진행되었는지 자동으로 확인할 수 있다.

## 사전 조건

없음. 반드시 Phase 1의 assembly.py 통합 작업보다 먼저 진행한다.

## 구현 절차

### 태스크 0.1: 캐릭터라이제이션 테스트 작성

1. Test 작성 - `tests/test_assembly_characterization.py` 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
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
   ```

2. 실행: `pytest tests/test_assembly_characterization.py -v`
   기대 결과: 이 시점에는 assembly.py가 아직 원본 그대로이므로 **16개 전부 PASS**해야 한다(이 Phase는 "실패를 먼저 확인"하는 일반 TDD와 다르다 - 이미 존재하는 원본 동작을 고정하는 것이 목적이므로, 처음부터 전부 PASS가 나와야 정상이다). 만약 하나라도 실패하면 테스트 코드가 원본 assembly.py의 실제 동작과 다르게 작성된 것이므로, 테스트를 원본 동작에 맞게 고친다(assembly.py를 고치지 않는다).

3. 커밋:
   ```bash
   git add tests/test_assembly_characterization.py
   git commit -m "test: add characterization test suite capturing original assembly.py behavior"
   ```

## 이 Phase가 끝나면 존재해야 하는 것

- `tests/test_assembly_characterization.py` - 16개 테스트, 전부 원본 assembly.py 기준으로 PASS
- git 커밋 1개

## 이후 Phase에서 이 안전망을 사용하는 방법 (모든 Phase 공통 규칙)

Phase 1부터는 car_assembly에 부품/로직을 추가하는 즉시 assembly.py를 해당 부분만 교체(통합)한다. assembly.py를 수정하는 모든 통합 스텝은 다음 순서를 따른다:

1. (통합 전) `pytest tests/test_assembly_characterization.py -v` 실행 -> 16개 전부 PASS(초록) 확인 - 지금부터 만들 변경의 출발점이 안전한 상태임을 확인
2. assembly.py의 해당 함수만 최소 범위로 교체
3. (통합 후) `pytest tests/test_assembly_characterization.py -v` 다시 실행 -> 여전히 16개 전부 PASS(초록) 확인 - 동작이 하나도 바뀌지 않았음을 자동으로 검증
4. 실패하는 테스트가 있으면 assembly.py 수정을 되돌리고 원인을 파악한다(테스트를 고치는 것이 아니라 코드를 고친다 - 이 테스트는 "지금 동작"이 아니라 "원본 동작"을 고정하는 것이 목적이기 때문)
5. 커밋 (car_assembly 쪽 새 코드 커밋과는 별도의 커밋으로, "assembly.py 통합" 전용 커밋 메시지를 사용)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] 16개 테스트가 PRD.md의 5개 호환성 규칙, 고장난 엔진 quirk, 뒤로가기 네비게이션, 범위 오류 메시지, 종료를 모두 커버하는지 확인
- [ ] `pytest tests/test_assembly_characterization.py -v` 실행 결과 16개 전부 PASS (원본 assembly.py 기준)
- [ ] 이 시점에 car_assembly 패키지나 assembly.py에 어떤 수정도 하지 않았는지 확인(순수하게 테스트 파일만 추가됨)
