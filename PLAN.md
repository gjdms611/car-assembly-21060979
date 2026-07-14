# 자동차 조립 시뮬레이터 리팩토링 계획

> **실행 방법:** superpowers:subagent-driven-development (추천) 또는 superpowers:executing-plans 로 태스크 단위 진행. 체크박스(`- [ ]`)로 진행상황 추적.

**목표:** 절차지향 단일 파일(`assembly.py`)을, 동작(콘솔 UI/판정 결과)은 완전히 동일하게 유지한 채 유지보수 가능한 구조로 재구성하고 pytest 테스트를 도입한다.

**아키텍처 / 설계 노트**

- 엔진·제동장치·조향장치는 클래스 계층으로 모델링한다. 세 부품 모두 "선택 메시지 출력", "리포트용 라벨" 로직이 동일한 형태라 공통 베이스 `Part`에 **템플릿 메서드**로 올린다.
- 엔진과 제동장치만 "특정 차량 타입과 호환 안 됨"이라는 동일한 규칙 형태를 가지므로, 이 부분만 `CarTypeConstrained` **믹스인**으로 분리해 두 클래스가 공유한다(조향장치는 이 제약이 없으므로 믹스인을 받지 않는다 — 불필요한 인터페이스를 강제하지 않기 위함).
- 제동장치가 조향장치 제약(Bosch 브레이크는 Bosch 조향장치 필요)을 검사하는 로직은 제동장치 쪽에만 존재 — 원본에서도 이 규칙의 주체는 브레이크이므로 자연스러운 위치.
- **의도적으로 도입하지 않은 패턴 (오버엔지니어링 방지):**
  - CLI 5단계는 선형 흐름뿐이라 State 패턴/클래스 계층 대신 순수 함수(`advance_step`) 유지 — 상태가 5개뿐이고 분기 로직도 단순해 클래스화 이득이 거의 없음.
  - `CarBuild`는 필드 4개를 순차로 채우는 것뿐이라 Builder 패턴(fluent API) 대신 평범한 mutable dataclass 유지 — 체이닝이 필요한 지점이 없음.
  - 부품 조회는 3~4개짜리 `dict` 팩토리로 충분 — Factory 클래스나 등록 데코레이터는 불필요한 간접화.
- 호환성 판정 순서(`CarBuild.first_incompatibility`)는 `or` 체이닝 3개로 충분 — Chain of Responsibility를 객체로 만들 만큼 단계가 많지 않음.

**Tech Stack:** Python 표준 라이브러리만 사용(외부 의존성 없음), pytest.

## Global Constraints (PRD.md 기준, 모든 Phase 공통)

- 콘솔 메뉴 텍스트, 한글 안내 메시지, 입력 처리 방식(숫자 입력 / `0` 뒤로가기 / `exit` 종료)은 리팩토링 전후 **한 글자도 다르지 않게** 유지
- 호환성 판정 결과(`run`/`test` 양쪽) 동일
- pytest 기반 유닛테스트, 호환성 규칙 + 상태 전이 커버리지 확보
- 확장 시 코드 수정은 허용하되, 규칙은 한 곳(해당 부품 클래스)에서만 관리
- Out of scope: 신규 차량 타입/부품 실제 추가, UI/UX 변경, 다국어화

## 파일 구조

```
car_assembly/
  __init__.py
  car_type.py       # CarType Enum + 라벨
  parts.py          # Part(템플릿 베이스) + CarTypeConstrained(믹스인)
                     # + EnginePart/BrakePart/SteeringPart 계층 + *_BY_CODE 팩토리
  car.py            # CarBuild (선택된 부품 객체 보관 + 리포트)
  cli.py            # 메뉴 출력, 상태 전이, main() 루프
assembly.py         # 얇은 entry point: cli.main() 호출만
tests/
  test_car_type.py
  test_parts.py
  test_car.py
  test_cli_state.py
```

---

## Phase 1: `CarType` (차량 타입 — 부품 아님, 단순 식별자)

