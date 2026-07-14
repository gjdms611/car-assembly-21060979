# Phase 9: 잔여 정리 (메뉴/상태를 car_assembly로 완전 이관)

## 목적

show_menu/is_valid_range를 car_assembly.cli로 옮기고, assembly.py에 남아있는 마지막 원본 구조인 전역 변수 q0~q4를 단일 CarBuild 객체로 통합한다. 이 Phase가 끝나면 assembly.py의 모든 함수가 이미 car_assembly에 위임하는 상태가 되어, Phase 10의 최종 슬림화가 거의 기계적인 작업이 된다.

## 사전 조건

Phase 8(advance_step + main 루프 통합) 완료. pytest tests/test_assembly_characterization.py -v 실행해 통합 전 전부 PASS 확인. 매 태스크마다 이 순서(통합 전 확인 -> 변경 -> 통합 후 확인 -> 커밋)를 반복한다.

## 구현 절차

### 태스크 9.1: show_menu 이관

1. 구현 - car_assembly/cli.py 파일 끝에 assembly.py의 show_menu 함수를 원본 텍스트 그대로 추가:

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

   이 함수가 clear()를 호출하므로, car_assembly/cli.py 파일 상단에 아래 delay/clear 헬퍼도 함께 추가한다(아직 없다면):

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

2. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
3. assembly.py에서 CLEAR_SCREEN 상수, delay(), clear(), show_menu() 함수 정의를 전부 삭제하고, 최상단 import 영역에 아래를 추가:

   ```python
   from car_assembly.cli import clear, delay, show_menu
   ```

   assembly.py의 import time, import sys는 delay/clear가 쓰던 유일한 코드이므로 함께 삭제한다.

4. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인
5. 커밋: git add assembly.py car_assembly/cli.py && git commit -m "Move show_menu/delay/clear into car_assembly.cli and delegate from assembly.py"

### 태스크 9.2: is_valid_range 이관

1. 구현 - car_assembly/cli.py 파일 끝에 추가:

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

2. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
3. assembly.py에서 is_valid_range() 함수 정의를 삭제하고, import 줄을 아래로 교체:

   ```python
   from car_assembly.cli import clear, delay, is_valid_range, show_menu
   ```

4. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인
5. 커밋: git add assembly.py car_assembly/cli.py && git commit -m "Move is_valid_range into car_assembly.cli and delegate from assembly.py"

### 태스크 9.3: car_type_selection_message 헬퍼로 통합

1. 구현 - car_assembly/cli.py 파일 상단에 추가:

   ```python
   from car_assembly.car_type import CAR_TYPE_LABEL, CarType
   ```

   파일 끝에 추가:

   ```python
   def car_type_selection_message(car_type: CarType) -> str:
       return f"차량 타입으로 {CAR_TYPE_LABEL[car_type]}을 선택하셨습니다."
   ```

2. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
3. assembly.py의 select_car_type()을 아래로 교체:

   ```python
   def select_car_type(a):
       global q0
       q0 = a
       print(car_type_selection_message(CarType(a)))
   ```

   import 줄을 아래로 교체:

   ```python
   from car_assembly.car_type import CAR_TYPE_LABEL, CarType
   from car_assembly.cli import car_type_selection_message, clear, delay, is_valid_range, show_menu
   ```

4. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인
5. 커밋: git add assembly.py car_assembly/cli.py && git commit -m "Move car_type_selection_message into car_assembly.cli and delegate from assembly.py"

### 태스크 9.4: 전역 상태(q0~q4)를 CarBuild 하나로 통합

1. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
2. assembly.py 상단의 아래 전역 변수 정의:

   ```python
   q0 = 0
   q1 = 0
   q2 = 0
   q3 = 0
   q4 = 0
   ```

   를 아래로 교체:

   ```python
   build = CarBuild()
   ```

3. select_car_type/select_engine/select_brake/select_steering을 각각 아래로 교체(global 대상이 q0~q3에서 build로 바뀐다):

   ```python
   def select_car_type(a):
       global build
       build.car_type = CarType(a)
       print(car_type_selection_message(build.car_type))

   def select_engine(a):
       global build
       build.engine = ENGINE_BY_CODE[a]()
       print(build.engine.selection_message())

   def select_brake(a):
       global build
       build.brake = BRAKE_BY_CODE[a]()
       print(build.brake.selection_message())

   def select_steering(a):
       global build
       build.steering = STEERING_BY_CODE[a]()
       print(build.steering.selection_message())
   ```

4. build_from_globals() 함수는 이제 필요 없다. build_from_globals() 정의를 삭제하고, run_produced_car/test_produced_car에서 build_from_globals()를 호출하던 부분을 전역 build를 직접 쓰도록 교체한다:

   ```python
   def run_produced_car():
       for line in build.run_report():
           print(line)

   def test_produced_car():
       print(build.test_report())
   ```

5. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인(특히 뒤로가기 후 재선택, RUN/TEST 반복 시나리오가 전역 객체 하나로도 원본과 동일하게 동작하는지 중요하게 확인)
6. 커밋: git add assembly.py && git commit -m "Consolidate q0-q4 globals into a single CarBuild instance in assembly.py"

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/cli.py - delay, clear, show_menu, is_valid_range, car_type_selection_message, advance_step 전부 포함(main()만 아직 없음 - Phase 10에서 추가)
- assembly.py - select_*/run_produced_car/test_produced_car/main()만 남고 나머지는 전부 car_assembly에서 import. 전역 상태는 build = CarBuild() 하나뿐
- git 커밋 4개

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] assembly.py에 더 이상 CLEAR_SCREEN, delay(), clear(), show_menu(), is_valid_range() 정의가 없는지 확인(전부 import로 대체)
- [ ] assembly.py에 q0~q4 전역 변수가 더 이상 없고 build = CarBuild() 하나만 있는지 확인
- [ ] select_* 함수들이 global build로 build의 필드에 직접 대입하는지 확인
- [ ] pytest tests/test_assembly_characterization.py -v 실행 결과 9.1~9.4 각 커밋 전후 모두 PASS(회귀 없음)
- [ ] python assembly.py를 직접 실행해 뒤로가기 후 다른 부품을 다시 선택했을 때도 정상 반영되는지(전역 객체 하나로 바뀌었어도 재선택이 이전 선택을 덮어쓰는지) 확인
