# 자동차 조립 시뮬레이터 리팩토링 계획

> **실행 방법:** superpowers:subagent-driven-development (추천) 또는 superpowers:executing-plans 로 태스크 단위 진행. 체크박스(`- [ ]`)로 진행상황 추적.

**목표:** 절차지향 단일 파일(`assembly.py`)을, 동작(콘솔 UI/판정 결과)은 완전히 동일하게 유지한 채 유지보수 가능한 구조로 재구성하고 pytest 테스트를 도입한다.

**아키텍처:** 도메인 값(차량 타입/부품)은 `Enum`으로, 호환성 규칙은 단일 규칙 테이블(`RULES`)로 통합해 `run`/`test` 양쪽에서 재사용. 상태 전이(단계 이동)는 입출력과 분리된 순수 함수로 추출해 `input()` 없이 테스트 가능하게 한다. CLI 루프는 이 두 계층을 조합만 한다.

**Tech Stack:** Python 표준 라이브러리만 사용(외부 의존성 없음), pytest.

## Global Constraints (PRD.md 기준, 모든 태스크 공통)

- 콘솔 메뉴 텍스트, 한글 안내 메시지, 입력 처리 방식(숫자 입력 / `0` 뒤로가기 / `exit` 종료)은 리팩토링 전후 **한 글자도 다르지 않게** 유지
- 호환성 판정 결과(`run`/`test` 양쪽) 동일
- pytest 기반 유닛테스트, 호환성 규칙 + 상태 전이 커버리지 확보
- 확장 시 코드 수정은 허용하되, 규칙은 한 곳에서만 관리(중복 수정 금지)
- Out of scope: 신규 차량 타입/부품 실제 추가, UI/UX 변경, 다국어화

---

## 파일 구조

```
car_assembly/
  __init__.py
  types.py          # CarType, Engine, Brake, Steering Enum
  compatibility.py  # RULES 테이블 + first_incompatibility()
  car.py            # CarBuild 데이터클래스 (선택 상태 보관)
  cli.py            # 메뉴 출력, 상태 전이, main() 루프
assembly.py         # 얇은 entry point: cli.main() 호출만
tests/
  test_compatibility.py
  test_car.py
  test_cli_state.py
```

기존 `assembly.py`의 텍스트/로직은 전부 위 파일들로 이동하고, `assembly.py`는 entry point만 남긴다.

---

### Task 1: 도메인 Enum 추출 (`car_assembly/types.py`)

**Files:**
- Create: `car_assembly/__init__.py` (빈 파일)
- Create: `car_assembly/types.py`
- Test: `tests/test_car.py` (이 태스크에서는 Enum 값만 검증하는 부분 작성)

**Interfaces:**
- Produces: `CarType`(SEDAN=1, SUV=2, TRUCK=3), `Engine`(GM=1, TOYOTA=2, WIA=3, BROKEN=4), `Brake`(MANDO=1, CONTINENTAL=2, BOSCH=3), `Steering`(BOSCH=1, MOBIS=2) — 이후 모든 태스크가 이 이름으로 import.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_car.py` 새로 생성:

```python
from car_assembly.types import CarType, Engine, Brake, Steering


def test_car_type_values():
    assert CarType.SEDAN == 1
    assert CarType.SUV == 2
    assert CarType.TRUCK == 3


def test_engine_values():
    assert Engine.GM == 1
    assert Engine.TOYOTA == 2
    assert Engine.WIA == 3
    assert Engine.BROKEN == 4


def test_brake_values():
    assert Brake.MANDO == 1
    assert Brake.CONTINENTAL == 2
    assert Brake.BOSCH == 3


def test_steering_values():
    assert Steering.BOSCH == 1
    assert Steering.MOBIS == 2
```

- [ ] **Step 2: 실패 확인**

실행: `pytest tests/test_car.py -v`
예상: `ModuleNotFoundError: No module named 'car_assembly'`로 실패

- [ ] **Step 3: 구현**

`car_assembly/__init__.py`:

```python
```

(빈 파일)

`car_assembly/types.py`:

```python
from enum import IntEnum


class CarType(IntEnum):
    SEDAN = 1
    SUV = 2
    TRUCK = 3


class Engine(IntEnum):
    GM = 1
    TOYOTA = 2
    WIA = 3
    BROKEN = 4


class Brake(IntEnum):
    MANDO = 1
    CONTINENTAL = 2
    BOSCH = 3


