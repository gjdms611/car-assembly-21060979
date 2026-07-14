# Phase 3: `CarTypeConstrained` 믹스인

## 목적

PRD.md의 호환성 제약 중 "엔진/제동장치가 특정 차량 타입 하나와 호환되지 않는다"는 규칙은 엔진과 제동장치 양쪽에 동일한 형태로 나타난다(예: "SUV에는 TOYOTA엔진 사용 불가", "Sedan에는 Continental제동장치 사용 불가" — 둘 다 "{차량타입}에는 {부품라벨}{품목명} 사용 불가" 패턴). 이 판정 로직을 `CarTypeConstrained` 믹스인 하나로 분리해 엔진/제동장치 두 계열이 공유한다. 조향장치는 이 제약이 없으므로 이 믹스인을 받지 않는다.

## 사전 조건

Phase 2(`Part`) 완료.

## 구현 절차

### 태스크 3.1: `CarTypeConstrained` 믹스인

1. Test 추가 — `tests/test_parts.py` 파일 맨 끝에 아래 내용을 그대로 추가한다(기존 내용은 지우지 않는다):

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

   파일 상단의 기존 `from car_assembly.parts import Part` import는 그대로 두고, 위 두 개의 새 import 문(`from car_assembly.car_type import CarType`, `from car_assembly.parts import CarTypeConstrained, Part`)을 파일 상단 import 영역에 추가한다. `Part`가 중복 import되지 않도록 기존 `from car_assembly.parts import Part` 줄을 `from car_assembly.parts import CarTypeConstrained, Part`로 합쳐도 된다.

2. 실행: `pytest tests/test_parts.py -v`
   기대 결과: `ImportError: cannot import name 'CarTypeConstrained' from 'car_assembly.parts'`로 실패.

3. 구현 — `car_assembly/parts.py` 파일 끝에 아래 내용을 그대로 추가한다:

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

   `from car_assembly.car_type import CAR_TYPE_LABEL, CarType` import 문은 파일 최상단(다른 import들과 함께)으로 옮겨도 되고, 이 클래스 바로 위에 그대로 둬도 된다 — 단, `car_assembly/parts.py` 안에 이 import 줄이 정확히 한 번만 존재해야 한다.

4. 실행: `pytest tests/test_parts.py -v`
   기대 결과: `test_car_type_constrained_reports_conflict`, `test_car_type_constrained_allows_other_car_types` 모두 PASS. 기존 Phase 2의 테스트 2개도 계속 PASS해야 한다.

5. 커밋:
   ```bash
   git commit -am "feat: add CarTypeConstrained mixin"
   ```

## 이 Phase가 끝나면 존재해야 하는 것

- `car_assembly/parts.py` — `Part`(Phase 2) + `CarTypeConstrained`(이 Phase) 두 클래스만 포함. 아직 `EnginePart`, `BrakePart`, `SteeringPart`는 없어야 정상(각각 Phase 4, 5, 6에서 추가).
- `tests/test_parts.py` — Phase 2 테스트 2개 + 이 Phase 테스트 2개, 총 4개
- git 커밋 1개(누적 4개): `feat: add CarTypeConstrained mixin`

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] `CarTypeConstrained`가 `Part`와 별개의 믹스인 클래스로 분리되어 있는지 확인(단독으로는 `label` 속성이 없어 사용 불가하고, 반드시 다른 클래스와 함께 다중 상속돼야 함)
- [ ] 메시지 포맷이 PRD.md의 실제 문구와 정확히 일치하는지 확인: `"{차량타입라벨}에는 {부품라벨}{품목명} 사용 불가"` (예: `"SUV에는 TOYOTA엔진 사용 불가"` — 실제 확인은 Phase 4에서)
- [ ] `unsupported_car_type`이 기본값 `None`인 부품은 어떤 차량 타입과도 항상 호환되는지 확인
- [ ] `pytest tests/test_parts.py -v` 실행 결과 4개 테스트 모두 PASS
- [ ] `car_assembly/parts.py`에 아직 `EnginePart`/`BrakePart`/`SteeringPart`가 없는지 확인(Phase 순서를 건너뛰지 않았는지 검증)
