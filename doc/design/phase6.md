# Phase 6: SteeringPart 계열 + assembly.py 통합

## 목적

조향장치 2종(Bosch/Mobis)을 클래스로 표현하고, 만들자마자 assembly.py의 select_steering()/run_produced_car()에 바로 연결한다(strangler-fig). 조향장치는 차량 타입 제약이 없으므로 CarTypeConstrained 믹스인을 받지 않고 Part만 상속한다.

## 사전 조건

Phase 5(BrakePart 계열 + assembly.py 통합) 완료. `pytest tests/test_assembly_characterization.py -v` 실행해 통합 전 전부 PASS 확인.

## 구현 절차

### 태스크 6.1: SteeringPart 베이스 + BoschSteering

1. Test 추가 - tests/test_parts.py 파일 끝에 추가:

   ```python
   from car_assembly.parts import BoschSteering


   def test_bosch_steering():
       steering = BoschSteering()
       assert steering.is_bosch is True
       assert steering.selection_message() == "BOSCH 조향장치를 선택하셨습니다."
       assert steering.run_label() == "Bosch"
   ```

2. 실행: pytest tests/test_parts.py -v -> ImportError로 실패 확인

3. 구현 - car_assembly/parts.py 파일 끝에 추가:

   ```python
   class SteeringPart(Part):
       unit_label = "조향장치를"
       is_bosch: bool = False


   class BoschSteering(SteeringPart):
       label = "Bosch"
       is_bosch = True
   ```

   주의: SteeringPart(Part)로만 상속하고 CarTypeConstrained는 추가하지 않는다.

4. 실행: pytest tests/test_parts.py -v -> PASS 확인
5. 커밋: git commit -am "feat: add SteeringPart base and BoschSteering"

### 태스크 6.2: MobisSteering

1. Test 추가:

   ```python
   from car_assembly.parts import MobisSteering


   def test_mobis_steering():
       steering = MobisSteering()
       assert steering.is_bosch is False
       assert steering.selection_message() == "MOBIS 조향장치를 선택하셨습니다."
       assert steering.run_label() == "Mobis"
   ```

2. 구현 - car_assembly/parts.py 파일 끝에 추가:

   ```python
   class MobisSteering(SteeringPart):
       label = "Mobis"
   ```

3. 실행: pytest tests/test_parts.py -v -> PASS 확인
4. 커밋: git commit -am "feat: add MobisSteering"

### 태스크 6.3: STEERING_BY_CODE 팩토리 딕셔너리 + BoschBrake와 실제 조합 검증

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

2. 구현 - car_assembly/parts.py 파일 끝에 추가:

   ```python
   STEERING_BY_CODE = {1: BoschSteering, 2: MobisSteering}
   ```

3. 실행: pytest tests/test_parts.py -v -> 전체 PASS 확인(엔진/브레이크/조향장치 전부)
4. 커밋: git commit -am "feat: add STEERING_BY_CODE factory map"

### 태스크 6.4: assembly.py 통합 (strangler-fig 컷오버)

1. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
2. assembly.py의 BRAKE_BY_CODE import 줄을 아래로 교체:

   ```python
   from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE
   ```

3. assembly.py의 select_steering() 함수 전체를 아래로 교체:

   ```python
   def select_steering(a):
       global q3
       q3 = a
       print(STEERING_BY_CODE[a]().selection_message())
   ```

4. assembly.py의 run_produced_car() 안에 있는 아래 if/elif 블록:

   ```python
   if q3 == 1:
       print("Steering : Bosch")
   elif q3 == 2:
       print("Steering : Mobis")
   ```

   을 아래 한 줄로 교체:

   ```python
   print(f"Steering : {STEERING_BY_CODE[q3]().run_label()}")
   ```

5. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인
6. 커밋:
   ```bash
   git add assembly.py
   git commit -m "Integrate SteeringPart into assembly.py (strangler-fig cutover, small step)"
   ```

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/parts.py에 SteeringPart, BoschSteering, MobisSteering, STEERING_BY_CODE 추가됨 - car_assembly/parts.py는 이로써 완성(이후 수정 없음)
- assembly.py의 select_steering()/run_produced_car() 조향장치 출력이 STEERING_BY_CODE에 위임됨
- assembly.py의 run_produced_car()는 이제 Car Type/Engine/Brake/Steering 네 줄 전부 car_assembly 부품 클래스에 위임하고, 남은 원본 로직은 is_valid_check()/test_produced_car()의 호환성 판정과 main()의 상태 전이뿐

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] SteeringPart가 CarTypeConstrained를 상속하지 않는지 확인
- [ ] BoschSteering/MobisSteering의 메시지가 원본과 정확히 일치하는지 확인
- [ ] select_steering()과 run_produced_car()의 조향장치 출력이 STEERING_BY_CODE 위임으로 교체되었는지 확인
- [ ] pytest tests/test_assembly_characterization.py -v 실행 결과 통합 전후 모두 PASS(회귀 없음)
- [ ] BOSCH_S/MOBIS 상수, q3 전역 변수는 아직 남아있는지 확인(Phase 7에서 정리 예정)
- [ ] pytest tests/test_parts.py -v 전체 실행 -> 부품 3계열 전부 PASS
