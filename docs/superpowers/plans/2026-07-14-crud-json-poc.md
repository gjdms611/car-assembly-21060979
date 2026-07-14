# CRUD JSON Console App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** JSON 파일로 조립된 차량 레코드를 관리하는 CRUD 콘솔 애플리케이션을 만든다 (Create/Read/Update/Delete), car-assembly의 기존 차종/부품 도메인을 재사용하고 정렬은 자체 구현한 QuickSort를 사용한다.

**Architecture:** `car_assembly/` 패키지의 기존 `car_type.py`, `parts.py`를 그대로 가져다 쓰고, 신규 `car_assembly/steering.py`로 조향장치 코드/라벨을 추가한다. CRUD 전용 로직은 새 `crud/` 패키지(`storage.py`, `quicksort.py`, `repository.py`, `crud_app.py`)에 둔다. 레코드는 `crud/data/cars.json`에 dict 리스트로 저장한다. `crud_app.py`는 `assembly.py`와 같은 번호 입력 + 화면 clear 메뉴 스타일을 따르되, 실제 로직은 모두 `repository.py`(테스트 가능)에 위임한다.

**Tech Stack:** Python 3 표준 라이브러리만 사용 (`json`, `os`). pytest.

## Global Constraints

- 표준 라이브러리 외 의존성 추가 금지 (spec: "언어/실행 환경")
- 기존 `assembly.py`, `car_assembly/car_type.py`, `car_assembly/parts.py`, `tests/test_car_type.py`, `tests/test_parts.py` 내용 변경 금지 (spec: "범위 제외")
- 레코드 스키마 고정: `{"id": int, "car_type": int, "engine_code": int, "brake_code": int, "steering_code": int}` (spec: "레코드 스키마")
- 부적합 조합 규칙은 `assembly.py`의 `is_valid_check`와 동일해야 함 (spec: "레코드 스키마" 하단 규칙 목록)
- 정렬은 반드시 QuickSort로 구현 (표준 `sorted()`/`list.sort()` 사용 금지) (spec: "사전 지식", "메뉴 흐름")
- pytest, plain `assert` 스타일 (기존 `tests/test_car_type.py`와 동일 스타일)

---

### Task 1: 조향장치 도메인 모듈 (`car_assembly/steering.py`)

**Files:**
- Create: `car_assembly/steering.py`
- Test: `tests/test_steering.py`

**Interfaces:**
- Consumes: 없음 (신규 독립 모듈)
- Produces: `STEERING_BY_CODE: dict[int, str]` — 코드 1=BOSCH, 2=MOBIS. 이후 Task 4(`repository.py`)에서 `from car_assembly.steering import STEERING_BY_CODE`로 사용.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_steering.py
from car_assembly.steering import STEERING_BY_CODE


def test_steering_codes():
    assert STEERING_BY_CODE[1] == "BOSCH"
    assert STEERING_BY_CODE[2] == "MOBIS"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_steering.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'car_assembly.steering'`

- [ ] **Step 3: Write minimal implementation**

```python
# car_assembly/steering.py
STEERING_BY_CODE = {
    1: "BOSCH",
    2: "MOBIS",
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_steering.py -v`
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add car_assembly/steering.py tests/test_steering.py
git commit -m "feat: add steering domain module"
git push
```

---

### Task 2: JSON 저장소 (`crud/storage.py`)

**Files:**
- Create: `crud/__init__.py` (빈 파일)
- Create: `crud/storage.py`
- Test: `tests/test_crud_storage.py`

**Interfaces:**
- Consumes: 없음
- Produces:
  - `DEFAULT_DATA_FILE: str` — 기본 저장 경로 (`crud/data/cars.json`의 절대 경로)
  - `load_cars(path: str = DEFAULT_DATA_FILE) -> list[dict]` — 파일 없으면 `[]` 반환
  - `save_cars(cars: list[dict], path: str = DEFAULT_DATA_FILE) -> None` — 디렉토리 없으면 생성 후 JSON으로 저장

  Task 4(`repository.py`)가 이 두 함수와 `DEFAULT_DATA_FILE`을 사용한다.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_crud_storage.py
import os

from crud.storage import load_cars, save_cars


def test_load_cars_missing_file_returns_empty_list(tmp_path):
    path = os.path.join(tmp_path, "does_not_exist.json")
    assert load_cars(path) == []


def test_save_then_load_round_trip(tmp_path):
    path = os.path.join(tmp_path, "nested_dir", "cars.json")
    cars = [
        {"id": 1, "car_type": 1, "engine_code": 1, "brake_code": 1, "steering_code": 1},
        {"id": 2, "car_type": 2, "engine_code": 2, "brake_code": 3, "steering_code": 1},
    ]

    save_cars(cars, path)
    loaded = load_cars(path)

    assert loaded == cars
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_crud_storage.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'crud'`

- [ ] **Step 3: Write minimal implementation**

```python
# crud/__init__.py
```

```python
# crud/storage.py
import json
import os

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "cars.json")


