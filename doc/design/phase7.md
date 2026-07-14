# Phase 7: CarBuild + assembly.py 핵심 판정 로직 통합

## 목적

부품 4종이 이미 assembly.py에 다 연결되어 있으므로(Phase 1,4,5,6), 이제 원본에서 가장 위험했던 교차 부품 호환성 판정(is_valid_check/run_produced_car의 호환성 체크/test_produced_car)을 CarBuild로 옮긴다. 위험한 로직이지만 나머지가 이미 정리되어 있어 통합 범위가 함수 3개로 좁고 명확하다.

## 사전 조건

Phase 6(SteeringPart + assembly.py 통합) 완료. pytest tests/test_assembly_characterization.py -v 실행해 통합 전 전부 PASS 확인.

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

2. 실행: pytest tests/test_car.py -v -> ModuleNotFoundError로 실패 확인

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

4. 실행: pytest tests/test_car.py -v -> 4개 PASS 확인
5. 커밋: git add car_assembly/car.py tests/test_car.py && git commit -m "feat: add CarBuild skeleton holding part objects"

### 태스크 7.2: first_incompatibility() / is_compatible()

1. Test 추가 - tests/test_car.py 상단 import에 추가:

   ```python
   from car_assembly.parts import BoschBrake, ContinentalBrake, MandoBrake, WIAEngine
   ```

   파일 끝에 추가:

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

2. 실행: pytest tests/test_car.py -v -> AttributeError로 실패 확인

3. 구현 - car_assembly/car.py의 CarBuild 클래스 안에 추가:

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

   중요: 엔진 -> 제동장치-차량타입 -> 제동장치-조향장치 순서를 반드시 지킨다(Truck+WIA+Mando 동시 위반 시 원본과 동일하게 엔진 메시지가 우선해야 함).

4. 실행: pytest tests/test_car.py -v -> PASS 확인
5. 커밋: git commit -am "feat: add CarBuild.first_incompatibility delegating to part objects"

### 태스크 7.3: run_report() / test_report()

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

2. 구현 - car_assembly/car.py의 CarBuild 클래스 안에 추가:

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

       def test_report(self) -> str:
           message = self.first_incompatibility()
           if message is None:
               return "PASS"
           return f"FAIL\n{message}"
   ```

3. 실행: pytest tests/test_car.py -v -> 전체 PASS 확인
4. 커밋: git commit -am "feat: add CarBuild.run_report and test_report"

### 태스크 7.4: assembly.py 통합 (1/3) - is_valid_check

1. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
2. assembly.py 최상단 import 영역에 추가:

   ```python
   from car_assembly.car import CarBuild
   ```

3. assembly.py 파일의 is_valid_check 바로 위에 헬퍼 함수 추가:

   ```python
   def build_from_globals():
       return CarBuild(
           car_type=CarType(q0),
           engine=ENGINE_BY_CODE[q1](),
           brake=BRAKE_BY_CODE[q2](),
           steering=STEERING_BY_CODE[q3](),
       )
   ```

4. is_valid_check() 함수 전체를 아래로 교체:

   ```python
   def is_valid_check():
       return build_from_globals().is_compatible()
   ```

5. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인
6. 커밋: git add assembly.py && git commit -m "Integrate CarBuild into assembly.py is_valid_check (strangler-fig cutover, small step)"

### 태스크 7.5: assembly.py 통합 (2/3) - test_produced_car

1. test_produced_car() 함수 전체를 아래로 교체:

   ```python
   def test_produced_car():
       print(build_from_globals().test_report())
   ```

2. 실행: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
3. 커밋: git commit -am "Integrate CarBuild into assembly.py test_produced_car (strangler-fig cutover, small step)"

### 태스크 7.6: assembly.py 통합 (3/3) - run_produced_car

1. run_produced_car() 함수 전체를 아래로 교체:

   ```python
   def run_produced_car():
       for line in build_from_globals().run_report():
           print(line)
   ```

2. 실행: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
3. 커밋: git commit -am "Integrate CarBuild into assembly.py run_produced_car (strangler-fig cutover, small step)"

### 태스크 7.7: 정리 - 미사용 코드 제거

is_valid_check()를 이제 아무도 호출하지 않는다(run_produced_car()가 build_from_globals().run_report()로 직접 판정). 원본 호환성 상수(SEDAN/SUV/TRUCK/GM/TOYOTA/WIA/MANDO/CONTINENTAL/BOSCH_B/BOSCH_S/MOBIS)도 더 이상 어디에서도 참조되지 않는다.

1. assembly.py에서 is_valid_check() 함수 전체를 삭제한다.
2. assembly.py 상단의 아래 상수 정의 블록을 전부 삭제한다:

   ```python
   SEDAN = 1
   SUV = 2
   TRUCK = 3

   GM = 1
   TOYOTA = 2
   WIA = 3

   MANDO = 1
   CONTINENTAL = 2
   BOSCH_B = 3

   BOSCH_S = 1
   MOBIS = 2
   ```

3. 실행: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인(삭제한 코드가 실제로 아무 데서도 쓰이지 않았음을 재확인)
4. 커밋: git commit -am "chore: remove dead is_valid_check and legacy compatibility constants from assembly.py"

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/car.py - CarBuild 완성(필드 4개 + is_engine_broken/first_incompatibility/is_compatible/run_report/test_report)
- assembly.py의 is_valid_check/run_produced_car/test_produced_car가 전부 build_from_globals()를 통해 CarBuild에 위임
- assembly.py에서 원본 호환성 상수와 원본 is_valid_check 로직이 완전히 제거됨(q0~q4 전역 변수는 아직 남아있음 - Phase 9에서 정리)
- git 커밋 다수(car_assembly 쪽 4개 + 통합 3개 + 정리 1개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] first_incompatibility()가 엔진 -> 제동장치(차량타입) -> 제동장치(조향장치) 순서로 검사하는지 확인
- [ ] run_report()/test_report()가 원본 run_produced_car()/test_produced_car()와 문자열 단위로 정확히 일치하는지 확인
- [ ] test_report()가 엔진 고장 여부를 검사하지 않는 원본 quirk를 재현하는지 확인
- [ ] pytest tests/test_car.py -v 전체 PASS
- [ ] pytest tests/test_assembly_characterization.py -v 실행 결과 7.4~7.7 각 커밋 전후 모두 PASS(회귀 없음)
- [ ] assembly.py에 SEDAN/SUV/TRUCK/GM/TOYOTA/WIA/MANDO/CONTINENTAL/BOSCH_B/BOSCH_S/MOBIS 상수와 is_valid_check()가 더 이상 존재하지 않는지 확인
- [ ] q0~q4 전역 변수는 아직 남아있는지 확인(의도적 - Phase 9에서 정리)
