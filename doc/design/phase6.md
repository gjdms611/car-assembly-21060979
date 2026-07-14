# Phase 6: `SteeringPart` 계열

## 목적

조향장치 2종(Bosch/Mobis)을 클래스로 표현한다. 조향장치는 차량 타입 제약이 전혀 없으므로 `CarTypeConstrained` 믹스인을 받지 않고 `Part`만 상속한다.

## 사전 조건

Phase 5(`BrakePart` 계열) 완료.

## 구현 절차

### 태스크 6.1: `SteeringPart` 베이스 + `BoschSteering`

1. Test 추가 — `tests/test_parts.py` 파일 끝에 추가:

   ```python
   from car_assembly.parts import BoschSteering


   def test_bosch_steering():
       steering = BoschSteering()
       assert steering.is_bosch is True
       assert steering.selection_message() == "BOSCH 조향장치를 선택하셨습니다."
       assert steering.run_label() == "Bosch"
   ```

2. 실행: `pytest tests/test_parts.py -v` -> `ImportError`로 실패 확인

3. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class SteeringPart(Part):
       unit_label = "조향장치를"
       is_bosch: bool = False


   class BoschSteering(SteeringPart):
       label = "Bosch"
       is_bosch = True
   ```

   주의: `SteeringPart(Part)`로만 상속하고 `CarTypeConstrained`는 절대 추가하지 않는다.

4. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
5. 커밋: `git commit -am "feat: add SteeringPart base and BoschSteering"`

### 태스크 6.2: `MobisSteering`

1. Test 추가:

   ```python
   from car_assembly.parts import MobisSteering


   def test_mobis_steering():
       steering = MobisSteering()
       assert steering.is_bosch is False
       assert steering.selection_message() == "MOBIS 조향장치를 선택하셨습니다."
       assert steering.run_label() == "Mobis"
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class MobisSteering(SteeringPart):
       label = "Mobis"
   ```

3. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
4. 커밋: `git commit -am "feat: add MobisSteering"`

### 태스크 6.3: `STEERING_BY_CODE` 팩토리 딕셔너리 + 실제 `BoschBrake`/`BoschSteering` 조합 검증

5.3에서는 `BoschBrake.incompatibility_with_steering`을 가짜 객체(`_FakeSteering`)로만 검증했다. 이제 실제 `SteeringPart` 서브클래스로 다시 한번 확인한다.

1. Test 추가:

   ```python
   from car_assembly.parts import STEERING_BY_CODE, BoschBrake, BoschSteering, MobisSteering


   def test_steering_by_code_maps_input_number_to_class():
       assert STEERING_BY_CODE[1] is BoschSteering
       assert STEERING_BY_CODE[2] is MobisSteering


   def test_bosch_brake_with_real_steering_classes():
       brake = BoschBrake()
       assert brake.incompatibility_with_steering(BoschSteering()) is None
       assert brake.incompatibility_with_steering(MobisSteering()) == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   STEERING_BY_CODE = {1: BoschSteering, 2: MobisSteering}
   ```

3. 실행: `pytest tests/test_parts.py -v` -> 전체 PASS 확인 (이 시점에 `test_parts.py`의 모든 테스트, 즉 엔진/브레이크/조향장치 전체가 PASS해야 함)
4. 커밋: `git commit -am "feat: add STEERING_BY_CODE factory map"`

## 이 Phase가 끝나면 존재해야 하는 것

- `car_assembly/parts.py`에 `SteeringPart`, `BoschSteering`, `MobisSteering`, `STEERING_BY_CODE` 추가됨 — 이로써 `car_assembly/parts.py`는 완성된다(이후 Phase에서 이 파일을 더 수정하지 않는다)
- git 커밋 3개(누적 16개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] `SteeringPart`가 `CarTypeConstrained`를 상속하지 **않는지** 확인
- [ ] 메시지 정확히 일치 확인:
  - `BoschSteering().selection_message() == "BOSCH 조향장치를 선택하셨습니다."`
  - `MobisSteering().selection_message() == "MOBIS 조향장치를 선택하셨습니다."`
  - `run_label()`은 각각 `"Bosch"`, `"Mobis"` (원표기, 대문자 아님)
- [ ] `test_bosch_brake_with_real_steering_classes` — "Bosch 브레이크 + Bosch 아닌 조향장치 -> 실패" 규칙이 진짜 클래스로도 동일하게 성립하는지 확인
- [ ] `pytest tests/test_parts.py -v` 전체 실행 -> `car_assembly/parts.py` 관련 테스트 전부 PASS. 이 시점에 부품 3계열(엔진/브레이크/조향장치)이 모두 완성됨