- [ ] **1.1 패키지 뼈대 생성**
  - Create: `car_assembly/__init__.py` (빈 파일)
  - 커밋: `git add car_assembly/__init__.py && git commit -m "chore: create car_assembly package"`

- [ ] **1.2 `CarType` enum + 라벨**
  - Test 작성 (`tests/test_car_type.py` 새로 생성):
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
  - 실행 -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/car_type.py` 새로 생성):
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
  - 실행 후 PASS 확인, 커밋: `git add car_assembly/car_type.py tests/test_car_type.py && git commit -m "feat: add CarType enum with labels"`

---

## Phase 2: `Part` 템플릿 베이스

모든 부품이 공유하는 "선택 메시지 생성", "리포트 라벨 반환" 동작을 한 곳에 정의(템플릿 메서드 패턴). 각 부품 서브클래스는 `label`/`unit_label` 값만 채우면 된다.

- [ ] **2.1 `Part` 베이스 클래스**
  - Test 작성 (`tests/test_parts.py` 새로 생성):
    ```python
    from car_assembly.parts import Part


    class _DummyPart(Part):
        label = "Dummy"
        unit_label = "테스트를"


    def test_part_selection_message_uppercases_label():
        assert _DummyPart().selection_message() == "DUMMY 테스트를 선택하셨습니다."


    def test_part_run_label_defaults_to_label():
        assert _DummyPart().run_label() == "Dummy"
    ```
  - 실행 -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/parts.py` 새로 생성):
    ```python
    from abc import ABC
    from typing import Optional


    class Part(ABC):
        """모든 부품이 공유하는 선택 메시지/리포트 라벨 동작(템플릿 메서드)."""

        label: str
        unit_label: str  # 예: "엔진을", "제동장치를", "조향장치를"

        def selection_message(self) -> str:
            return f"{self.label.upper()} {self.unit_label} 선택하셨습니다."

        def run_label(self) -> Optional[str]:
            return self.label
    ```
  - 실행 후 PASS 확인, 커밋: `git add car_assembly/parts.py tests/test_parts.py && git commit -m "feat: add Part template base class"`

---

## Phase 3: `CarTypeConstrained` 믹스인

엔진과 제동장치만 공유하는 "특정 차량 타입 하나와 호환 안 됨" 규칙을 믹스인으로 분리 — 조향장치는 이 제약이 없으므로 받지 않는다.

**Consumes:** Phase 1의 `CarType`, `CAR_TYPE_LABEL`

- [ ] **3.1 `CarTypeConstrained` 믹스인**
  - Test 추가 (`tests/test_parts.py`):
    ```python
    from car_assembly.car_type import CarType
    from car_assembly.parts import CarTypeConstrained, Part


    class _DummyConstrainedPart(CarTypeConstrained, Part):
        label = "Dummy"
        unit_label = "테스트를"
        car_type_conflict_noun = "부품"
        unsupported_car_type = CarType.TRUCK


    def test_car_type_constrained_reports_conflict():
        part = _DummyConstrainedPart()
        assert part.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 Dummy부품 사용 불가"


    def test_car_type_constrained_allows_other_car_types():
        part = _DummyConstrainedPart()
        assert part.incompatibility_with_car_type(CarType.SEDAN) is None
    ```
  - 실행 -> `ImportError`로 실패 확인
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    from car_assembly.car_type import CAR_TYPE_LABEL, CarType


    class CarTypeConstrained:
        """특정 차량 타입과 호환되지 않는 부품(엔진/제동장치)이 공유하는 믹스인."""

        unsupported_car_type: Optional[CarType] = None
        car_type_conflict_noun: str = ""

        def incompatibility_with_car_type(self, car_type: CarType) -> Optional[str]:
            if self.unsupported_car_type is not None and car_type == self.unsupported_car_type:
                return f"{CAR_TYPE_LABEL[car_type]}에는 {self.label}{self.car_type_conflict_noun} 사용 불가"
            return None
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarTypeConstrained mixin"`

---

## Phase 4: `EnginePart` 계열