class Steering(IntEnum):
    BOSCH = 1
    MOBIS = 2
```

- [ ] **Step 4: 통과 확인**

실행: `pytest tests/test_car.py -v`
예상: PASS 4개

- [ ] **Step 5: 커밋**

```bash
git add car_assembly/__init__.py car_assembly/types.py tests/test_car.py
git commit -m "refactor: extract domain enums into car_assembly.types"
```

---

### Task 2: 호환성 규칙 단일화 (`car_assembly/compatibility.py`)

**Files:**
- Create: `car_assembly/compatibility.py`
- Create: `car_assembly/car.py` (이 태스크에서는 `CarBuild`의 필드만 정의, 규칙 판정에 필요한 최소 형태)
- Test: `tests/test_compatibility.py`

**Interfaces:**
- Consumes: `car_assembly.types`의 `CarType`, `Engine`, `Brake`, `Steering` (Task 1)
- Produces: `car_assembly.car.CarBuild(car_type, engine, brake, steering)` 데이터클래스, `car_assembly.compatibility.first_incompatibility(build) -> str | None` — Task 3(run/test 로직)과 Task 4(CLI)가 그대로 사용.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_compatibility.py` 새로 생성:

```python
import pytest

from car_assembly.car import CarBuild
from car_assembly.compatibility import first_incompatibility
from car_assembly.types import Brake, CarType, Engine, Steering


def make(car_type, engine, brake, steering):
    return CarBuild(car_type=car_type, engine=engine, brake=brake, steering=steering)


def test_sedan_continental_incompatible():
    build = make(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    assert first_incompatibility(build) == "Sedan에는 Continental제동장치 사용 불가"


def test_suv_toyota_incompatible():
    build = make(CarType.SUV, Engine.TOYOTA, Brake.MANDO, Steering.MOBIS)
    assert first_incompatibility(build) == "SUV에는 TOYOTA엔진 사용 불가"


def test_truck_wia_incompatible():
    build = make(CarType.TRUCK, Engine.WIA, Brake.CONTINENTAL, Steering.MOBIS)
    assert first_incompatibility(build) == "Truck에는 WIA엔진 사용 불가"


def test_truck_mando_incompatible():
    build = make(CarType.TRUCK, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert first_incompatibility(build) == "Truck에는 Mando제동장치 사용 불가"


def test_bosch_brake_requires_bosch_steering():
    build = make(CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.MOBIS)
    assert first_incompatibility(build) == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


def test_bosch_brake_with_bosch_steering_is_compatible():
    build = make(CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.BOSCH)
    assert first_incompatibility(build) is None


def test_valid_combination_has_no_incompatibility():
    build = make(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert first_incompatibility(build) is None


def test_first_match_wins_when_multiple_rules_violated():
    # Truck + WIA(엔진 규칙) + Mando(제동장치 규칙) 동시 위반 -> 원본 elif 순서상 WIA 메시지가 먼저 잡힘
    build = make(CarType.TRUCK, Engine.WIA, Brake.MANDO, Steering.MOBIS)
    assert first_incompatibility(build) == "Truck에는 WIA엔진 사용 불가"
```

- [ ] **Step 2: 실패 확인**

실행: `pytest tests/test_compatibility.py -v`
예상: `ModuleNotFoundError: No module named 'car_assembly.car'`로 실패

- [ ] **Step 3: 구현**

`car_assembly/car.py`:

```python
from dataclasses import dataclass
from typing import Optional

from car_assembly.types import Brake, CarType, Engine, Steering


@dataclass
class CarBuild:
    car_type: Optional[CarType] = None
    engine: Optional[Engine] = None
    brake: Optional[Brake] = None
    steering: Optional[Steering] = None

    def is_engine_broken(self) -> bool:
        return self.engine == Engine.BROKEN
```

`car_assembly/compatibility.py`:

