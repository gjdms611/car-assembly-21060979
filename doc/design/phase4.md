# Phase 4: `EnginePart` 계열

## 목적

Phase 2(`Part`)와 Phase 3(`CarTypeConstrained`)를 실제로 사용하는 첫 부품 계열을 만든다. 엔진 4종(GM/TOYOTA/WIA/고장난 엔진)을 각각 클래스로 표현해, "이 엔진은 어느 차량 타입과 호환 안 되는지"를 엔진 객체 스스로 알게 한다.

## 사전 조건

Phase 3(`CarTypeConstrained`) 완료.

## 구현 절차

### 태스크 4.1: `EnginePart` 베이스 + `GMEngine`

1. Test 추가 — `tests/test_parts.py` 파일 끝에 추가(상단에 `from car_assembly.car_type import CarType`는 이미 있으므로 재사용):

   ```python
   from car_assembly.parts import GMEngine


   def test_gm_engine_label_and_message():
       engine = GMEngine()
       assert engine.selection_message() == "GM 엔진을 선택하셨습니다."
       assert engine.run_label() == "GM"
       assert engine.is_broken is False


   def test_gm_engine_compatible_with_every_car_type():
       engine = GMEngine()
       assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
       assert engine.incompatibility_with_car_type(CarType.SUV) is None
       assert engine.incompatibility_with_car_type(CarType.TRUCK) is None
   ```

2. 실행: `pytest tests/test_parts.py -v`
   기대 결과: `ImportError: cannot import name 'GMEngine' from 'car_assembly.parts'`로 실패.

3. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class EnginePart(CarTypeConstrained, Part):
       unit_label = "엔진을"
       car_type_conflict_noun = "엔진"
       is_broken: bool = False


   class GMEngine(EnginePart):
       label = "GM"
   ```

4. 실행: `pytest tests/test_parts.py -v` -> 새 테스트 2개 PASS, 기존 테스트도 전부 PASS.
5. 커밋: `git commit -am "feat: add EnginePart base and GMEngine"`

### 태스크 4.2: `ToyotaEngine` (SUV 불가)

1. Test 추가:

   ```python
   from car_assembly.parts import ToyotaEngine


   def test_toyota_engine_incompatible_with_suv():
       engine = ToyotaEngine()
       assert engine.incompatibility_with_car_type(CarType.SUV) == "SUV에는 TOYOTA엔진 사용 불가"
       assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
       assert engine.selection_message() == "TOYOTA 엔진을 선택하셨습니다."
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class ToyotaEngine(EnginePart):
       label = "TOYOTA"
       unsupported_car_type = CarType.SUV
   ```

3. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
4. 커밋: `git commit -am "feat: add ToyotaEngine"`

### 태스크 4.3: `WIAEngine` (Truck 불가)

1. Test 추가:

   ```python
   from car_assembly.parts import WIAEngine


   def test_wia_engine_incompatible_with_truck():
       engine = WIAEngine()
       assert engine.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 WIA엔진 사용 불가"
       assert engine.selection_message() == "WIA 엔진을 선택하셨습니다."
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class WIAEngine(EnginePart):
       label = "WIA"
       unsupported_car_type = CarType.TRUCK
   ```

3. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
4. 커밋: `git commit -am "feat: add WIAEngine"`

### 태스크 4.4: `BrokenEngine` (항상 호환되지만 `is_broken=True`, run 리포트에 라벨 없음)

1. Test 추가:

   ```python
   from car_assembly.parts import BrokenEngine


   def test_broken_engine_is_broken_and_has_no_run_label():
       engine = BrokenEngine()
       assert engine.is_broken is True
       assert engine.run_label() is None
       assert engine.selection_message() == "고장난 엔진을 선택하셨습니다."
       assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝에 추가:

   ```python
   class BrokenEngine(EnginePart):
       label = "고장난"
       is_broken = True

       def run_label(self) -> Optional[str]:
           return None
   ```

3. 실행: `pytest tests/test_parts.py -v` -> PASS 확인
4. 커밋: `git commit -am "feat: add BrokenEngine"`

### 태스크 4.5: `ENGINE_BY_CODE` 팩토리 딕셔너리

1. Test 추가:

   ```python
   from car_assembly.parts import ENGINE_BY_CODE, BrokenEngine, GMEngine, ToyotaEngine, WIAEngine


   def test_engine_by_code_maps_input_number_to_class():
       assert ENGINE_BY_CODE[1] is GMEngine
       assert ENGINE_BY_CODE[2] is ToyotaEngine
       assert ENGINE_BY_CODE[3] is WIAEngine
       assert ENGINE_BY_CODE[4] is BrokenEngine
   ```