**Consumes:** Phase 2(`Part`), Phase 3(`CarTypeConstrained`)
**Produces:** `EnginePart`, `GMEngine`/`ToyotaEngine`/`WIAEngine`/`BrokenEngine`, `ENGINE_BY_CODE`

- [ ] **4.1 `EnginePart` 베이스 + `GMEngine`**
  - Test 추가 (`tests/test_parts.py`):
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
  - 실행 -> `ImportError`로 실패 확인
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class EnginePart(CarTypeConstrained, Part):
        unit_label = "엔진을"
        car_type_conflict_noun = "엔진"
        is_broken: bool = False


    class GMEngine(EnginePart):
        label = "GM"
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add EnginePart base and GMEngine"`

- [ ] **4.2 `ToyotaEngine` (SUV 불가)**
  - Test 추가:
    ```python
    from car_assembly.parts import ToyotaEngine


    def test_toyota_engine_incompatible_with_suv():
        engine = ToyotaEngine()
        assert engine.incompatibility_with_car_type(CarType.SUV) == "SUV에는 TOYOTA엔진 사용 불가"
        assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
        assert engine.selection_message() == "TOYOTA 엔진을 선택하셨습니다."
    ```
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class ToyotaEngine(EnginePart):
        label = "TOYOTA"
        unsupported_car_type = CarType.SUV
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add ToyotaEngine"`

- [ ] **4.3 `WIAEngine` (Truck 불가)**
  - Test 추가:
    ```python
    from car_assembly.parts import WIAEngine


    def test_wia_engine_incompatible_with_truck():
        engine = WIAEngine()
        assert engine.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 WIA엔진 사용 불가"
        assert engine.selection_message() == "WIA 엔진을 선택하셨습니다."
    ```
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class WIAEngine(EnginePart):
        label = "WIA"
        unsupported_car_type = CarType.TRUCK
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add WIAEngine"`

- [ ] **4.4 `BrokenEngine` (항상 호환되지만 `is_broken=True`, run 리포트에 라벨 없음)**
  - Test 추가:
    ```python
    from car_assembly.parts import BrokenEngine


    def test_broken_engine_is_broken_and_has_no_run_label():
        engine = BrokenEngine()
        assert engine.is_broken is True
        assert engine.run_label() is None
        assert engine.selection_message() == "고장난 엔진을 선택하셨습니다."
        assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
    ```
  - 구현 (`car_assembly/parts.py`에 추가— `run_label`만 오버라이드, 나머지는 `Part`/`EnginePart` 그대로 재사용):
    ```python
    class BrokenEngine(EnginePart):
        label = "고장난"
        is_broken = True

        def run_label(self) -> Optional[str]:
            return None
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add BrokenEngine"`

- [ ] **4.5 `ENGINE_BY_CODE` 팩토리 딕셔너리**
  - Test 추가:
    ```python
    from car_assembly.parts import ENGINE_BY_CODE, BrokenEngine, GMEngine, ToyotaEngine, WIAEngine


    def test_engine_by_code_maps_input_number_to_class():
        assert ENGINE_BY_CODE[1] is GMEngine
        assert ENGINE_BY_CODE[2] is ToyotaEngine
        assert ENGINE_BY_CODE[3] is WIAEngine
        assert ENGINE_BY_CODE[4] is BrokenEngine
    ```
  - 구현 (`car_assembly/parts.py`에 추가, 엔진 클래스들 바로 아래):
    ```python
    ENGINE_BY_CODE = {1: GMEngine, 2: ToyotaEngine, 3: WIAEngine, 4: BrokenEngine}
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add ENGINE_BY_CODE factory map"`

---

## Phase 5: `BrakePart` 계열

제동장치는 `CarTypeConstrained`(엔진과 동일 형태)를 재사용하고, "Bosch 브레이크는 Bosch 조향장치 필요"라는 조향장치 제약만 추가로 갖는다. `steering` 인자는 `is_bosch` 속성만 있으면 되므로(덕 타이핑) `SteeringPart`를 import할 필요가 없다 — Phase 6과 순서 의존성 없음.