```python
from typing import Callable, NamedTuple, Optional

from car_assembly.car import CarBuild
from car_assembly.types import Brake, CarType, Engine, Steering


class Rule(NamedTuple):
    predicate: Callable[[CarBuild], bool]
    message: str


# 순서가 원본 test_produced_car()의 elif 순서와 동일해야
# 여러 규칙이 동시에 위반됐을 때도 같은 메시지가 출력된다.
RULES = [
    Rule(
        lambda b: b.car_type == CarType.SEDAN and b.brake == Brake.CONTINENTAL,
        "Sedan에는 Continental제동장치 사용 불가",
    ),
    Rule(
        lambda b: b.car_type == CarType.SUV and b.engine == Engine.TOYOTA,
        "SUV에는 TOYOTA엔진 사용 불가",
    ),
    Rule(
        lambda b: b.car_type == CarType.TRUCK and b.engine == Engine.WIA,
        "Truck에는 WIA엔진 사용 불가",
    ),
    Rule(
        lambda b: b.car_type == CarType.TRUCK and b.brake == Brake.MANDO,
        "Truck에는 Mando제동장치 사용 불가",
    ),
    Rule(
        lambda b: b.brake == Brake.BOSCH and b.steering != Steering.BOSCH,
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ),
]


def first_incompatibility(build: CarBuild) -> Optional[str]:
    for rule in RULES:
        if rule.predicate(build):
            return rule.message
    return None
```

- [ ] **Step 4: 통과 확인**

실행: `pytest tests/test_compatibility.py -v`
예상: PASS 8개

- [ ] **Step 5: 커밋**

```bash
git add car_assembly/car.py car_assembly/compatibility.py tests/test_compatibility.py
git commit -m "refactor: unify compatibility rules into single RULES table"
```

---

### Task 3: `CarBuild` 실행/테스트 메서드 추가

**Files:**
- Modify: `car_assembly/car.py`
- Test: `tests/test_car.py` (기존 파일에 추가)

**Interfaces:**
- Consumes: `car_assembly.compatibility.first_incompatibility` (Task 2)
- Produces: `CarBuild.is_compatible() -> bool`, `CarBuild.run_report() -> list[str]`, `CarBuild.test_report() -> str` — Task 4(cli.py)가 그대로 호출.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_car.py`에 추가:

```python
from car_assembly.car import CarBuild
from car_assembly.types import Brake, CarType, Engine, Steering


def test_is_compatible_true_for_valid_build():
    build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert build.is_compatible() is True


def test_is_compatible_false_for_invalid_build():
    build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    assert build.is_compatible() is False


def test_run_report_incompatible():
    build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    assert build.run_report() == ["자동차가 동작되지 않습니다"]


def test_run_report_broken_engine():
    build = CarBuild(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    assert build.run_report() == ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]


def test_run_report_success():
    build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert build.run_report() == [
        "Car Type : Sedan",
        "Engine   : GM",
        "Brake    : Mando",
        "Steering : Mobis",
        "자동차가 동작됩니다.",
    ]


def test_test_report_fail():
    build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
    assert build.test_report() == "FAIL\nSedan에는 Continental제동장치 사용 불가"


def test_test_report_pass():
    build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
    assert build.test_report() == "PASS"


def test_test_report_pass_even_with_broken_engine():
    # 원본 test_produced_car()는 엔진 고장 여부를 검사하지 않는다 — 동작 보존 대상 quirk
    build = CarBuild(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
    assert build.test_report() == "PASS"
```

- [ ] **Step 2: 실패 확인**

실행: `pytest tests/test_car.py -v`
예상: `AttributeError: 'CarBuild' object has no attribute 'is_compatible'` 등으로 실패

- [ ] **Step 3: 구현**

`car_assembly/car.py` 전체를 아래로 교체:

```python
from dataclasses import dataclass
from typing import Optional

from car_assembly.compatibility import first_incompatibility
from car_assembly.types import Brake, CarType, Engine, Steering

_CAR_TYPE_LABEL = {CarType.SEDAN: "Sedan", CarType.SUV: "SUV", CarType.TRUCK: "Truck"}
_ENGINE_LABEL = {Engine.GM: "GM", Engine.TOYOTA: "TOYOTA", Engine.WIA: "WIA"}
_BRAKE_LABEL = {Brake.MANDO: "Mando", Brake.CONTINENTAL: "Continental", Brake.BOSCH: "Bosch"}
_STEERING_LABEL = {Steering.BOSCH: "Bosch", Steering.MOBIS: "Mobis"}


@dataclass
class CarBuild:
    car_type: Optional[CarType] = None
    engine: Optional[Engine] = None
    brake: Optional[Brake] = None
    steering: Optional[Steering] = None

    def is_engine_broken(self) -> bool:
        return self.engine == Engine.BROKEN

    def is_compatible(self) -> bool:
        return first_incompatibility(self) is None

    def run_report(self) -> list[str]:
        if not self.is_compatible():
            return ["자동차가 동작되지 않습니다"]
        if self.is_engine_broken():
            return ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]

        lines = [f"Car Type : {_CAR_TYPE_LABEL[self.car_type]}"]
        if self.engine in _ENGINE_LABEL:
            lines.append(f"Engine   : {_ENGINE_LABEL[self.engine]}")
        lines.append(f"Brake    : {_BRAKE_LABEL[self.brake]}")
        lines.append(f"Steering : {_STEERING_LABEL[self.steering]}")
        lines.append("자동차가 동작됩니다.")
        return lines

    def test_report(self) -> str:
        message = first_incompatibility(self)
        if message is None:
            return "PASS"
        return f"FAIL\n{message}"
