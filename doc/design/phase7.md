# Phase 7: CarBuild (조립 상태 + 리포트)

## 목적

부품 객체(엔진/제동장치/조향장치)들을 보관하는 CarBuild를 만든다. 판정(호환성 검사)과 출력(리포트 문자열 생성)은 전부 부품 객체(Phase 4~6)에 위임하고, CarBuild 자신은 어떤 규칙도 새로 알지 않는다.

## 사전 조건

Phase 6(SteeringPart 계열) 완료 - car_assembly/parts.py가 완성되어 있어야 함.

## 구현 절차

### 태스크 7.1: CarBuild 골격 + is_engine_broken()

1. Test 작성 - tests/test_car.py 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
   from car_assembly.car import CarBuild
   from car_assembly.car_type import CarType
   from car_assembly.parts import BrokenEngine, GMEngine, MandoBrake, MobisSteering


   def test_carbuild_holds_selections():
       build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
       assert build.car_type == CarType.SEDAN
       assert isinstance(build.engine, GMEngine)


   def test_carbuild_defaults_to_none():
       assert CarBuild().car_type is None


   def test_is_engine_broken_true():
       build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
       assert build.is_engine_broken() is True


   def test_is_engine_broken_false():
       build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
       assert build.is_engine_broken() is False
   ```

2. 실행: pytest tests/test_car.py -v
   기대 결과: ModuleNotFoundError로 실패.

3. 구현 - car_assembly/car.py 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
   from dataclasses import dataclass
   from typing import Optional

   from car_assembly.car_type import CAR_TYPE_LABEL, CarType
   from car_assembly.parts import BrakePart, EnginePart, SteeringPart


   @dataclass
   class CarBuild:
       car_type: Optional[CarType] = None
       engine: Optional[EnginePart] = None
       brake: Optional[BrakePart] = None
       steering: Optional[SteeringPart] = None

       def is_engine_broken(self) -> bool:
           return self.engine is not None and self.engine.is_broken
   ```

4. 실행: pytest tests/test_car.py -v -> 4개 테스트 모두 PASS
5. 커밋:
   git add car_assembly/car.py tests/test_car.py
   git commit -m "feat: add CarBuild skeleton holding part objects"

### 태스크 7.2: first_incompatibility() / is_compatible()

1. Test 추가 - tests/test_car.py 파일 상단 import 영역에 아래 줄을 추가:

   ```python
   from car_assembly.parts import BoschBrake, ContinentalBrake, MandoBrake, WIAEngine
   ```

   그리고 파일 끝에 아래 테스트를 추가:

   ```python
   def test_first_incompatibility_engine_checked_before_brake():
       build = CarBuild(CarType.TRUCK, WIAEngine(), MandoBrake(), MobisSteering())
       assert build.first_incompatibility() == "Truck에는 WIA엔진 사용 불가"


   def test_first_incompatibility_brake_car_type_rule():
       build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
       assert build.first_incompatibility() == "Sedan에는 Continental제동장치 사용 불가"


   def test_first_incompatibility_brake_steering_rule():
       build = CarBuild(CarType.SEDAN, GMEngine(), BoschBrake(), MobisSteering())
       assert build.first_incompatibility() == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


   def test_is_compatible_true_for_valid_build():
       build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
       assert build.is_compatible() is True


   def test_is_compatible_false_for_invalid_build():
       build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
       assert build.is_compatible() is False
   ```

   참고: 위 test_first_incompatibility_engine_checked_before_brake는 Truck + WIA(엔진 위반) + Mando(제동장치 위반)가 동시에 발생하는 케이스로, 원본과 동일하게 엔진 메시지가 우선해야 함을 검증한다.

2. 실행: pytest tests/test_car.py -v
   기대 결과: AttributeError로 실패.

3. 구현 - car_assembly/car.py의 CarBuild 클래스 안(is_engine_broken 메서드 아래)에 추가:

   ```python
       def first_incompatibility(self) -> Optional[str]:
           return (
               self.engine.incompatibility_with_car_type(self.car_type)
               or self.brake.incompatibility_with_car_type(self.car_type)
               or self.brake.incompatibility_with_steering(self.steering)
           )

       def is_compatible(self) -> bool:
           return self.first_incompatibility() is None
   ```

   중요: 세 가지 판정을 반드시 이 순서(엔진 -> 제동장치-차량타입 -> 제동장치-조향장치)로 or 체이닝해야 한다. 순서를 바꾸면 위 테스트가 실패한다.

