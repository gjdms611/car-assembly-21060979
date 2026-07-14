# Phase 2: `Part` 템플릿 베이스

## 목적

엔진/제동장치/조향장치 세 부품 계열이 공통으로 필요로 하는 동작 두 가지 — "선택 메시지 생성"과 "리포트용 라벨 반환" — 을 한 곳(`Part`)에 정의한다(템플릿 메서드 패턴). 이후 Phase 4~6에서 만들 각 부품 클래스는 `label`, `unit_label` 두 값만 채우면 이 동작을 공짜로 얻는다.

## 사전 조건

Phase 1 완료(이 Phase는 `CarType`을 직접 사용하지 않지만, 저장소 히스토리상 Phase 1 다음에 진행).

## 구현 절차

### 태스크 2.1: `Part` 베이스 클래스

1. Test 작성 — `tests/test_parts.py` 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

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

2. 실행: `pytest tests/test_parts.py -v`
   기대 결과: `ModuleNotFoundError: No module named 'car_assembly.parts'`로 실패.

3. 구현 — `car_assembly/parts.py` 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

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

4. 실행: `pytest tests/test_parts.py -v`
   기대 결과: `test_part_selection_message_uppercases_label`, `test_part_run_label_defaults_to_label` 모두 PASS.

5. 커밋:
   ```bash
   git add car_assembly/parts.py tests/test_parts.py
   git commit -m "feat: add Part template base class"
   ```

## 이 Phase가 끝나면 존재해야 하는 것

- `car_assembly/parts.py` — `Part` 클래스 **하나만** 포함 (아직 `EnginePart`, `CarTypeConstrained` 등은 없어야 정상 — 각각 Phase 3, 4에서 추가)
- `tests/test_parts.py` — 위 두 테스트만 포함
- git 커밋 1개: `feat: add Part template base class`

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] `car_assembly/parts.py`에 `Part` 클래스 외 다른 클래스가 아직 없는지 확인
- [ ] `selection_message()`가 `label`을 항상 대문자로 변환해서 조합하는지 확인 — 이후 엔진/브레이크/조향장치 선택 메시지가 전부 대문자(`GM`, `MANDO`, `BOSCH`)로 나오는 원본 동작의 근거가 되는 지점
- [ ] `run_label()`이 기본적으로 `label`을 그대로 반환하는지 확인
- [ ] `pytest tests/test_parts.py -v` 실행 결과 2개 테스트 모두 PASS
- [ ] 이 Phase만으로는 `assembly.py` 실행 결과에 아무 변화가 없어야 정상(아직 아무 데서도 `Part`를 실제로 사용하지 않음) — Phase 4~6에서 실제 부품 클래스가 이를 상속하면서 효과가 드러남
