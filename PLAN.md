# 자동차 조립 시뮬레이터 리팩토링 계획

> **실행 방법:** superpowers:subagent-driven-development (추천) 또는 superpowers:executing-plans 로 태스크 단위 진행. 체크박스(`- [ ]`)로 진행상황 추적.

**목표:** 절차지향 단일 파일(`assembly.py`)을, 동작(콘솔 UI/판정 결과)은 완전히 동일하게 유지한 채 유지보수 가능한 구조로 재구성하고 pytest 테스트를 도입한다.

**아키텍처:** 도메인 값(차량 타입/부품)은 `Enum`으로, 호환성 규칙은 단일 규칙 테이블(`RULES`)로 통합해 `run`/`test` 양쪽에서 재사용. 상태 전이(단계 이동)는 입출력과 분리된 순수 함수로 추출해 `input()` 없이 테스트 가능하게 한다. CLI 루프는 이 두 계층을 조합만 한다.

**Tech Stack:** Python 표준 라이브러리만 사용(외부 의존성 없음), pytest.

## Global Constraints (PRD.md 기준, 모든 Phase 공통)

- 콘솔 메뉴 텍스트, 한글 안내 메시지, 입력 처리 방식(숫자 입력 / `0` 뒤로가기 / `exit` 종료)은 리팩토링 전후 **한 글자도 다르지 않게** 유지
- 호환성 판정 결과(`run`/`test` 양쪽) 동일
- pytest 기반 유닛테스트, 호환성 규칙 + 상태 전이 커버리지 확보
- 확장 시 코드 수정은 허용하되, 규칙은 한 곳에서만 관리(중복 수정 금지)
- Out of scope: 신규 차량 타입/부품 실제 추가, UI/UX 변경, 다국어화

## 파일 구조

```
car_assembly/
  __init__.py
  types.py          # CarType, Engine, Brake, Steering Enum
  compatibility.py  # RULES 테이블 + first_incompatibility()
  car.py            # CarBuild 데이터클래스 (선택 상태 + 리포트)
  cli.py            # 메뉴 출력, 상태 전이, main() 루프
assembly.py         # 얇은 entry point: cli.main() 호출만
tests/
  test_types.py
  test_compatibility.py
  test_car.py
  test_cli_state.py
```

---

## Phase 1: 도메인 Enum 추출 (`car_assembly/types.py`)

기존 상수(`SEDAN=1` 등 모듈 전역 int)를 타입 안전한 `Enum`으로 대체. 이후 모든 Phase가 이 이름으로 import.

- [ ] **1.1 패키지 뼈대 생성**
  - Create: `car_assembly/__init__.py` (빈 파일)
  - 커밋: `git add car_assembly/__init__.py && git commit -m "chore: create car_assembly package"`

- [ ] **1.2 CarType enum**
  - Test 작성 (`tests/test_types.py` 새로 생성):
    ```python
    from car_assembly.types import CarType


    def test_car_type_values():
        assert CarType.SEDAN == 1
        assert CarType.SUV == 2
        assert CarType.TRUCK == 3
    ```
  - 실행: `pytest tests/test_types.py -v` -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/types.py` 새로 생성):
    ```python
    from enum import IntEnum


    class CarType(IntEnum):
        SEDAN = 1
        SUV = 2
        TRUCK = 3
    ```
  - 실행: `pytest tests/test_types.py -v` -> PASS 확인
  - 커밋: `git add car_assembly/types.py tests/test_types.py && git commit -m "feat: add CarType enum"`

- [ ] **1.3 Engine enum**
  - Test 추가 (`tests/test_types.py`):
    ```python
    from car_assembly.types import Engine


    def test_engine_values():
        assert Engine.GM == 1
        assert Engine.TOYOTA == 2
        assert Engine.WIA == 3
        assert Engine.BROKEN == 4
    ```
  - 실행: `pytest tests/test_types.py -v` -> `ImportError`로 실패 확인
  - 구현 (`car_assembly/types.py`에 추가):
    ```python
    class Engine(IntEnum):
        GM = 1
        TOYOTA = 2
        WIA = 3
        BROKEN = 4
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add Engine enum"`

