# Phase 1: `CarType` (차량 타입 — 부품 아님, 단순 식별자)

## 목적

리팩토링 전체의 뼈대가 되는 패키지(`car_assembly`)를 만들고, 차량 타입(Sedan/SUV/Truck)을 원본의 전역 int 상수 대신 `IntEnum`으로 표현한다. 차량 타입은 이후 Phase에서 다룰 엔진/제동장치/조향장치와 달리 자체 행동(호환성 로직 등)이 없는 단순 식별자이므로, 클래스 계층이 아닌 `Enum` + 라벨 딕셔너리로만 표현한다.

## 사전 조건

없음(첫 Phase).

## 구현 절차

### 태스크 1.1: 패키지 뼈대 생성

- Create: `car_assembly/__init__.py` — 내용은 완전히 빈 파일(0바이트)로 생성한다.
- 커밋:
  ```bash
  git add car_assembly/__init__.py
  git commit -m "chore: create car_assembly package"
  ```

### 태스크 1.2: `CarType` enum + 라벨

1. Test 작성 — `tests/test_car_type.py` 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
   from car_assembly.car_type import CAR_TYPE_LABEL, CarType


   def test_car_type_values():
       assert CarType.SEDAN == 1
       assert CarType.SUV == 2
       assert CarType.TRUCK == 3


   def test_car_type_labels():
       assert CAR_TYPE_LABEL[CarType.SEDAN] == "Sedan"
       assert CAR_TYPE_LABEL[CarType.SUV] == "SUV"
       assert CAR_TYPE_LABEL[CarType.TRUCK] == "Truck"
   ```

2. 실행: `pytest tests/test_car_type.py -v`
   기대 결과: `ModuleNotFoundError: No module named 'car_assembly.car_type'`로 실패. 실패를 확인한 뒤 다음 단계로 진행한다.

3. 구현 — `car_assembly/car_type.py` 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
   from enum import IntEnum


   class CarType(IntEnum):
       SEDAN = 1
       SUV = 2
       TRUCK = 3


   CAR_TYPE_LABEL = {
       CarType.SEDAN: "Sedan",
       CarType.SUV: "SUV",
       CarType.TRUCK: "Truck",
   }
   ```

4. 실행: `pytest tests/test_car_type.py -v`
   기대 결과: `test_car_type_values`, `test_car_type_labels` 모두 PASS. 실패하면 3번 코드가 위 내용과 정확히 일치하는지 다시 확인한다.

5. 커밋:
   ```bash
   git add car_assembly/car_type.py tests/test_car_type.py
   git commit -m "feat: add CarType enum with labels"
   ```

## 이 Phase가 끝나면 존재해야 하는 것

- `car_assembly/__init__.py` (빈 파일)
- `car_assembly/car_type.py` (위 코드 그대로)
- `tests/test_car_type.py` (위 코드 그대로)
- git 커밋 2개: `chore: create car_assembly package`, `feat: add CarType enum with labels`

이 시점에 `car_assembly.parts`, `car_assembly.car`, `car_assembly.cli`, `assembly.py` 수정은 **아직 하지 않는다.** 원본 `assembly.py`는 이 Phase 이후에도 그대로 동작해야 한다(아직 아무것도 대체하지 않았으므로).

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] `car_assembly/__init__.py`, `car_assembly/car_type.py`, `tests/test_car_type.py` 세 파일이 위 코드와 한 글자도 다르지 않게 생성되었는지 확인
- [ ] `CarType.SEDAN == 1`, `CarType.SUV == 2`, `CarType.TRUCK == 3` — 원본 `assembly.py`의 `SEDAN=1`, `SUV=2`, `TRUCK=3` 상수 값과 동일한지 확인
- [ ] `CAR_TYPE_LABEL`의 라벨 문자열이 원본 출력 문구와 정확히 일치하는지 확인: `"Sedan"`, `"SUV"`, `"Truck"` (대소문자 포함)
- [ ] `pytest tests/test_car_type.py -v` 실행 결과 2개 테스트 모두 PASS
- [ ] `git log --oneline -2`로 커밋 2개가 순서대로 존재하는지 확인
- [ ] 원본 `assembly.py`를 아직 건드리지 않았는지 확인 (`git diff HEAD~2 -- assembly.py`가 비어 있어야 함)