def load_cars(path=DEFAULT_DATA_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cars(cars, path=DEFAULT_DATA_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_crud_storage.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add crud/__init__.py crud/storage.py tests/test_crud_storage.py
git commit -m "feat: add JSON storage load/save for CRUD app"
git push
```

---

### Task 3: QuickSort (`crud/quicksort.py`)

**Files:**
- Create: `crud/quicksort.py`
- Test: `tests/test_crud_quicksort.py`

**Interfaces:**
- Consumes: 없음
- Produces: `quicksort(items: list[dict], key: str) -> list[dict]` — 원본 리스트를 변경하지 않고 `key` 필드 오름차순으로 정렬된 새 리스트를 반환. Task 4(`repository.py`)의 `list_cars`가 사용.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_crud_quicksort.py
from crud.quicksort import quicksort


def test_empty_list():
    assert quicksort([], "id") == []


def test_single_item():
    items = [{"id": 1}]
    assert quicksort(items, "id") == [{"id": 1}]


def test_sorts_ascending_by_key():
    items = [{"id": 3}, {"id": 1}, {"id": 2}]
    assert quicksort(items, "id") == [{"id": 1}, {"id": 2}, {"id": 3}]


def test_sorts_by_different_key():
    items = [
        {"id": 1, "car_type": 3},
        {"id": 2, "car_type": 1},
        {"id": 3, "car_type": 2},
    ]
    result = quicksort(items, "car_type")
    assert [item["id"] for item in result] == [2, 3, 1]


def test_handles_duplicate_keys():
    items = [{"id": 1}, {"id": 2}, {"id": 1}]
    result = quicksort(items, "id")
    assert [item["id"] for item in result] == [1, 1, 2]


def test_does_not_mutate_original_list():
    items = [{"id": 2}, {"id": 1}]
    quicksort(items, "id")
    assert items == [{"id": 2}, {"id": 1}]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_crud_quicksort.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'crud.quicksort'`

- [ ] **Step 3: Write minimal implementation**

```python
# crud/quicksort.py
def quicksort(items, key):
    if len(items) <= 1:
        return list(items)

    pivot = items[len(items) // 2][key]
    less = [item for item in items if item[key] < pivot]
    equal = [item for item in items if item[key] == pivot]
    greater = [item for item in items if item[key] > pivot]

    return quicksort(less, key) + equal + quicksort(greater, key)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_crud_quicksort.py -v`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add crud/quicksort.py tests/test_crud_quicksort.py
git commit -m "feat: add quicksort for CRUD record listing"
git push
```

---

### Task 4: CRUD 리포지토리 (`crud/repository.py`)

**Files:**
- Create: `crud/repository.py`
- Test: `tests/test_crud_repository.py`

**Interfaces:**
- Consumes:
  - `car_assembly.car_type.CarType` (enum, 값 1/2/3)
  - `crud.storage.load_cars(path) -> list[dict]`, `save_cars(cars, path) -> None`, `DEFAULT_DATA_FILE`
  - `crud.quicksort.quicksort(items, key) -> list[dict]`
- Produces (Task 5의 `crud_app.py`가 사용):
  - `is_valid_combination(car_type: int, engine_code: int, brake_code: int, steering_code: int) -> tuple[bool, str | None]` — 유효하면 `(True, None)`, 아니면 `(False, "사유 메시지")`
  - `next_id(cars: list[dict]) -> int`
  - `create_car(car_type: int, engine_code: int, brake_code: int, steering_code: int, path: str = DEFAULT_DATA_FILE) -> tuple[dict | None, str | None]` — 성공 시 `(레코드, None)`, 부적합 조합이면 `(None, "사유 메시지")`
  - `list_cars(sort_key: str = "id", path: str = DEFAULT_DATA_FILE) -> list[dict]`
  - `find_car(car_id: int, path: str = DEFAULT_DATA_FILE) -> dict | None`
  - `update_car(car_id: int, field: str, value: int, path: str = DEFAULT_DATA_FILE) -> tuple[dict | None, str | None]` — 성공 시 `(수정된 레코드, None)`, ID 없으면 `(None, "해당 ID 없음")`, 부적합 조합이면 `(None, "사유 메시지")`
  - `delete_car(car_id: int, path: str = DEFAULT_DATA_FILE) -> bool` — 삭제 성공 True, ID 없으면 False

- [ ] **Step 1: Write the failing test**

```python
# tests/test_crud_repository.py
import os

import pytest

from crud.repository import (
    create_car,
    delete_car,
    find_car,
    is_valid_combination,
    list_cars,
    next_id,
    update_car,
)


@pytest.fixture
def data_path(tmp_path):
    return os.path.join(tmp_path, "cars.json")


def test_is_valid_combination_rejects_sedan_continental():
    valid, reason = is_valid_combination(1, 1, 2, 1)
    assert valid is False
    assert reason == "Sedan에는 Continental제동장치 사용 불가"


def test_is_valid_combination_rejects_suv_toyota():
    valid, reason = is_valid_combination(2, 2, 1, 1)
    assert valid is False
    assert reason == "SUV에는 TOYOTA엔진 사용 불가"


def test_is_valid_combination_rejects_truck_wia():
    valid, reason = is_valid_combination(3, 3, 3, 1)
    assert valid is False
    assert reason == "Truck에는 WIA엔진 사용 불가"


def test_is_valid_combination_rejects_truck_mando():
    valid, reason = is_valid_combination(3, 1, 1, 1)
    assert valid is False
    assert reason == "Truck에는 Mando제동장치 사용 불가"


def test_is_valid_combination_rejects_bosch_brake_non_bosch_steering():
    valid, reason = is_valid_combination(2, 1, 3, 2)
    assert valid is False
    assert reason == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


def test_is_valid_combination_accepts_valid_combo():
    valid, reason = is_valid_combination(1, 1, 1, 1)
    assert valid is True
    assert reason is None


def test_next_id_empty_list():
    assert next_id([]) == 1


def test_next_id_increments_from_max():
    cars = [{"id": 1}, {"id": 3}, {"id": 2}]
    assert next_id(cars) == 4


def test_create_car_assigns_incrementing_id(data_path):
    first, err1 = create_car(1, 1, 1, 1, path=data_path)
    second, err2 = create_car(2, 1, 3, 1, path=data_path)

    assert err1 is None
    assert err2 is None
    assert first["id"] == 1
    assert second["id"] == 2


def test_create_car_rejects_invalid_combination(data_path):
    car, err = create_car(1, 1, 2, 1, path=data_path)

    assert car is None
    assert err == "Sedan에는 Continental제동장치 사용 불가"
    assert list_cars(path=data_path) == []


def test_list_cars_sorted_by_key(data_path):
    create_car(3, 1, 1, 1, path=data_path)
    create_car(1, 1, 1, 1, path=data_path)
    create_car(2, 1, 1, 1, path=data_path)

    result = list_cars(sort_key="car_type", path=data_path)

    assert [car["car_type"] for car in result] == [1, 2, 3]


def test_find_car_existing_and_missing(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    assert find_car(created["id"], path=data_path) == created
    assert find_car(999, path=data_path) is None


def test_update_car_modifies_field(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    updated, err = update_car(created["id"], "brake_code", 3, path=data_path)

    assert err is None
    assert updated["brake_code"] == 3
    assert find_car(created["id"], path=data_path)["brake_code"] == 3


def test_update_car_missing_id(data_path):
    updated, err = update_car(999, "brake_code", 3, path=data_path)

    assert updated is None
    assert err == "해당 ID 없음"


def test_update_car_rejects_invalid_combination(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    updated, err = update_car(created["id"], "brake_code", 2, path=data_path)

    assert updated is None
    assert err == "Sedan에는 Continental제동장치 사용 불가"
    assert find_car(created["id"], path=data_path)["brake_code"] == 1


def test_delete_car_existing_and_missing(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    assert delete_car(created["id"], path=data_path) is True
    assert find_car(created["id"], path=data_path) is None
    assert delete_car(created["id"], path=data_path) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_crud_repository.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'crud.repository'`

- [ ] **Step 3: Write minimal implementation**

```python
# crud/repository.py
from car_assembly.car_type import CarType
from crud.quicksort import quicksort
from crud.storage import DEFAULT_DATA_FILE, load_cars, save_cars

SEDAN = CarType.SEDAN.value
SUV = CarType.SUV.value
TRUCK = CarType.TRUCK.value

TOYOTA_ENGINE = 2
WIA_ENGINE = 3

MANDO_BRAKE = 1
CONTINENTAL_BRAKE = 2
BOSCH_BRAKE = 3

BOSCH_STEERING = 1


def is_valid_combination(car_type, engine_code, brake_code, steering_code):
    if car_type == SEDAN and brake_code == CONTINENTAL_BRAKE:
        return False, "Sedan에는 Continental제동장치 사용 불가"
    if car_type == SUV and engine_code == TOYOTA_ENGINE:
        return False, "SUV에는 TOYOTA엔진 사용 불가"
    if car_type == TRUCK and engine_code == WIA_ENGINE:
        return False, "Truck에는 WIA엔진 사용 불가"
    if car_type == TRUCK and brake_code == MANDO_BRAKE:
        return False, "Truck에는 Mando제동장치 사용 불가"
    if brake_code == BOSCH_BRAKE and steering_code != BOSCH_STEERING:
        return False, "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"
    return True, None


def next_id(cars):
    if not cars:
        return 1
    return max(car["id"] for car in cars) + 1


def create_car(car_type, engine_code, brake_code, steering_code, path=DEFAULT_DATA_FILE):
    valid, reason = is_valid_combination(car_type, engine_code, brake_code, steering_code)
    if not valid:
        return None, reason

    cars = load_cars(path)
    car = {
        "id": next_id(cars),
        "car_type": car_type,
        "engine_code": engine_code,
        "brake_code": brake_code,
        "steering_code": steering_code,
    }
    cars.append(car)
    save_cars(cars, path)
    return car, None


def list_cars(sort_key="id", path=DEFAULT_DATA_FILE):
    return quicksort(load_cars(path), sort_key)


def find_car(car_id, path=DEFAULT_DATA_FILE):
    for car in load_cars(path):
        if car["id"] == car_id:
            return car
    return None


def update_car(car_id, field, value, path=DEFAULT_DATA_FILE):
    cars = load_cars(path)
    target = None
    for car in cars:
        if car["id"] == car_id:
            target = car
            break

    if target is None:
        return None, "해당 ID 없음"

    candidate = dict(target)
    candidate[field] = value
    valid, reason = is_valid_combination(
        candidate["car_type"],
        candidate["engine_code"],
        candidate["brake_code"],
        candidate["steering_code"],
    )
    if not valid:
        return None, reason

    target[field] = value
    save_cars(cars, path)
    return target, None


def delete_car(car_id, path=DEFAULT_DATA_FILE):
    cars = load_cars(path)
    remaining = [car for car in cars if car["id"] != car_id]

    if len(remaining) == len(cars):
        return False

    save_cars(remaining, path)
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_crud_repository.py -v`
Expected: PASS (16 passed)

- [ ] **Step 5: Commit**

```bash
git add crud/repository.py tests/test_crud_repository.py
git commit -m "feat: add CRUD repository for car records"
git push
```

---

### Task 5: 콘솔 메뉴 앱 (`crud/crud_app.py`)

**Files:**
- Create: `crud/crud_app.py`

**Interfaces:**
- Consumes:
  - `car_assembly.car_type.CarType`, `CAR_TYPE_LABEL`
  - `car_assembly.parts.ENGINE_BY_CODE`, `BRAKE_BY_CODE`
  - `car_assembly.steering.STEERING_BY_CODE`
  - `crud.repository.create_car`, `list_cars`, `find_car`, `update_car`, `delete_car`
- Produces: `main()` — 콘솔 진입점 (`python -m crud.crud_app`로 실행). 자동 테스트 대상 아님(대화형 I/O) — 수동 실행으로 검증.

이 태스크는 대화형 콘솔이라 자동 테스트를 작성하지 않는다. 모든 판정/저장 로직은 이미 Task 4에서 테스트된 `repository.py`에 있고, 이 파일은 입출력만 담당한다. Step 4에서 수동 실행 시나리오로 검증한다.

- [ ] **Step 1: Write the implementation**

```python
# crud/crud_app.py
import sys

from car_assembly.car_type import CAR_TYPE_LABEL, CarType
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE
from car_assembly.steering import STEERING_BY_CODE
from crud.repository import create_car, delete_car, find_car, list_cars, update_car

CLEAR_SCREEN = "\033[H\033[2J"

FIELD_LABEL = {
    "car_type": "차종",
    "engine_code": "엔진",
    "brake_code": "제동장치",
    "steering_code": "조향장치",
}


def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()


def read_int(prompt, low, high):
    while True:
        buf = input(prompt).strip()
        if buf == "exit":
            return None
        try:
            value = int(buf)
        except ValueError:
            print(f"ERROR :: {low} ~ {high} 범위의 숫자만 입력 가능")
            continue
        if value < low or value > high:
            print(f"ERROR :: {low} ~ {high} 범위만 선택 가능")
            continue
        return value


def describe_car(car):
    car_type_label = CAR_TYPE_LABEL[CarType(car["car_type"])]
    engine_label = ENGINE_BY_CODE[car["engine_code"]]().label
    brake_label = BRAKE_BY_CODE[car["brake_code"]]().label
    steering_label = STEERING_BY_CODE[car["steering_code"]]
    return (
        f"ID={car['id']} | 차종={car_type_label} | 엔진={engine_label} | "
        f"제동장치={brake_label} | 조향장치={steering_label}"
    )


def prompt_car_type():
    print("어떤 차량 타입을 선택할까요?")
    print("1. Sedan")
    print("2. SUV")
    print("3. Truck")
    return read_int("INPUT > ", 1, 3)


def prompt_engine():
    print("어떤 엔진을 탑재할까요?")
    print("1. GM")
    print("2. TOYOTA")
    print("3. WIA")
    print("4. 고장난 엔진")
    return read_int("INPUT > ", 1, 4)


def prompt_brake():
    print("어떤 제동장치를 선택할까요?")
    print("1. MANDO")
    print("2. CONTINENTAL")
    print("3. BOSCH")
    return read_int("INPUT > ", 1, 3)


def prompt_steering():
    print("어떤 조향장치를 선택할까요?")
    print("1. BOSCH")
    print("2. MOBIS")
    return read_int("INPUT > ", 1, 2)


def do_create():
    clear()
    car_type = prompt_car_type()
    if car_type is None:
        return
    engine_code = prompt_engine()
    if engine_code is None:
        return
    brake_code = prompt_brake()
    if brake_code is None:
        return
    steering_code = prompt_steering()
    if steering_code is None:
        return

    car, err = create_car(car_type, engine_code, brake_code, steering_code)
    if err is not None:
        print(f"ERROR :: {err}")
    else:
        print(f"생성됨 -> {describe_car(car)}")
    input("계속하려면 Enter > ")


def do_read():
    clear()
    print("1. 전체 목록")
    print("2. ID로 검색")
    choice = read_int("INPUT > ", 1, 2)
    if choice is None:
        return

    if choice == 1:
        print("정렬 기준을 선택하세요")
        print("1. id  2. car_type  3. engine_code  4. brake_code  5. steering_code")
        sort_choice = read_int("INPUT > ", 1, 5)
        if sort_choice is None:
            return
        sort_key = ["id", "car_type", "engine_code", "brake_code", "steering_code"][sort_choice - 1]
        cars = list_cars(sort_key=sort_key)
        if not cars:
            print("등록된 데이터 없음")
        for car in cars:
            print(describe_car(car))
    else:
        car_id = read_int("검색할 ID > ", 1, 10**9)
        if car_id is None:
            return
        car = find_car(car_id)
        print(describe_car(car) if car else "해당 ID 없음")

    input("계속하려면 Enter > ")


def do_update():
    clear()
    car_id = read_int("수정할 ID > ", 1, 10**9)
    if car_id is None:
        return
    car = find_car(car_id)
    if car is None:
        print("해당 ID 없음")
        input("계속하려면 Enter > ")
        return

    print(describe_car(car))
    print("수정할 필드를 선택하세요")
    print("1. car_type  2. engine_code  3. brake_code  4. steering_code")
    field_choice = read_int("INPUT > ", 1, 4)
    if field_choice is None:
        return
    field = ["car_type", "engine_code", "brake_code", "steering_code"][field_choice - 1]

    prompt_by_field = {
        "car_type": prompt_car_type,
        "engine_code": prompt_engine,
        "brake_code": prompt_brake,
        "steering_code": prompt_steering,
    }
    new_value = prompt_by_field[field]()
    if new_value is None:
        return

    updated, err = update_car(car_id, field, new_value)
    if err is not None:
        print(f"ERROR :: {err}")
    else:
        print(f"수정됨 -> {describe_car(updated)}")
    input("계속하려면 Enter > ")


def do_delete():
    clear()
    car_id = read_int("삭제할 ID > ", 1, 10**9)
    if car_id is None:
        return
    car = find_car(car_id)
    if car is None:
        print("해당 ID 없음")
        input("계속하려면 Enter > ")
        return

    print(describe_car(car))
    confirm = input("정말 삭제할까요? (y/n) > ").strip().lower()
    if confirm == "y":
        delete_car(car_id)
        print("삭제됨")
    else:
        print("취소됨")
    input("계속하려면 Enter > ")


def main():
    while True:
        clear()
        print("메인 메뉴")
        print("1. Create")
        print("2. Read")
        print("3. Update")
        print("4. Delete")
        print("5. Exit")
        choice = input("INPUT > ").strip()

        if choice == "exit" or choice == "5":
            print("바이바이")
            break
        try:
            choice_num = int(choice)
        except ValueError:
            continue
        if choice_num == 1:
            do_create()
        elif choice_num == 2:
            do_read()
        elif choice_num == 3:
            do_update()
        elif choice_num == 4:
            do_delete()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Manual verification**

Run: `python -m crud.crud_app`

Manually exercise:
1. Create a Sedan / GM / MANDO / BOSCH combination -> confirm "생성됨" message with ID 1
2. Create a Sedan / GM / CONTINENTAL combination -> confirm rejected with "Sedan에는 Continental제동장치 사용 불가"
3. Read -> 전체 목록, 정렬 기준 `car_type` 선택 -> confirm list printed
4. Read -> ID로 검색, 존재하는 ID -> confirm record printed; 존재하지 않는 ID -> confirm "해당 ID 없음"
5. Update -> 존재하는 ID, `brake_code`를 BOSCH로 변경 후 조향장치가 MOBIS인 상태라면 거부 메시지 확인
6. Delete -> 존재하는 ID 삭제 후 Read로 재확인, 존재하지 않는 ID 삭제 시도 시 "해당 ID 없음" 확인
7. `crud/data/cars.json` 파일 내용이 각 조작마다 갱신되는지 확인

- [ ] **Step 3: Commit**

```bash
git add crud/crud_app.py
git commit -m "feat: add CRUD console menu app"
git push
```

---

### Task 6: `.gitignore`에 런타임 데이터 파일 제외 추가

**Files:**
- Modify: `.gitignore`

**Interfaces:**
- Consumes: 없음
- Produces: 없음 (빌드/저장소 설정만 변경)

- [ ] **Step 1: Add ignore rule**

`.gitignore` 파일 끝에 아래 줄 추가:

```
crud/data/cars.json
```

- [ ] **Step 2: Verify**

Run: `git status`
Expected: `crud/data/cars.json`이 untracked/ignored로 표시되고 (테스트 실행 중 생성됐다면) staged 대상에 안 잡힘.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore CRUD runtime data file"
git push
```

---

## Self-Review Notes

- **Spec coverage:** Create/Read(전체+검색)/Update/Delete 전부 Task 4~5에서 구현. QuickSort(Task 3), JSON 저장(Task 2), car-assembly 도메인 재사용(Task 1, 4), 부적합 조합 검사(Task 4), 자동 증가 ID(Task 4), 에러 처리(ID 없음/범위 밖 입력, Task 4~5) 모두 커버됨.
- **Placeholder scan:** 없음 — 모든 스텝에 실제 코드 포함.
- **Type consistency:** `create_car`/`update_car`가 `(record|None, error|None)` 튜플을 일관되게 반환하고, `crud_app.py`는 이 계약대로 언패킹함. `list_cars(sort_key=...)`와 `quicksort(items, key)` 시그니처 일치.