**Consumes:** Phase 2(`Part`), Phase 3(`CarTypeConstrained`)
**Produces:** `BrakePart`, `MandoBrake`/`ContinentalBrake`/`BoschBrake`, `BRAKE_BY_CODE`

- [ ] **5.1 `BrakePart` 베이스 + `MandoBrake` (Truck 불가)**
  - Test 추가 (`tests/test_parts.py`):
    ```python
    from car_assembly.parts import MandoBrake


    def test_mando_brake_incompatible_with_truck():
        brake = MandoBrake()
        assert brake.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 Mando제동장치 사용 불가"
        assert brake.incompatibility_with_car_type(CarType.SEDAN) is None
        assert brake.selection_message() == "MANDO 제동장치를 선택하셨습니다."
        assert brake.run_label() == "Mando"
    ```
  - 구현 (`car_assembly/parts.py`에 추가 — `incompatibility_with_car_type`/`selection_message`/`run_label`은 전부 상속으로 재사용, 새로 작성하는 코드는 조향장치 제약 하나뿐):
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
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add BrakePart base and MandoBrake"`

- [ ] **5.2 `ContinentalBrake` (Sedan 불가)**
  - Test 추가:
    ```python
    from car_assembly.parts import ContinentalBrake


    def test_continental_brake_incompatible_with_sedan():
        brake = ContinentalBrake()
        assert brake.incompatibility_with_car_type(CarType.SEDAN) == "Sedan에는 Continental제동장치 사용 불가"
        assert brake.selection_message() == "CONTINENTAL 제동장치를 선택하셨습니다."
        assert brake.run_label() == "Continental"
    ```
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class ContinentalBrake(BrakePart):
        label = "Continental"
        unsupported_car_type = CarType.SEDAN
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add ContinentalBrake"`

- [ ] **5.3 `BoschBrake` (Bosch 조향장치 필요)**
  - Test 추가 (더미 객체로 `is_bosch`만 흉내내 검증 — `SteeringPart`가 아직 없어도 됨을 실제로 보여줌):
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
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class BoschBrake(BrakePart):
        label = "Bosch"
        requires_bosch_steering = True
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add BoschBrake requiring Bosch steering"`

- [ ] **5.4 `BRAKE_BY_CODE` 팩토리 딕셔너리**
  - Test 추가:
    ```python
    from car_assembly.parts import BRAKE_BY_CODE, BoschBrake, ContinentalBrake, MandoBrake


    def test_brake_by_code_maps_input_number_to_class():
        assert BRAKE_BY_CODE[1] is MandoBrake
        assert BRAKE_BY_CODE[2] is ContinentalBrake
        assert BRAKE_BY_CODE[3] is BoschBrake
    ```
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    BRAKE_BY_CODE = {1: MandoBrake, 2: ContinentalBrake, 3: BoschBrake}
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add BRAKE_BY_CODE factory map"`

---

## Phase 6: `SteeringPart` 계열

조향장치는 차량 타입 제약이 없으므로 `CarTypeConstrained`를 받지 않고 `Part`만 상속한다. "자신이 Bosch인지"는 `is_bosch` 속성으로만 노출하면 `BoschBrake`가 덕 타이핑으로 사용할 수 있다.

**Consumes:** Phase 2(`Part`)
**Produces:** `SteeringPart`, `BoschSteering`/`MobisSteering`, `STEERING_BY_CODE`

- [ ] **6.1 `SteeringPart` 베이스 + `BoschSteering`**
  - Test 작성 (`tests/test_parts.py`):
    ```python
    from car_assembly.parts import BoschSteering


    def test_bosch_steering():
        steering = BoschSteering()
        assert steering.is_bosch is True
        assert steering.selection_message() == "BOSCH 조향장치를 선택하셨습니다."
        assert steering.run_label() == "Bosch"
    ```
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class SteeringPart(Part):
        unit_label = "조향장치를"
        is_bosch: bool = False


    class BoschSteering(SteeringPart):
        label = "Bosch"
        is_bosch = True
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add SteeringPart base and BoschSteering"`