4. 실행: pytest tests/test_car.py -v -> PASS 확인
5. 커밋: git commit -am "feat: add CarBuild.first_incompatibility delegating to part objects"

### 태스크 7.3: run_report()

1. Test 추가 - tests/test_car.py 파일 끝에 추가:

   ```python
   def test_run_report_incompatible():
       build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
       assert build.run_report() == ["자동차가 동작되지 않습니다"]


   def test_run_report_broken_engine():
       build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
       assert build.run_report() == ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]


   def test_run_report_success():
       build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
       assert build.run_report() == [
           "Car Type : Sedan",
           "Engine   : GM",
           "Brake    : Mando",
           "Steering : Mobis",
           "자동차가 동작됩니다.",
       ]
   ```

2. 실행: pytest tests/test_car.py -v
   기대 결과: AttributeError로 실패.

3. 구현 - car_assembly/car.py의 CarBuild 클래스 안에 추가:

   ```python
       def run_report(self) -> list[str]:
           if not self.is_compatible():
               return ["자동차가 동작되지 않습니다"]
           if self.is_engine_broken():
               return ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]

           lines = [f"Car Type : {CAR_TYPE_LABEL[self.car_type]}"]
           engine_label = self.engine.run_label()
           if engine_label is not None:
               lines.append(f"Engine   : {engine_label}")
           lines.append(f"Brake    : {self.brake.run_label()}")
           lines.append(f"Steering : {self.steering.run_label()}")
           lines.append("자동차가 동작됩니다.")
           return lines
   ```

   Engine   :, Brake    :, Steering : 각 줄의 공백 개수(콜론 앞 정렬)는 원본 assembly.py와 정확히 일치해야 한다. 위 코드를 그대로 복사해서 붙여넣을 것.

4. 실행: pytest tests/test_car.py -v -> PASS 확인
5. 커밋: git commit -am "feat: add CarBuild.run_report"

### 태스크 7.4: test_report()

1. Test 추가 - tests/test_car.py 파일 끝에 추가:

   ```python
   def test_test_report_fail():
       build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
       assert build.test_report() == "FAIL\nSedan에는 Continental제동장치 사용 불가"


   def test_test_report_pass():
       build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
       assert build.test_report() == "PASS"


   def test_test_report_pass_even_with_broken_engine():
       build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
       assert build.test_report() == "PASS"
   ```

   참고: test_test_report_pass_even_with_broken_engine은 원본 test_produced_car()가 엔진 고장 여부를 검사하지 않는다는 동작 보존 대상 quirk를 검증한다.

2. 구현 - car_assembly/car.py의 CarBuild 클래스 안에 추가:

   ```python
       def test_report(self) -> str:
           message = self.first_incompatibility()
           if message is None:
               return "PASS"
           return f"FAIL\n{message}"
   ```

3. 실행: pytest tests/test_car.py -v -> 전체 PASS 확인 (특히 test_test_report_pass_even_with_broken_engine이 PASS해야 함 - test_report()는 is_engine_broken()을 절대 호출하지 않는다는 뜻)
4. 커밋: git commit -am "feat: add CarBuild.test_report"

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/car.py - CarBuild 데이터클래스, 필드 4개 + 메서드 5개(is_engine_broken, first_incompatibility, is_compatible, run_report, test_report)
- tests/test_car.py - 위 테스트 전부(총 13개)
- git 커밋 4개(누적 20개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] first_incompatibility()가 엔진 -> 제동장치(차량타입) -> 제동장치(조향장치) 순서로 검사하는지 확인(순서를 바꾸면 Truck+WIA+Mando 동시 위반 케이스에서 원본과 다른 메시지가 나옴)
- [ ] run_report()의 5가지 케이스(비호환/고장난 엔진/정상)가 원본 run_produced_car()와 문자열 단위로 정확히 일치하는지 확인
- [ ] test_report()가 엔진 고장 여부를 검사하지 않는지 확인 - "고장난 엔진인데도 TEST는 PASS로 나오는" quirk를 재현하고 있는지가 핵심 리뷰 포인트
- [ ] pytest tests/test_car.py -v 실행 결과 전부 PASS
- [ ] CarBuild에 판정 로직(예: if self.car_type == ... and self.brake == ... 같은 코드)이 전혀 없고, 전부 self.engine.xxx(...) / self.brake.xxx(...) 위임 호출뿐인지 확인