- [ ] **1.4 Brake enum**
  - Test 추가:
    ```python
    from car_assembly.types import Brake


    def test_brake_values():
        assert Brake.MANDO == 1
        assert Brake.CONTINENTAL == 2
        assert Brake.BOSCH == 3
    ```
  - 구현 (`car_assembly/types.py`에 추가):
    ```python
    class Brake(IntEnum):
        MANDO = 1
        CONTINENTAL = 2
        BOSCH = 3
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add Brake enum"`

- [ ] **1.5 Steering enum**
  - Test 추가:
    ```python
    from car_assembly.types import Steering


    def test_steering_values():
        assert Steering.BOSCH == 1
        assert Steering.MOBIS == 2
    ```
  - 구현 (`car_assembly/types.py`에 추가):
    ```python
    class Steering(IntEnum):
        BOSCH = 1
        MOBIS = 2
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add Steering enum"`

---

## Phase 2: `CarBuild` 골격 + 호환성 규칙 단일화

**Interfaces:**
- Consumes: Phase 1의 `CarType/Engine/Brake/Steering`
- Produces: `car_assembly.car.CarBuild(car_type, engine, brake, steering)`, `car_assembly.compatibility.first_incompatibility(build) -> str | None` — 이후 Phase가 그대로 사용.

- [ ] **2.1 `CarBuild` 데이터클래스 골격**
  - Test 작성 (`tests/test_car.py` 새로 생성):
    ```python
    from car_assembly.car import CarBuild
    from car_assembly.types import Brake, CarType, Engine, Steering


    def test_carbuild_holds_selections():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert build.car_type == CarType.SEDAN
        assert build.engine == Engine.GM
        assert build.brake == Brake.MANDO
        assert build.steering == Steering.MOBIS


    def test_carbuild_defaults_to_none():
        build = CarBuild()
        assert build.car_type is None
    ```
  - 실행 -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/car.py` 새로 생성):
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
    ```
  - 실행 -> PASS 확인, 커밋: `git add car_assembly/car.py tests/test_car.py && git commit -m "feat: add CarBuild dataclass skeleton"`

- [ ] **2.2 `is_engine_broken()`**
  - Test 추가 (`tests/test_car.py`):
    ```python
    def test_is_engine_broken_true():
        build = CarBuild(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
        assert build.is_engine_broken() is True


    def test_is_engine_broken_false():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert build.is_engine_broken() is False
    ```
  - 구현 (`CarBuild`에 메서드 추가):
    ```python
        def is_engine_broken(self) -> bool:
            return self.engine == Engine.BROKEN
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.is_engine_broken"`

- [ ] **2.3 규칙 테이블 골격 + 규칙 1 (Sedan/Continental)**
  - Test 작성 (`tests/test_compatibility.py` 새로 생성):
    ```python
    from car_assembly.car import CarBuild
    from car_assembly.compatibility import first_incompatibility
    from car_assembly.types import Brake, CarType, Engine, Steering


    def test_sedan_continental_incompatible():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
        assert first_incompatibility(build) == "Sedan에는 Continental제동장치 사용 불가"


    def test_valid_combination_has_no_incompatibility():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert first_incompatibility(build) is None
    ```
  - 실행 -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/compatibility.py` 새로 생성):
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
    ]


    def first_incompatibility(build: CarBuild) -> Optional[str]:
        for rule in RULES:
            if rule.predicate(build):
                return rule.message
        return None
    ```
  - 실행 -> PASS 확인, 커밋: `git add car_assembly/compatibility.py tests/test_compatibility.py && git commit -m "feat: add RULES table with Sedan/Continental rule"`

- [ ] **2.4 규칙 2 (SUV/Toyota) 추가**
  - Test 추가 (`tests/test_compatibility.py`):
    ```python
    def test_suv_toyota_incompatible():
        build = CarBuild(CarType.SUV, Engine.TOYOTA, Brake.MANDO, Steering.MOBIS)
        assert first_incompatibility(build) == "SUV에는 TOYOTA엔진 사용 불가"
    ```
  - 실행 -> 실패 확인 (매칭 규칙 없어 `None` 반환)
  - 구현 (`RULES` 리스트에 항목 추가):
    ```python
        Rule(
            lambda b: b.car_type == CarType.SUV and b.engine == Engine.TOYOTA,
            "SUV에는 TOYOTA엔진 사용 불가",
        ),
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add SUV/Toyota incompatibility rule"`

