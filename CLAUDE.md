# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code(claude.ai/code)에게 제공하는 가이드입니다.

## 명령어

Python 프로젝트

- 실행: `python assembly.py`
- 대화형 종료: 아무 프롬프트에서나 `exit` 입력
- 테스트 실행: `pytest`

## 비즈니스 규칙

차량 제조 순서: 차량 타입 선택 -> 부품(엔진, 제동장치, 조향장치) 각각 선택 -> 완성된 차량 테스트(선택 부품이 타입에 사용 가능한지 검사)

호환성 제약:
- Bosch 제동장치는 Bosch 조향장치와만 호환 (타사 조향장치 불가)
- Continental 제동장치는 Sedan에 사용 불가
- Toyota 엔진은 SUV에 사용 불가
- WIA 엔진은 Truck에 사용 불가
- Mando 제동장치는 Truck에 사용 불가

차량 타입은 향후 추가될 수 있음 (현재 Sedan/SUV/Truck) -> 새 타입 추가가 쉬운 구조로 설계.

## 관련 문서

- `doc/PRD.md`: 리팩토링 목적/범위(동작 유지 범위, 테스트 요구사항, Out of scope 등). 작업 전 반드시 참고할 것.
- `doc/PLAN.md`: 리팩토링 실행 계획. Phase/태스크 단위 TDD 체크리스트(테스트 작성 -> 구현 -> 커밋). 부품(엔진/제동/조향)을 클래스 계층(Template Method + Mixin)으로 설계.
