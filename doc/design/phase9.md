# Phase 9: CLI 이식 (문구/동작 100% 동일)

## 목적

원본 show_menu, is_valid_range, select_*, run_produced_car, test_produced_car, main, delay, clear를 car_assembly/cli.py로 옮긴다. 부품 선택/판정 로직은 전부 Phase 4~7의 클래스에 위임한다. 이 Phase가 끝나면 car_assembly.cli.main()이 원본 assembly.py의 main()과 100% 동일하게 동작해야 한다.

## 사전 조건

Phase 8(advance_step) 완료.

## 구현 절차

### 태스크 9.1: delay/clear 헬퍼

유닛테스트 없음(time.sleep/화면 클리어는 값 검증 대상이 아님).

구현 - car_assembly/cli.py 파일 맨 위(advance_step 함수보다 위)에 아래 내용을 추가:

```python
import sys
import time

CLEAR_SCREEN = "\033[H\033[2J"


def delay(ms):
    time.sleep(ms / 1000.0)


def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()
```

커밋: git commit -am "feat: add delay/clear helpers to cli.py"

### 태스크 9.2: car_type_selection_message (차량 타입은 클래스가 아니므로 별도 헬퍼)

1. Test 추가 - tests/test_cli_state.py 파일 끝에 추가:

   ```python
   from car_assembly.car_type import CarType
   from car_assembly.cli import car_type_selection_message


   def test_car_type_selection_message():
       assert car_type_selection_message(CarType.SEDAN) == "차량 타입으로 Sedan을 선택하셨습니다."
       assert car_type_selection_message(CarType.SUV) == "차량 타입으로 SUV을 선택하셨습니다."
       assert car_type_selection_message(CarType.TRUCK) == "차량 타입으로 Truck을 선택하셨습니다."
   ```

   주의: SUV 케이스는 "차량 타입으로 SUV를 선택하셨습니다."가 아니라 "차량 타입으로 SUV을 선택하셨습니다."이다(원본 문법 그대로, 조사가 "을"로 고정되어 있음). 절대 "를"로 바꾸지 말 것.

2. 실행: pytest tests/test_cli_state.py -v
   기대 결과: ImportError로 실패.

3. 구현 - car_assembly/cli.py 파일 맨 위(import 영역)에 추가:

   ```python
   from car_assembly.car_type import CAR_TYPE_LABEL, CarType
   ```

   그리고 advance_step 함수 위나 아래(파일 아무 곳이나, 단 다른 함수 정의와 섞이지 않게)에 아래 함수를 추가:

   ```python
   def car_type_selection_message(car_type: CarType) -> str:
       return f"차량 타입으로 {CAR_TYPE_LABEL[car_type]}을 선택하셨습니다."
   ```

4. 실행: pytest tests/test_cli_state.py -v -> PASS 확인
5. 커밋: git commit -am "feat: add car_type_selection_message helper"

### 태스크 9.3: show_menu 이식

유닛테스트 없음(화면 출력 전용, 검증은 Phase 11 수동 회귀에서 수행).

구현 - car_assembly/cli.py 파일 끝에 아래 내용을 원본 텍스트 그대로 추가한다. 이모지, 특수문자, 공백, 줄바꿈 위치까지 원본 assembly.py의 show_menu 함수와 정확히 동일해야 한다:

```python
STEP_CAR_TYPE = 0
STEP_ENGINE = 1
STEP_BRAKE = 2
STEP_STEERING = 3
STEP_RUN_TEST = 4


def show_menu(step):
    clear()
    if step == STEP_CAR_TYPE:
        print("        ______________")
        print("       /|            |")
        print("  ____/_|_____________|____")
        print(" |                      O  |")
        print(" '-(@)----------------(@)--'")
        print("===============================")
        print("어떤 차량 타입을 선택할까요?")
        print("1. Sedan")
        print("2. SUV")
        print("3. Truck")
    elif step == STEP_ENGINE:
        print("어떤 엔진을 탑재할까요?")
        print("0. 뒤로가기")
        print("1. GM")
        print("2. TOYOTA")
        print("3. WIA")
        print("4. 고장난 엔진")
    elif step == STEP_BRAKE:
        print("어떤 제동장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. MANDO")
        print("2. CONTINENTAL")
        print("3. BOSCH")
    elif step == STEP_STEERING:
        print("어떤 조향장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. BOSCH")
        print("2. MOBIS")
    elif step == STEP_RUN_TEST:
        print("멋진 차량이 완성되었습니다.")
        print("0. 처음 화면으로 돌아가기")
        print("1. RUN")
        print("2. Test")
    print("===============================")
```

커밋: git commit -am "feat: port show_menu to cli.py"

### 태스크 9.4: is_valid_range 이식