- [ ] **6.2 `MobisSteering`**
  - Test 추가:
    ```python
    from car_assembly.parts import MobisSteering


    def test_mobis_steering():
        steering = MobisSteering()
        assert steering.is_bosch is False
        assert steering.selection_message() == "MOBIS 조향장치를 선택하셨습니다."
        assert steering.run_label() == "Mobis"
    ```
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    class MobisSteering(SteeringPart):
        label = "Mobis"
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add MobisSteering"`

- [ ] **6.3 `STEERING_BY_CODE` 팩토리 딕셔너리 + 실제 `BoschBrake`/`BoschSteering` 조합 검증**
  - Test 추가 (5.3에서는 가짜 객체로 검증했으니, 여기서 실제 클래스 조합으로 한 번 더 확인):
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
  - 구현 (`car_assembly/parts.py`에 추가):
    ```python
    STEERING_BY_CODE = {1: BoschSteering, 2: MobisSteering}
    ```
  - 실행: `pytest tests/test_parts.py -v` -> PASS 전부 확인
  - 커밋: `git commit -am "feat: add STEERING_BY_CODE factory map"`

---

## Phase 7: `CarBuild` (조립 상태 + 리포트)

부품 객체들을 보관하고, 판정/출력은 부품 객체에 위임만 한다(평범한 mutable dataclass — Builder 패턴은 이 단순한 필드 채우기에는 과함).

**Consumes:** Phase 1(`CarType`/`CAR_TYPE_LABEL`), Phase 4~6(`EnginePart`/`BrakePart`/`SteeringPart`)
**Produces:** `CarBuild(car_type, engine, brake, steering)`, `.is_engine_broken()`, `.first_incompatibility()`, `.is_compatible()`, `.run_report()`, `.test_report()` — Phase 9(cli.py)이 그대로 사용.

- [ ] **7.1 `CarBuild` 골격 + `is_engine_broken()`**
  - Test 작성 (`tests/test_car.py` 새로 생성):
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
  - 실행 -> `ModuleNotFoundError`로 실패 확인
  - 구현 (`car_assembly/car.py` 새로 생성):
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
  - 실행 후 PASS 확인, 커밋: `git add car_assembly/car.py tests/test_car.py && git commit -m "feat: add CarBuild skeleton holding part objects"`

- [ ] **7.2 `first_incompatibility()` / `is_compatible()`**
  - Test 추가 (`tests/test_car.py`, 상단 import에 필요한 부품 클래스 추가):
    ```python
    from car_assembly.parts import BoschBrake, ContinentalBrake, MandoBrake, WIAEngine


    def test_first_incompatibility_engine_checked_before_brake():
        # Truck + WIA(엔진 위반) + Mando(제동장치 위반) 동시 발생 -> 원본과 동일하게 엔진 메시지가 우선
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
  - 실행 -> `AttributeError`로 실패 확인
  - 구현 (`car_assembly/car.py`에 메서드 추가):
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
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.first_incompatibility delegating to part objects"`

- [ ] **7.3 `run_report()`**
  - Test 추가:
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
  - 실행 -> `AttributeError`로 실패 확인
  - 구현 (`car_assembly/car.py`에 메서드 추가):
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
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add CarBuild.run_report"`

- [ ] **7.4 `test_report()`**
  - Test 추가:
    ```python
    def test_test_report_fail():
        build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
        assert build.test_report() == "FAIL\nSedan에는 Continental제동장치 사용 불가"


    def test_test_report_pass():
        build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
        assert build.test_report() == "PASS"


    def test_test_report_pass_even_with_broken_engine():
        # 원본 test_produced_car()는 엔진 고장 여부를 검사하지 않는다 — 동작 보존 대상 quirk
        build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
        assert build.test_report() == "PASS"
    ```
  - 구현 (`car_assembly/car.py`에 메서드 추가):
    ```python
        def test_report(self) -> str:
            message = self.first_incompatibility()
            if message is None:
                return "PASS"
            return f"FAIL\n{message}"
    ```
  - 실행: `pytest tests/test_car.py -v` -> PASS 전부 확인
  - 커밋: `git commit -am "feat: add CarBuild.test_report"`

---

