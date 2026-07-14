# Phase 5: `BrakePart` 계열

## 목적

제동장치 3종(Mando/Continental/Bosch)을 클래스로 표현한다. 제동장치는 엔진과 같은 "차량 타입 제약"(`CarTypeConstrained` 재사용) 외에, 엔진에는 없는 "조향장치 제약"(Bosch 제동장치는 Bosch 조향장치가 필요)을 추가로 갖는다.

## 사전 조건

Phase 4(`EnginePart` 계열) 완료.

## 구현 절차

### 태스크 5.1: `BrakePart` 베이스 + `MandoBrake` (Truck 불가)

1. Test 추가 — `tests/test_parts.py` 파일 끝에 추가:

   ```python
   from car_assembly.parts import MandoBrake


   def test_mando_brake_incompatible_with_truck():
       brake = MandoBrake()
       assert brake.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 Mando제동장치 사용 불가"
       assert brake.incompatibility_with_car_type(CarType.SEDAN) is None
       assert brake.selection_message() == "MANDO 제동장치를 선택하셨습니다."
       assert brake.run_label() == "Mando"
   ```

2. 실행: `pytest tests/test_parts.py -v` -> `ImportError`로 실패 확인

3. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class BrakePart(CarTypeConstrained, Part):
       unit_label = "제동장치를"
       car_type_conflict_noun = "제동장치"
       requires_bosch_steering: bool = False

       def incompatibility_with_steering(self, steering) -> Optional[str]:
           if self.requires_bosch_steering and not steering.is_bosch:
               return "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"
           return None


   class MandoBrake(BrakePart):
       label = "Mando"
       unsupported_car_type = CarType.TRUCK
   ```

4. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
5. 커밋: `git commit -am "feat: add BrakePart base and MandoBrake"`

### 태스크 5.2: `ContinentalBrake` (Sedan 불가)

1. Test 추가:

   ```python
   from car_assembly.parts import ContinentalBrake


   def test_continental_brake_incompatible_with_sedan():
       brake = ContinentalBrake()
       assert brake.incompatibility_with_car_type(CarType.SEDAN) == "Sedan에는 Continental제동장치 사용 불가"
       assert brake.selection_message() == "CONTINENTAL 제동장치를 선택하셨습니다."
       assert brake.run_label() == "Continental"
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class ContinentalBrake(BrakePart):
       label = "Continental"
       unsupported_car_type = CarType.SEDAN
   ```

3. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
4. 커밋: `git commit -am "feat: add ContinentalBrake"`

### 태스크 5.3: `BoschBrake` (Bosch 조향장치 필요)

이 태스크는 `SteeringPart`(Phase 6)가 아직 없어도 진행할 수 있다 — `incompatibility_with_steering`은 `steering.is_bosch` 속성만 읽으므로(덕 타이핑), 그 속성만 가진 가짜 객체로 검증한다.

1. Test 추가:

   ```python
   from car_assembly.parts import BoschBrake


   class _FakeSteering:
       def __init__(self, is_bosch):
           self.is_bosch = is_bosch


   def test_bosch_brake_requires_bosch_steering():
       brake = BoschBrake()
       assert brake.incompatibility_with_steering(_FakeSteering(False)) == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"
       assert brake.incompatibility_with_steering(_FakeSteering(True)) is None
       assert brake.incompatibility_with_car_type(CarType.SEDAN) is None
       assert brake.selection_message() == "BOSCH 제동장치를 선택하셨습니다."
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class BoschBrake(BrakePart):
       label = "Bosch"
       requires_bosch_steering = True
   ```

3. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
4. 커밋: `git commit -am "feat: add BoschBrake requiring Bosch steering"`

### 태스크 5.4: `BRAKE_BY_CODE` 팩토리 딕셔너리

1. Test 추가:

   ```python
   from car_assembly.parts import BRAKE_BY_CODE, BoschBrake, ContinentalBrake, MandoBrake


   def test_brake_by_code_maps_input_number_to_class():
       assert BRAKE_BY_CODE[1] is MandoBrake
       assert BRAKE_BY_CODE[2] is ContinentalBrake
       assert BRAKE_BY_CODE[3] is BoschBrake
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   BRAKE_BY_CODE = {1: MandoBrake, 2: ContinentalBrake, 3: BoschBrake}
   ```

3. 실행: `pytest tests/test_parts.py -v` -> 전체 PASS 확인
4. 커밋: `git commit -am "feat: add BRAKE_BY_CODE factory map"`

## 이 Phase가 끝나면 존재해야 하는 것

- `car_assembly/parts.py`에 `BrakePart`, `MandoBrake`, `ContinentalBrake`, `BoschBrake`, `BRAKE_BY_CODE` 추가됨
- `BrakePart`가 `EnginePart`와 마찬가지로 `CarTypeConstrained`를 재사용(차량 타입 제약 로직을 새로 작성하지 않음)하고, `incompatibility_with_steering`만 새로 추가
- git 커밋 4개(누적 13개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] `BrakePart`가 `CarTypeConstrained`를 재사용하고 있는지 확인(차량 타입 제약 로직을 새로 작성하지 않았어야 함)
- [ ] `incompatibility_with_steering`이 `BrakePart`에서만 정의되어 있고(엔진/조향장치엔 없음), `requires_bosch_steering=True`인 경우에만 메시지를 반환하는지 확인
- [ ] 메시지 정확히 일치 확인:
  - `MandoBrake().incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 Mando제동장치 사용 불가"`
  - `ContinentalBrake().incompatibility_with_car_type(CarType.SEDAN) == "Sedan에는 Continental제동장치 사용 불가"`
  - `BoschBrake().incompatibility_with_steering(<is_bosch=False>) == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"`