```

- [ ] **Step 4: 통과 확인**

실행: `pytest tests/test_car.py -v`
예상: PASS 전부

- [ ] **Step 5: 커밋**

```bash
git add car_assembly/car.py tests/test_car.py
git commit -m "feat: add CarBuild.run_report/test_report matching original output"
```

---

### Task 4: 상태 전이 순수 함수 추출 (`car_assembly/cli.py` 일부)

원본 `main()`의 `step` 이동 로직(뒤로가기 포함)을 `input()` 없이 테스트 가능한 순수 함수로 분리한다.

**Files:**
- Create: `car_assembly/cli.py` (이 태스크에서는 상태 전이 함수만)
- Test: `tests/test_cli_state.py`

**Interfaces:**
- Produces: `car_assembly.cli.advance_step(step: int, ans: int) -> int` — Task 5(main 루프)가 그대로 사용. 규칙: `ans == 0`이면 `step == 4`일 때 `0`, 그 외 `step > 0`이면 `step - 1`, `step == 0`이면 유지(원본과 동일하게 이동 없음). `ans != 0`이면 `step`이 0~3일 때 `step + 1`, `step == 4`일 때는 유지(run/test는 화면 전환 없음).

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_cli_state.py` 새로 생성:

```python
from car_assembly.cli import advance_step


def test_back_navigation_from_step4_goes_to_0():
    assert advance_step(4, 0) == 0


def test_back_navigation_decrements_step():
    assert advance_step(2, 0) == 1
    assert advance_step(1, 0) == 0


def test_back_navigation_at_step0_stays():
    assert advance_step(0, 0) == 0


def test_forward_navigation_increments_step():
    assert advance_step(0, 1) == 1
    assert advance_step(1, 2) == 2
    assert advance_step(2, 3) == 3
    assert advance_step(3, 1) == 4


def test_step4_non_zero_answer_stays_on_step4():
    assert advance_step(4, 1) == 4
    assert advance_step(4, 2) == 4
```

- [ ] **Step 2: 실패 확인**

실행: `pytest tests/test_cli_state.py -v`
예상: `ModuleNotFoundError: No module named 'car_assembly.cli'`로 실패

- [ ] **Step 3: 구현**

`car_assembly/cli.py` 새로 생성 (이 태스크 범위만 작성, 다음 태스크에서 이어서 채움):

```python
def advance_step(step: int, ans: int) -> int:
    if ans == 0:
        if step == 4:
            return 0
        if step > 0:
            return step - 1
        return step
    if step in (0, 1, 2, 3):
        return step + 1
    return step
```

- [ ] **Step 4: 통과 확인**

실행: `pytest tests/test_cli_state.py -v`
예상: PASS 전부

- [ ] **Step 5: 커밋**

```bash
git add car_assembly/cli.py tests/test_cli_state.py
git commit -m "refactor: extract pure advance_step() state transition function"
```

---

### Task 5: CLI 메뉴/루프 이식 (동작 100% 동일 유지)

원본 `assembly.py`의 `show_menu`, `is_valid_range`, `select_*`, `run_produced_car`, `test_produced_car`, `main`, `delay`, `clear`를 `car_assembly/cli.py`로 옮기고 `CarBuild`/`advance_step`을 사용하도록 바꾼다. 출력 문자열은 원본과 완전히 동일해야 한다.