- [ ] **2.5 규칙 3 (Truck/WIA) 추가**
  - Test 추가:
    ```python
    def test_truck_wia_incompatible():
        build = CarBuild(CarType.TRUCK, Engine.WIA, Brake.CONTINENTAL, Steering.MOBIS)
        assert first_incompatibility(build) == "Truck에는 WIA엔진 사용 불가"
    ```
  - 구현 (`RULES`에 추가):
    ```python
        Rule(
            lambda b: b.car_type == CarType.TRUCK and b.engine == Engine.WIA,
            "Truck에는 WIA엔진 사용 불가",
        ),
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add Truck/WIA incompatibility rule"`

- [ ] **2.6 규칙 4 (Truck/Mando) 추가**
  - Test 추가:
    ```python
    def test_truck_mando_incompatible():
        build = CarBuild(CarType.TRUCK, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert first_incompatibility(build) == "Truck에는 Mando제동장치 사용 불가"
    ```
  - 구현 (`RULES`에 추가):
    ```python
        Rule(
            lambda b: b.car_type == CarType.TRUCK and b.brake == Brake.MANDO,
            "Truck에는 Mando제동장치 사용 불가",
        ),
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add Truck/Mando incompatibility rule"`

- [ ] **2.7 규칙 5 (Bosch 제동장치/조향장치) 추가**
  - Test 추가:
    ```python
    def test_bosch_brake_requires_bosch_steering():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.MOBIS)
        assert first_incompatibility(build) == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


    def test_bosch_brake_with_bosch_steering_is_compatible():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.BOSCH, Steering.BOSCH)
        assert first_incompatibility(build) is None


    def test_first_match_wins_when_multiple_rules_violated():
        # Truck + WIA(엔진 규칙) + Mando(제동장치 규칙) 동시 위반
        # -> 원본 elif 순서상 WIA 메시지가 먼저 잡힘
        build = CarBuild(CarType.TRUCK, Engine.WIA, Brake.MANDO, Steering.MOBIS)
        assert first_incompatibility(build) == "Truck에는 WIA엔진 사용 불가"
    ```
  - 구현 (`RULES`에 추가):
    ```python
        Rule(
            lambda b: b.brake == Brake.BOSCH and b.steering != Steering.BOSCH,
            "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
        ),
    ```
  - 실행: `pytest tests/test_compatibility.py -v` -> PASS 8개 확인
  - 커밋: `git commit -am "feat: add Bosch brake/steering incompatibility rule"`

---

## Phase 3: `CarBuild` run/test 리포트

**Interfaces:**
- Consumes: Phase 2의 `first_incompatibility`
- Produces: `CarBuild.is_compatible()`, `CarBuild.run_report()`, `CarBuild.test_report()` — Phase 5(cli.py)가 그대로 호출.

- [ ] **3.1 `is_compatible()`**
  - Test 추가 (`tests/test_car.py`):
    ```python
    def test_is_compatible_true_for_valid_build():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert build.is_compatible() is True


    def test_is_compatible_false_for_invalid_build():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
        assert build.is_compatible() is False
    ```
  - 실행 -> `AttributeError`로 실패 확인
  - 구현 (`car_assembly/car.py` 상단에 import 추가 후 메서드 추가):
    ```python
    from car_assembly.compatibility import first_incompatibility
    ```
    ```python
        def is_compatible(self) -> bool:
            return first_incompatibility(self) is None
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.is_compatible"`

- [ ] **3.2 `run_report()` - 비호환 케이스**
  - Test 추가:
    ```python
    def test_run_report_incompatible():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
        assert build.run_report() == ["자동차가 동작되지 않습니다"]
    ```
  - 구현 (메서드 추가, 이후 스텝에서 계속 확장):
    ```python
        def run_report(self) -> list[str]:
            if not self.is_compatible():
                return ["자동차가 동작되지 않습니다"]
            return []
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.run_report incompatible case"`