## Phase 8: 상태 전이 순수 함수 (`advance_step`)

원본 `main()`의 `step` 이동 로직(뒤로가기 포함)을 `input()` 없이 테스트 가능한 순수 함수로 분리. (앞서 설계 노트에서 설명한 대로, State 클래스 계층 대신 함수 하나로 충분한 규모)

**Produces:** `car_assembly.cli.advance_step(step, ans) -> int` — Phase 9가 그대로 사용.

- [ ] **8.1 뒤로가기: STEP 4 -> 0**
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

- [ ] **8.2 뒤로가기: 일반 단계 -1**
  - Test 추가:
    ```python
    def test_back_navigation_decrements_step():
        assert advance_step(2, 0) == 1
        assert advance_step(1, 0) == 0


    def test_back_navigation_at_step0_stays():
        assert advance_step(0, 0) == 0
    ```
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

- [ ] **8.3 정방향 이동**
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
  - 구현 (`advance_step` 마지막 분기 수정):
    ```python
        if step in (0, 1, 2, 3):
            return step + 1
        return step
    ```
  - 실행: `pytest tests/test_cli_state.py -v` -> PASS 전부 확인
  - 커밋: `git commit -am "feat: add advance_step forward navigation"`

---

## Phase 9: CLI 이식 (문구/동작 100% 동일)

원본 `show_menu`, `is_valid_range`, `select_*`, `run_produced_car`, `test_produced_car`, `main`, `delay`, `clear`를 `car_assembly/cli.py`로 옮긴다. 부품 선택/판정 로직은 전부 Phase 4~7의 클래스에 위임한다.

**Consumes:** `CarType`(Phase 1), `*_BY_CODE`(Phase 4~6), `CarBuild`(Phase 7), `advance_step`(Phase 8)
**Produces:** `car_assembly.cli.main()` — Phase 10이 그대로 호출.

- [ ] **9.1 `delay`/`clear` 헬퍼**
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

- [ ] **9.2 `car_type_selection_message` (차량 타입은 클래스가 아니므로 별도 헬퍼)**
  - Test 추가 (`tests/test_cli_state.py`):
    ```python
    from car_assembly.car_type import CarType
    from car_assembly.cli import car_type_selection_message


    def test_car_type_selection_message():
        assert car_type_selection_message(CarType.SEDAN) == "차량 타입으로 Sedan을 선택하셨습니다."
        assert car_type_selection_message(CarType.SUV) == "차량 타입으로 SUV을 선택하셨습니다."
        assert car_type_selection_message(CarType.TRUCK) == "차량 타입으로 Truck을 선택하셨습니다."
    ```
  - 구현 (`car_assembly/cli.py`에 추가):
    ```python
    from car_assembly.car_type import CAR_TYPE_LABEL, CarType


    def car_type_selection_message(car_type: CarType) -> str:
        return f"차량 타입으로 {CAR_TYPE_LABEL[car_type]}을 선택하셨습니다."
    ```
  - 실행 후 PASS 확인, 커밋: `git commit -am "feat: add car_type_selection_message helper"`

- [ ] **9.3 `show_menu` 이식**
  - 유닛테스트 없음(화면 출력 전용, 검증은 Phase 11 수동 회귀에서 수행)
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

- [ ] **9.4 `is_valid_range` 이식**
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