**Files:**
- Modify: `car_assembly/cli.py`
- Test: 자동화된 유닛테스트로 `input()`을 감쌀 필요는 없음 — 이 태스크의 검증은 Task 7 수동 회귀 테스트에서 수행(아래 "Step 2" 참고, 텍스트 출력물이 크고 `time.sleep`/화면 클리어를 포함해 유닛테스트 가치가 낮음). 대신 아래 Step 1에서 `select_*` 함수들의 반환 문자열을 유닛테스트로 고정한다.

**Interfaces:**
- Consumes: `CarBuild`(Task 3), `advance_step`(Task 4), `CarType/Engine/Brake/Steering`(Task 1)
- Produces: `car_assembly.cli.main()` — `assembly.py`(Task 6)가 그대로 호출.

- [ ] **Step 1: `select_*` 안내 메시지 실패 테스트 작성**

`tests/test_cli_state.py`에 추가:

```python
from car_assembly.cli import selection_message
from car_assembly.types import Brake, CarType, Engine, Steering


def test_selection_message_car_type():
    assert selection_message("car_type", CarType.SEDAN) == "차량 타입으로 Sedan을 선택하셨습니다."
    assert selection_message("car_type", CarType.SUV) == "차량 타입으로 SUV을 선택하셨습니다."
    assert selection_message("car_type", CarType.TRUCK) == "차량 타입으로 Truck을 선택하셨습니다."


def test_selection_message_engine():
    assert selection_message("engine", Engine.GM) == "GM 엔진을 선택하셨습니다."
    assert selection_message("engine", Engine.TOYOTA) == "TOYOTA 엔진을 선택하셨습니다."
    assert selection_message("engine", Engine.WIA) == "WIA 엔진을 선택하셨습니다."
    assert selection_message("engine", Engine.BROKEN) == "고장난 엔진을 선택하셨습니다."


def test_selection_message_brake():
    assert selection_message("brake", Brake.MANDO) == "MANDO 제동장치를 선택하셨습니다."
    assert selection_message("brake", Brake.CONTINENTAL) == "CONTINENTAL 제동장치를 선택하셨습니다."
    assert selection_message("brake", Brake.BOSCH) == "BOSCH 제동장치를 선택하셨습니다."


def test_selection_message_steering():
    assert selection_message("steering", Steering.BOSCH) == "BOSCH 조향장치를 선택하셨습니다."
    assert selection_message("steering", Steering.MOBIS) == "MOBIS 조향장치를 선택하셨습니다."
```

- [ ] **Step 2: 실패 확인**

실행: `pytest tests/test_cli_state.py -v`
예상: `ImportError: cannot import name 'selection_message'`로 실패

- [ ] **Step 3: `car_assembly/cli.py` 구현 (전체 교체)**

```python
import sys
import time

from car_assembly.car import CarBuild
from car_assembly.types import Brake, CarType, Engine, Steering

CLEAR_SCREEN = "\033[H\033[2J"

STEP_CAR_TYPE = 0
STEP_ENGINE = 1
STEP_BRAKE = 2
STEP_STEERING = 3
STEP_RUN_TEST = 4

_SELECTION_MESSAGES = {
    "car_type": {
        CarType.SEDAN: "차량 타입으로 Sedan을 선택하셨습니다.",
        CarType.SUV: "차량 타입으로 SUV을 선택하셨습니다.",
        CarType.TRUCK: "차량 타입으로 Truck을 선택하셨습니다.",
    },
    "engine": {
        Engine.GM: "GM 엔진을 선택하셨습니다.",
        Engine.TOYOTA: "TOYOTA 엔진을 선택하셨습니다.",
        Engine.WIA: "WIA 엔진을 선택하셨습니다.",
        Engine.BROKEN: "고장난 엔진을 선택하셨습니다.",
    },
    "brake": {
        Brake.MANDO: "MANDO 제동장치를 선택하셨습니다.",
        Brake.CONTINENTAL: "CONTINENTAL 제동장치를 선택하셨습니다.",
        Brake.BOSCH: "BOSCH 제동장치를 선택하셨습니다.",
    },
    "steering": {
        Steering.BOSCH: "BOSCH 조향장치를 선택하셨습니다.",
        Steering.MOBIS: "MOBIS 조향장치를 선택하셨습니다.",
    },
}


def selection_message(field: str, value) -> str:
    return _SELECTION_MESSAGES[field][value]


def delay(ms):
    time.sleep(ms / 1000.0)


def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()


def advance_step(step: int, ans: int) -> int:
    if ans == 0:
        if step == 4:
            return 0
        if step > 0:
            return step - 1
        return step
    if step in (0, 1, 2, 3):
        return step + 1
    return step


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
            print(selection_message("car_type", build.car_type))
            delay(800)
        elif step == STEP_ENGINE:
            build.engine = Engine(ans)
            print(selection_message("engine", build.engine))
            delay(800)
        elif step == STEP_BRAKE:
            build.brake = Brake(ans)
            print(selection_message("brake", build.brake))
            delay(800)
        elif step == STEP_STEERING:
            build.steering = Steering(ans)
            print(selection_message("steering", build.steering))
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

- [ ] **Step 4: 통과 확인**

실행: `pytest tests/test_cli_state.py -v`
예상: PASS 전부

- [ ] **Step 5: 커밋**

```bash
git add car_assembly/cli.py tests/test_cli_state.py
git commit -m "refactor: move menu loop into car_assembly.cli using CarBuild/advance_step"
```

---

### Task 6: `assembly.py`를 얇은 entry point로 축소

**Files:**
- Modify: `assembly.py` (전체 교체)

**Interfaces:**
- Consumes: `car_assembly.cli.main`(Task 5)

- [ ] **Step 1: `assembly.py` 전체를 아래로 교체**

```python
from car_assembly.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 전체 테스트 스위트 실행**