- [ ] **3.3 `run_report()` - 고장난 엔진 케이스**
  - Test 추가:
    ```python
    def test_run_report_broken_engine():
        build = CarBuild(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
        assert build.run_report() == ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]
    ```
  - 실행 -> 실패 확인 (빈 리스트 반환)
  - 구현 (`run_report` 본문에 추가):
    ```python
            if self.is_engine_broken():
                return ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.run_report broken engine case"`

- [ ] **3.4 `run_report()` - 정상 완성 케이스**
  - Test 추가:
    ```python
    def test_run_report_success():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert build.run_report() == [
            "Car Type : Sedan",
            "Engine   : GM",
            "Brake    : Mando",
            "Steering : Mobis",
            "자동차가 동작됩니다.",
        ]
    ```
  - 실행 -> 실패 확인 (빈 리스트 반환)
  - 구현 (`car_assembly/car.py` 파일 상단에 라벨 딕셔너리 추가):
    ```python
    _CAR_TYPE_LABEL = {CarType.SEDAN: "Sedan", CarType.SUV: "SUV", CarType.TRUCK: "Truck"}
    _ENGINE_LABEL = {Engine.GM: "GM", Engine.TOYOTA: "TOYOTA", Engine.WIA: "WIA"}
    _BRAKE_LABEL = {Brake.MANDO: "Mando", Brake.CONTINENTAL: "Continental", Brake.BOSCH: "Bosch"}
    _STEERING_LABEL = {Steering.BOSCH: "Bosch", Steering.MOBIS: "Mobis"}
    ```
    `run_report` 끝에 추가:
    ```python
            lines = [f"Car Type : {_CAR_TYPE_LABEL[self.car_type]}"]
            if self.engine in _ENGINE_LABEL:
                lines.append(f"Engine   : {_ENGINE_LABEL[self.engine]}")
            lines.append(f"Brake    : {_BRAKE_LABEL[self.brake]}")
            lines.append(f"Steering : {_STEERING_LABEL[self.steering]}")
            lines.append("자동차가 동작됩니다.")
            return lines
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.run_report success case"`

- [ ] **3.5 `test_report()` - FAIL 케이스**
  - Test 추가:
    ```python
    def test_test_report_fail():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.CONTINENTAL, Steering.MOBIS)
        assert build.test_report() == "FAIL\nSedan에는 Continental제동장치 사용 불가"
    ```
  - 실행 -> `AttributeError`로 실패 확인
  - 구현 (메서드 추가):
    ```python
        def test_report(self) -> str:
            message = first_incompatibility(self)
            if message is None:
                return "PASS"
            return f"FAIL\n{message}"
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.test_report"`

- [ ] **3.6 `test_report()` - PASS 케이스 + 고장난 엔진 quirk**
  - Test 추가:
    ```python
    def test_test_report_pass():
        build = CarBuild(CarType.SEDAN, Engine.GM, Brake.MANDO, Steering.MOBIS)
        assert build.test_report() == "PASS"


    def test_test_report_pass_even_with_broken_engine():
        # 원본 test_produced_car()는 엔진 고장 여부를 검사하지 않는다 — 동작 보존 대상 quirk
        build = CarBuild(CarType.SEDAN, Engine.BROKEN, Brake.MANDO, Steering.MOBIS)
        assert build.test_report() == "PASS"
    ```
  - 실행: `pytest tests/test_car.py -v` -> 이미 PASS (3.5 구현이 이 케이스도 만족시킴, 확인만)
  - 커밋: `git commit -am "test: cover CarBuild.test_report pass and broken-engine quirk"`

---

## Phase 4: 상태 전이 순수 함수 (`advance_step`)

원본 `main()`의 `step` 이동 로직(뒤로가기 포함)을 `input()` 없이 테스트 가능한 순수 함수로 분리.

**Produces:** `car_assembly.cli.advance_step(step, ans) -> int` — Phase 5가 그대로 사용.