- [ ] **9.5 `main()` 루프 조립 (통합)**
  - 유닛테스트 없음(입출력 통합 지점, 검증은 Phase 11 수동 회귀에서 수행)
  - 구현 (`car_assembly/cli.py` 최상단 import 정리 후 파일 끝에 추가):
    ```python
    from car_assembly.car import CarBuild
    from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE


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
                print(car_type_selection_message(build.car_type))
                delay(800)
            elif step == STEP_ENGINE:
                build.engine = ENGINE_BY_CODE[ans]()
                print(build.engine.selection_message())
                delay(800)
            elif step == STEP_BRAKE:
                build.brake = BRAKE_BY_CODE[ans]()
                print(build.brake.selection_message())
                delay(800)
            elif step == STEP_STEERING:
                build.steering = STEERING_BY_CODE[ans]()
                print(build.steering.selection_message())
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
  - 커밋: `git commit -am "feat: assemble main() loop in cli.py using part factories"`

---

## Phase 10: `assembly.py` entry point 축소

**Consumes:** `car_assembly.cli.main`(Phase 9)

- [ ] **10.1 `assembly.py` 전체 교체**
  - 구현 (`assembly.py` 전체를 아래로 교체):
    ```python
    from car_assembly.cli import main

    if __name__ == "__main__":
        main()
    ```
  - 실행: `pytest -v` -> 전체 테스트 PASS 확인
  - 커밋: `git commit -am "refactor: slim assembly.py down to a thin entry point"`

---

## Phase 11: 수동 회귀 테스트 + 문서 정리

- [ ] **11.1 수동 시나리오: 정상 RUN**
  - `python assembly.py` 실행 -> Sedan -> GM -> Mando -> Mobis -> RUN
  - 확인: `Car Type : Sedan` / `Engine   : GM` / `Brake    : Mando` / `Steering : Mobis` / `자동차가 동작됩니다.` 순서로 원본과 동일하게 출력

- [ ] **11.2 수동 시나리오: 비호환 RUN/TEST**
  - Sedan -> GM -> Continental -> Mobis -> RUN -> `자동차가 동작되지 않습니다` 확인
  - 동일 조합 -> TEST -> `FAIL` + `Sedan에는 Continental제동장치 사용 불가` 확인

- [ ] **11.3 수동 시나리오: 고장난 엔진 quirk**
  - Sedan -> 고장난 엔진(4) -> Mando -> Mobis -> RUN -> `엔진이 고장나있습니다.` / `자동차가 움직이지 않습니다.` 확인
  - 동일 조합 -> TEST -> `PASS` 확인 (원본 quirk 재현 여부)

- [ ] **11.4 수동 시나리오: 네비게이션/에러/종료**
  - 각 단계에서 `0` 입력 시 한 단계 뒤로가기, STEP 4에서 `0` 입력 시 STEP 0으로 이동 확인
  - 범위 밖 숫자 입력 시 원본과 동일한 `ERROR ::` 메시지 확인
  - `exit` 입력 시 `바이바이` 출력 후 종료 확인

- [ ] **11.5 `CLAUDE.md`에 pytest 명령 추가**
  - `## 명령어` 섹션의 실행 항목 아래에 추가:
    ```markdown
    - 테스트 실행: `pytest`
    ```
  - 커밋: `git add CLAUDE.md && git commit -m "docs: add pytest command to CLAUDE.md after refactor"`

- [ ] **11.6 푸시**
  - `git push`

---

## Self-Review 체크리스트

- PRD.md의 5개 호환성 규칙 전부 Phase 4~7에서 부품 클래스 단위로 테스트 커버됨
- "동작 유지" 요구사항은 Phase 9에서 문자열을 원본과 1:1 대조, Phase 11에서 수동 회귀로 재확인
- pytest 요구사항은 Phase 1~9 전 단계에서 테스트 작성으로 충족
- 중복 제거: `selection_message`/`run_label`은 `Part` 하나에만 존재(템플릿 메서드), 차량 타입 제약 검사는 `CarTypeConstrained` 하나에만 존재(믹스인) — 엔진/브레이크 두 클래스 계열이 동일 로직을 복붙하지 않음
- 확장성: 새 엔진/브레이크/조향장치 추가 시 해당 `*Part` 서브클래스 하나(+ `*_BY_CODE` 항목 하나)만 추가하면 `run`/`test`/선택 메시지 전부에 자동 반영됨
- 오버엔지니어링 방지: State 패턴(CLI 5단계), Builder 패턴(`CarBuild`), Factory 클래스(부품 조회)는 규모에 비해 과하다고 판단해 각각 순수 함수/평범한 dataclass/`dict`로 대체 — 위 "아키텍처 / 설계 노트"에 근거 명시
- Out of scope(신규 타입/부품 추가, UI 변경, 다국어화)는 어떤 Phase에도 포함하지 않음