1. Test 추가 - tests/test_cli_state.py 파일 끝에 추가:

   ```python
   from car_assembly.cli import is_valid_range


   def test_is_valid_range_car_type_bounds():
       assert is_valid_range(0, 1) is True
       assert is_valid_range(0, 3) is True
       assert is_valid_range(0, 0) is False
       assert is_valid_range(0, 4) is False


   def test_is_valid_range_engine_bounds():
       assert is_valid_range(1, 0) is True
       assert is_valid_range(1, 4) is True
       assert is_valid_range(1, 5) is False
   ```

2. 실행: pytest tests/test_cli_state.py -v
   기대 결과: ImportError로 실패.

3. 구현 - car_assembly/cli.py 파일 끝에 아래 내용을 그대로 추가(원본 에러 메시지 문구 그대로):

   ```python
   def is_valid_range(step, ans):
       if step == STEP_CAR_TYPE and not (1 <= ans <= 3):
           print("ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능")
           return False
       if step == STEP_ENGINE and not (0 <= ans <= 4):
           print("ERROR :: 엔진은 1 ~ 4 범위만 선택 가능")
           return False
       if step == STEP_BRAKE and not (0 <= ans <= 3):
           print("ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능")
           return False
       if step == STEP_STEERING and not (0 <= ans <= 2):
           print("ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능")
           return False
       if step == STEP_RUN_TEST and not (0 <= ans <= 2):
           print("ERROR :: Run 또는 Test 중 하나를 선택 필요")
           return False
       return True
   ```

4. 실행: pytest tests/test_cli_state.py -v -> PASS 확인
5. 커밋: git commit -am "feat: port is_valid_range to cli.py"

### 태스크 9.5: main() 루프 조립 (통합)

유닛테스트 없음(입출력 통합 지점, 검증은 Phase 11 수동 회귀에서 수행).

구현 - car_assembly/cli.py 파일 맨 위 import 영역에 아래 두 줄을 추가:

```python
from car_assembly.car import CarBuild
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE
```

그리고 car_assembly/cli.py 파일 끝에 아래 내용을 그대로 추가:

```python
def main():
    step = STEP_CAR_TYPE
    build = CarBuild()

    while True:
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except ValueError:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == 0:
            step = advance_step(step, ans)
            continue

        if step == STEP_CAR_TYPE:
            build.car_type = CarType(ans)
            print(car_type_selection_message(build.car_type))
            delay(800)
        elif step == STEP_ENGINE:
            build.engine = ENGINE_BY_CODE[ans]()
            print(build.engine.selection_message())
            delay(800)
        elif step == STEP_BRAKE:
            build.brake = BRAKE_BY_CODE[ans]()
            print(build.brake.selection_message())
            delay(800)
        elif step == STEP_STEERING:
            build.steering = STEERING_BY_CODE[ans]()
            print(build.steering.selection_message())
            delay(800)
        elif step == STEP_RUN_TEST:
            if ans == 1:
                for line in build.run_report():
                    print(line)
                delay(2000)
            elif ans == 2:
                print("Test...")
                delay(1500)
                print(build.test_report())
                delay(2000)

        step = advance_step(step, ans)


if __name__ == "__main__":
    main()
```

실행: pytest -v (프로젝트 전체 테스트) -> 지금까지 작성된 테스트가 전부 PASS해야 한다(이 태스크는 새 테스트를 추가하지 않고, import 에러 없이 전체 스위트가 통과하는지만 확인하는 통합 단계).

커밋: git commit -am "feat: assemble main() loop in cli.py using part factories"

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/cli.py에 delay, clear, car_type_selection_message, STEP_* 상수, show_menu, is_valid_range, main 전부 포함(advance_step은 Phase 8에서 이미 있음)
- car_assembly/cli.py 안의 모든 문자열이 원본 assembly.py와 정확히 동일
- git 커밋 5개(누적 28개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] car_assembly/cli.py의 show_menu 출력 텍스트를 원본 assembly.py의 show_menu 함수와 한 줄씩 diff 비교해서 완전히 동일한지 확인
- [ ] is_valid_range의 5개 에러 메시지가 원본과 정확히 일치하는지 확인
- [ ] main()의 분기 구조(단계별 부품 생성 -> selection_message 출력 -> delay -> advance_step)가 원본 main()의 흐름과 논리적으로 동일한지 확인
- [ ] main()이 CarBuild, ENGINE_BY_CODE, BRAKE_BY_CODE, STEERING_BY_CODE, advance_step에만 위임하고 판정/문자열 조합 로직을 직접 갖고 있지 않은지 확인
- [ ] pytest -v (전체 스위트) 실행 결과 지금까지 작성된 모든 테스트가 PASS
- [ ] 이 시점에 원본 assembly.py는 아직 수정하지 않았는지 확인(Phase 10에서 교체)