- [ ] **4.1 뒤로가기: STEP 4 -> 0**
  - Test 작성 (`tests/test_cli_state.py` 새로 생성):
    ```python
    from car_assembly.cli import advance_step


    def test_back_navigation_from_step4_goes_to_0():
        assert advance_step(4, 0) == 0
    ```
  - 실행 -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/cli.py` 새로 생성):
    ```python
    def advance_step(step: int, ans: int) -> int:
        if ans == 0 and step == 4:
            return 0
        return step
    ```
  - 실행 후 PASS 확인, 커밋: `git add car_assembly/cli.py tests/test_cli_state.py && git commit -m "feat: add advance_step step4-to-0 back navigation"`

- [ ] **4.2 뒤로가기: 일반 단계 -1**
  - Test 추가:
    ```python
    def test_back_navigation_decrements_step():
        assert advance_step(2, 0) == 1
        assert advance_step(1, 0) == 0


    def test_back_navigation_at_step0_stays():
        assert advance_step(0, 0) == 0
    ```
  - 실행 -> 실패 확인 (현재 항상 step 그대로 반환)
  - 구현 (`advance_step` 수정):
    ```python
    def advance_step(step: int, ans: int) -> int:
        if ans == 0:
            if step == 4:
                return 0
            if step > 0:
                return step - 1
            return step
        return step
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add advance_step generic back navigation"`

- [ ] **4.3 정방향 이동**
  - Test 추가:
    ```python
    def test_forward_navigation_increments_step():
        assert advance_step(0, 1) == 1
        assert advance_step(1, 2) == 2
        assert advance_step(2, 3) == 3
        assert advance_step(3, 1) == 4


    def test_step4_non_zero_answer_stays_on_step4():
        assert advance_step(4, 1) == 4
        assert advance_step(4, 2) == 4
    ```
  - 실행 -> 실패 확인 (정방향 시 항상 step 그대로 반환)
  - 구현 (`advance_step` 마지막 분기 수정):
    ```python
        if step in (0, 1, 2, 3):
            return step + 1
        return step
    ```
  - 실행: `pytest tests/test_cli_state.py -v` -> PASS 전부 확인
  - 커밋: `git commit -am "feat: add advance_step forward navigation"`

---

## Phase 5: CLI 이식 (문구/동작 100% 동일)

원본 `show_menu`, `is_valid_range`, `select_*`, `run_produced_car`, `test_produced_car`, `main`, `delay`, `clear`를 `car_assembly/cli.py`로 옮긴다.

**Consumes:** `CarBuild`(Phase 3), `advance_step`(Phase 4), Enum(Phase 1)
**Produces:** `car_assembly.cli.main()` — Phase 6이 그대로 호출.

- [ ] **5.1 `delay`/`clear` 헬퍼**
  - 구현 (`car_assembly/cli.py` 상단에 추가, 유닛테스트 없음 — `time.sleep`/화면 클리어는 값 검증 대상이 아님):
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
  - 커밋: `git commit -am "feat: add delay/clear helpers to cli.py"`

- [ ] **5.2 `selection_message` - car_type**
  - Test 추가 (`tests/test_cli_state.py`):
    ```python
    from car_assembly.types import CarType

    def test_selection_message_car_type():
        assert selection_message("car_type", CarType.SEDAN) == "차량 타입으로 Sedan을 선택하셨습니다."
        assert selection_message("car_type", CarType.SUV) == "차량 타입으로 SUV을 선택하셨습니다."
        assert selection_message("car_type", CarType.TRUCK) == "차량 타입으로 Truck을 선택하셨습니다."
    ```
    (파일 상단 import에 `from car_assembly.cli import advance_step, selection_message`로 수정)
  - 실행 -> `ImportError`로 실패 확인
  - 구현 (`car_assembly/cli.py`에 추가):
    ```python
    _SELECTION_MESSAGES = {
        "car_type": {
            CarType.SEDAN: "차량 타입으로 Sedan을 선택하셨습니다.",
            CarType.SUV: "차량 타입으로 SUV을 선택하셨습니다.",
            CarType.TRUCK: "차량 타입으로 Truck을 선택하셨습니다.",
        },
    }


    def selection_message(field: str, value) -> str:
        return _SELECTION_MESSAGES[field][value]
    ```
    (import에 `from car_assembly.types import CarType` 추가)
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add selection_message for car_type"`