2. 구현 — `car_assembly/parts.py` 파일 끝(엔진 클래스들 바로 아래)에 추가:

   ```python
   ENGINE_BY_CODE = {1: GMEngine, 2: ToyotaEngine, 3: WIAEngine, 4: BrokenEngine}
   ```

3. 실행: `pytest tests/test_parts.py -v` -> 전체 PASS 확인
4. 커밋: `git commit -am "feat: add ENGINE_BY_CODE factory map"`

## 이 Phase가 끝나면 존재해야 하는 것

- `car_assembly/parts.py`에 `EnginePart`, `GMEngine`, `ToyotaEngine`, `WIAEngine`, `BrokenEngine`, `ENGINE_BY_CODE` 추가됨
- 4개 엔진 클래스는 각각 `label`(+필요 시 `unsupported_car_type`)만 정의하고, `incompatibility_with_car_type`/`selection_message`/`run_label`은 전혀 재작성하지 않음(단, `BrokenEngine`은 `run_label`만 오버라이드)
- git 커밋 5개(누적 9개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] 4개 엔진 클래스가 각각 `label` 하나(+필요 시 `unsupported_car_type`)만 정의하고 있는지 확인(중복 코드 없음이 핵심 리뷰 포인트)
- [ ] 메시지 정확히 일치 확인:
  - `GMEngine().selection_message() == "GM 엔진을 선택하셨습니다."`
  - `ToyotaEngine().incompatibility_with_car_type(CarType.SUV) == "SUV에는 TOYOTA엔진 사용 불가"`
  - `WIAEngine().incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 WIA엔진 사용 불가"`
  - `BrokenEngine().selection_message() == "고장난 엔진을 선택하셨습니다."`, `run_label() is None`
- [ ] `ENGINE_BY_CODE`의 키(1~4)가 원본 메뉴 번호(`1.GM 2.TOYOTA 3.WIA 4.고장난 엔진`)와 정확히 일치하는지 확인
- [ ] `pytest tests/test_parts.py -v -k Engine` 실행 결과 전부 PASS

## 태스크 4.6: assembly.py 통합 (strangler-fig 컷오버)

1. 통합 전 확인: `pytest tests/test_assembly_characterization.py -v` -> 전부 PASS 확인
2. `assembly.py` 최상단 import 영역에 추가:

   ```python
   from car_assembly.parts import ENGINE_BY_CODE
   ```

3. `assembly.py`의 `select_engine()` 함수 전체를 아래로 교체:

   ```python
   def select_engine(a):
       global q1
       q1 = a
       print(ENGINE_BY_CODE[a]().selection_message())
   ```

4. `assembly.py`의 `run_produced_car()` 안에 있는 아래 if/elif 블록:

   ```python
   if q1 == 1:
       print("Engine   : GM")
   elif q1 == 2:
       print("Engine   : TOYOTA")
   elif q1 == 3:
       print("Engine   : WIA")
   ```

   을 아래로 교체:

   ```python
   engine_label = ENGINE_BY_CODE[q1]().run_label()
   if engine_label is not None:
       print(f"Engine   : {engine_label}")
   ```

   (`BrokenEngine.run_label()`이 `None`을 반환하므로 `q1 == 4`일 때 이 줄이 자동으로 생략된다 — 다만 `run_produced_car()`는 이 지점에 도달하기 전에 이미 `if q1 == 4:` 분기에서 return하므로 실제로는 도달하지 않는 방어적 코드다.)

5. 통합 후 확인: `pytest tests/test_assembly_characterization.py -v` -> 여전히 전부 PASS 확인
6. 커밋:
   ```bash
   git add assembly.py
   git commit -m "Integrate EnginePart into assembly.py (strangler-fig cutover, small step)"
   ```

## 구현 확인 체크리스트 추가 (assembly.py 통합)

- [ ] `select_engine()`과 `run_produced_car()`의 엔진 출력이 `ENGINE_BY_CODE` 위임으로 교체되었는지 확인
- [ ] `pytest tests/test_assembly_characterization.py -v` 실행 결과 통합 전후 모두 PASS(회귀 없음)
- [ ] `GM`/`TOYOTA`/`WIA` 상수, `q1` 전역 변수는 아직 남아있는지 확인(Phase 7에서 정리 예정)