실행: `pytest -v`
예상: 모든 테스트 PASS (Task 1~5에서 작성한 전부)

- [ ] **Step 3: 커밋**

```bash
git add assembly.py
git commit -m "refactor: slim assembly.py down to a thin entry point"
```

---

### Task 7: 수동 회귀 테스트 (동작 100% 동일 확인) 및 문서 정리

**Files:**
- (코드 변경 없음, 있다면 회귀에서 드러난 문제만 수정)
- Modify: `CLAUDE.md` (명령어 섹션에 `pytest` 실행법 추가)

- [ ] **Step 1: 수동 시나리오 실행**

`python assembly.py` 실행 후 아래 시나리오를 각각 수행하며 리팩토링 전 원본 출력과 비교:
1. Sedan -> GM -> Continental 선택 시 에러 메뉴 재출력 없이 다음 단계로 진행되는지(제동장치 자체 선택은 허용되고, 실제 판정은 RUN/TEST 단계에서 일어남을 확인)
2. Sedan -> GM -> Continental -> Mobis -> RUN 선택 -> "자동차가 동작되지 않습니다" 출력 확인
3. 동일 조합 -> TEST 선택 -> `FAIL` + `Sedan에는 Continental제동장치 사용 불가` 확인
4. Sedan -> 고장난 엔진(4) -> Mando -> Mobis -> RUN -> "엔진이 고장나있습니다." / "자동차가 움직이지 않습니다." 확인
5. 동일 조합 -> TEST -> `PASS` 출력 확인(원본의 quirk 그대로 재현되는지)
6. 각 단계에서 `0` 입력 시 정확히 한 단계 뒤로가기, STEP 4(완성 화면)에서 `0` 입력 시 처음(STEP 0)으로 이동
7. 범위 밖 숫자 입력 시 원본과 동일한 `ERROR ::` 메시지 확인
8. `exit` 입력 시 "바이바이" 출력 후 프로그램 종료 확인

- [ ] **Step 2: `CLAUDE.md`에 테스트 실행 명령 추가**

`## 명령어` 섹션의 실행 항목 아래에 추가:

```markdown
- 테스트 실행: `pytest`
```

- [ ] **Step 3: 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: add pytest command to CLAUDE.md after refactor"
```

- [ ] **Step 4: 푸시**

```bash
git push
```

---

## Self-Review 체크리스트

- PRD.md의 5개 호환성 규칙 전부 Task 2에서 테스트로 커버됨
- "동작 유지" 요구사항은 Task 5의 문자열을 원본과 1:1 대조, Task 7에서 수동 회귀로 재확인
- pytest 요구사항은 Task 1~5에서 각 모듈마다 테스트 작성으로 충족
- 확장성(규칙 단일 관리)은 Task 2의 `RULES` 테이블로 충족 — 새 규칙 추가 시 `RULES`에 항목 하나만 추가하면 `run`/`test` 양쪽에 자동 반영됨
- Out of scope(신규 타입/부품 추가, UI 변경, 다국어화)는 어떤 태스크에도 포함하지 않음