- [ ] **5.3 `selection_message` - engine**
  - Test 추가:
    ```python
    from car_assembly.types import Engine

    def test_selection_message_engine():
        assert selection_message("engine", Engine.GM) == "GM 엔진을 선택하셨습니다."
        assert selection_message("engine", Engine.TOYOTA) == "TOYOTA 엔진을 선택하셨습니다."
        assert selection_message("engine", Engine.WIA) == "WIA 엔진을 선택하셨습니다."
        assert selection_message("engine", Engine.BROKEN) == "고장난 엔진을 선택하셨습니다."
    ```
  - 구현 (`_SELECTION_MESSAGES`에 `"engine"` 키 추가):
    ```python
        "engine": {
            Engine.GM: "GM 엔진을 선택하셨습니다.",
            Engine.TOYOTA: "TOYOTA 엔진을 선택하셨습니다.",
            Engine.WIA: "WIA 엔진을 선택하셨습니다.",
            Engine.BROKEN: "고장난 엔진을 선택하셨습니다.",
        },
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add selection_message for engine"`

- [ ] **5.4 `selection_message` - brake**
  - Test 추가:
    ```python
    from car_assembly.types import Brake

    def test_selection_message_brake():
        assert selection_message("brake", Brake.MANDO) == "MANDO 제동장치를 선택하셨습니다."
        assert selection_message("brake", Brake.CONTINENTAL) == "CONTINENTAL 제동장치를 선택하셨습니다."
        assert selection_message("brake", Brake.BOSCH) == "BOSCH 제동장치를 선택하셨습니다."
    ```
  - 구현 (`_SELECTION_MESSAGES`에 `"brake"` 키 추가):
    ```python
        "brake": {
            Brake.MANDO: "MANDO 제동장치를 선택하셨습니다.",
            Brake.CONTINENTAL: "CONTINENTAL 제동장치를 선택하셨습니다.",
            Brake.BOSCH: "BOSCH 제동장치를 선택하셨습니다.",
        },
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add selection_message for brake"`

- [ ] **5.5 `selection_message` - steering**
  - Test 추가:
    ```python
    from car_assembly.types import Steering

    def test_selection_message_steering():
        assert selection_message("steering", Steering.BOSCH) == "BOSCH 조향장치를 선택하셨습니다."
        assert selection_message("steering", Steering.MOBIS) == "MOBIS 조향장치를 선택하셨습니다."
    ```
  - 구현 (`_SELECTION_MESSAGES`에 `"steering"` 키 추가):
    ```python
        "steering": {
            Steering.BOSCH: "BOSCH 조향장치를 선택하셨습니다.",
            Steering.MOBIS: "MOBIS 조향장치를 선택하셨습니다.",
        },
    ```
  - 실행: `pytest tests/test_cli_state.py -v` -> PASS 전부 확인
  - 커밋: `git commit -am "feat: add selection_message for steering"`

- [ ] **5.6 `show_menu` 이식**
  - 유닛테스트 없음(화면 출력 전용, 검증은 Phase 7 수동 회귀에서 수행)
  - 구현 (`car_assembly/cli.py`에 원본 텍스트 그대로 추가):
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
  - 커밋: `git commit -am "feat: port show_menu to cli.py"`

- [ ] **5.7 `is_valid_range` 이식**
  - Test 추가 (`tests/test_cli_state.py`):
    ```python
    from car_assembly.cli import is_valid_range


    def test_is_valid_range_car_type_bounds():
        assert is_valid_range(0, 1) is True
        assert is_valid_range(0, 3) is True
        assert is_valid_range(0, 0) is False
        assert is_valid_range(0, 4) is False


    def test_is_valid_range_engine_bounds():
        assert is_valid_range(1, 0) is True
        assert is_valid_range(1, 4) is True
        assert is_valid_range(1, 5) is False
    ```
  - 실행 -> `ImportError`로 실패 확인
  - 구현 (`car_assembly/cli.py`에 추가, 원본 에러 메시지 그대로):
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
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: port is_valid_range to cli.py"`