- [ ] 선택 메시지가 전부 대문자인지 확인: `"MANDO 제동장치를 선택하셨습니다."` 등
- [ ] `run_label()`은 대문자가 아니라 원래 표기(`"Mando"`, `"Continental"`, `"Bosch"`)를 반환하는지 확인
- [ ] `pytest tests/test_parts.py -v -k Brake` 실행 결과 전부 PASS

## 태스크 5.5: assembly.py 통합 (strangler-fig 컷오버)

1. 통합 전 확인: `pytest tests/test_assembly_characterization.py -v` -> 전부 PASS 확인
2. `assembly.py`의 `ENGINE_BY_CODE` import 줄을 아래로 교체:

   ```python
   from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE
   ```

3. `assembly.py`의 `select_brake()` 함수 전체를 아래로 교체:

   ```python
   def select_brake(a):
       global q2
       q2 = a
       print(BRAKE_BY_CODE[a]().selection_message())
   ```

4. `assembly.py`의 `run_produced_car()` 안에 있는 아래 if/elif 블록:

   ```python
   if q2 == 1:
       print("Brake    : Mando")
   elif q2 == 2:
       print("Brake    : Continental")
   elif q2 == 3:
       print("Brake    : Bosch")
   ```

   을 아래 한 줄로 교체:

   ```python
   print(f"Brake    : {BRAKE_BY_CODE[q2]().run_label()}")
   ```

5. 통합 후 확인: `pytest tests/test_assembly_characterization.py -v` -> 여전히 전부 PASS 확인
6. 커밋:
   ```bash
   git add assembly.py
   git commit -m "Integrate BrakePart into assembly.py (strangler-fig cutover, small step)"
   ```

## 구현 확인 체크리스트 추가 (assembly.py 통합)

- [ ] `select_brake()`와 `run_produced_car()`의 브레이크 출력이 `BRAKE_BY_CODE` 위임으로 교체되었는지 확인
- [ ] `pytest tests/test_assembly_characterization.py -v` 실행 결과 통합 전후 모두 PASS(회귀 없음)
- [ ] `MANDO`/`CONTINENTAL`/`BOSCH_B` 상수, `q2` 전역 변수는 아직 남아있는지 확인(Phase 7에서 정리 예정)