- [ ] **5.8 `main()` 루프 조립 (통합)**
  - 유닛테스트 없음(입출력 통합 지점, 검증은 Phase 7 수동 회귀에서 수행)
  - 구현 (`car_assembly/cli.py` 최상단 import 정리 후 파일 끝에 추가):
    ```python
    from car_assembly.car import CarBuild
    from car_assembly.types import Brake, CarType, Engine, Steering


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
  - 실행: `pytest -v` -> 지금까지 작성된 테스트 전부 PASS 확인 (import 에러 없는지 확인 목적)
  - 커밋: `git commit -am "feat: assemble main() loop in cli.py"`

---

## Phase 6: `assembly.py` entry point 축소

**Consumes:** `car_assembly.cli.main`(Phase 5)

- [ ] **6.1 `assembly.py` 전체 교체**
  - 구현 (`assembly.py` 전체를 아래로 교체):
    ```python
    from car_assembly.cli import main

    if __name__ == "__main__":
        main()
    ```
  - 실행: `pytest -v` -> 전체 테스트 PASS 확인
  - 커밋: `git commit -am "refactor: slim assembly.py down to a thin entry point"`

---

## Phase 7: 수동 회귀 테스트 + 문서 정리

- [ ] **7.1 수동 시나리오: 정상 RUN**
  - `python assembly.py` 실행 -> Sedan -> GM -> Mando -> Mobis -> RUN
  - 확인: `Car Type : Sedan` / `Engine   : GM` / `Brake    : Mando` / `Steering : Mobis` / `자동차가 동작됩니다.` 순서로 원본과 동일하게 출력

- [ ] **7.2 수동 시나리오: 비호환 RUN/TEST**
  - Sedan -> GM -> Continental -> Mobis -> RUN -> `자동차가 동작되지 않습니다` 확인
  - 동일 조합 -> TEST -> `FAIL` + `Sedan에는 Continental제동장치 사용 불가` 확인

- [ ] **7.3 수동 시나리오: 고장난 엔진 quirk**
  - Sedan -> 고장난 엔진(4) -> Mando -> Mobis -> RUN -> `엔진이 고장나있습니다.` / `자동차가 움직이지 않습니다.` 확인
  - 동일 조합 -> TEST -> `PASS` 확인 (원본 quirk 재현 여부)

- [ ] **7.4 수동 시나리오: 네비게이션/에러/종료**
  - 각 단계에서 `0` 입력 시 한 단계 뒤로가기, STEP 4에서 `0` 입력 시 STEP 0으로 이동 확인
  - 범위 밖 숫자 입력 시 원본과 동일한 `ERROR ::` 메시지 확인
  - `exit` 입력 시 `바이바이` 출력 후 종료 확인

- [ ] **7.5 `CLAUDE.md`에 pytest 명령 추가**
  - `## 명령어` 섹션의 실행 항목 아래에 추가:
    ```markdown
    - 테스트 실행: `pytest`
    ```
  - 커밋: `git add CLAUDE.md && git commit -m "docs: add pytest command to CLAUDE.md after refactor"`

- [ ] **7.6 푸시**
  - `git push`

---

## Self-Review 체크리스트

- PRD.md의 5개 호환성 규칙 전부 Phase 2에서 규칙 1개씩 테스트로 커버됨
- "동작 유지" 요구사항은 Phase 5에서 문자열을 원본과 1:1 대조, Phase 7에서 수동 회귀로 재확인
- pytest 요구사항은 Phase 1~5 전 단계에서 테스트 작성으로 충족
- 확장성(규칙 단일 관리)은 Phase 2의 `RULES` 테이블로 충족 — 새 규칙 추가 시 `RULES`에 항목 하나만 추가하면 `run`/`test` 양쪽에 자동 반영됨
- Out of scope(신규 타입/부품 추가, UI 변경, 다국어화)는 어떤 Phase에도 포함하지 않음
