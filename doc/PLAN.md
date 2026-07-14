# 자동차 조립 시뮬레이터 리팩토링 계획

> **실행 방법:** superpowers:subagent-driven-development (추천) 또는 superpowers:executing-plans 로 태스크 단위 진행. 체크박스(`- [ ]`)로 진행상황 추적.

**목표:** 절차지향 단일 파일(`assembly.py`)을, 동작(콘솔 UI/판정 결과)은 완전히 동일하게 유지한 채 유지보수 가능한 구조로 재구성하고 pytest 테스트를 도입한다.

## 통합 전략: 점진적(strangler-fig) 컷오버

**이전 설계의 문제점:** 처음에는 `car_assembly` 패키지를 assembly.py와 완전히 분리된 채로 전부 만든 뒤, 마지막 Phase에서 assembly.py 전체를 한 번에 새 패키지 호출로 스왑하는 방식이었다. 이러면 assembly.py가 여러 Phase 동안 전혀 검증되지 않다가, 가장 위험한 "전체 교체" 커밋 하나에 리스크가 몰린다.

**새 설계:** 부품 클래스(또는 함수)를 하나 만들 때마다 **그 자리에서 바로 assembly.py의 해당 부분만 교체**한다. assembly.py는 리팩토링 시작부터 끝까지 매 커밋마다 실행 가능한 상태를 유지하며, 새 기능이 아니라 기존 동작을 고정하는 것이 목적이므로 일반적인 "실패 -> 구현 -> 통과" TDD 대신 **캐릭터라이제이션 테스트(Phase 0)를 이용한 "초록 -> 변경 -> 초록" 회귀 확인**을 각 통합 스텝마다 반복한다(Michael Feathers의 레거시 코드 TDD 기법).

모든 assembly.py 통합 스텝은 다음 순서를 지킨다:
1. `pytest tests/test_assembly_characterization.py -v` 실행 -> 통합 전 전부 PASS(초록) 확인
2. assembly.py의 해당 함수만 최소 범위로 교체
3. `pytest tests/test_assembly_characterization.py -v` 재실행 -> 여전히 전부 PASS(초록) 확인
4. 실패하면 assembly.py 변경을 되돌리고 원인 파악(테스트가 아니라 코드를 고친다)
5. 커밋(car_assembly 쪽 신규 코드 커밋과는 분리된, "통합" 전용 커밋)

## 설계 노트 (클래스 구조)

- 엔진·제동장치·조향장치는 클래스 계층으로 모델링한다. 세 부품 모두 "선택 메시지 출력", "리포트용 라벨" 로직이 동일한 형태라 공통 베이스 `Part`에 **템플릿 메서드**로 올린다.
- 엔진과 제동장치만 "특정 차량 타입과 호환 안 됨"이라는 동일한 규칙 형태를 가지므로, 이 부분만 `CarTypeConstrained` **믹스인**으로 분리해 두 클래스가 공유한다(조향장치는 이 제약이 없으므로 믹스인을 받지 않는다).
- 제동장치가 조향장치 제약(Bosch 브레이크는 Bosch 조향장치 필요)을 검사하는 로직은 제동장치 쪽에만 존재 — 원본에서도 이 규칙의 주체는 브레이크이므로 자연스러운 위치.
- **의도적으로 도입하지 않은 패턴 (오버엔지니어링 방지):**
  - CLI 5단계는 선형 흐름뿐이라 State 패턴/클래스 계층 대신 순수 함수(`advance_step`) 유지.
  - `CarBuild`는 필드 4개를 순차로 채우는 것뿐이라 Builder 패턴 대신 평범한 mutable dataclass 유지.
  - 부품 조회는 3~4개짜리 `dict` 팩토리로 충분 — Factory 클래스나 등록 데코레이터는 불필요한 간접화.
- 호환성 판정 순서(`CarBuild.first_incompatibility`)는 `or` 체이닝 3개로 충분.

**Tech Stack:** Python 표준 라이브러리만 사용(외부 의존성 없음), pytest.

## Global Constraints (PRD.md 기준, 모든 Phase 공통)

- 콘솔 메뉴 텍스트, 한글 안내 메시지, 입력 처리 방식(숫자 입력 / `0` 뒤로가기 / `exit` 종료)은 리팩토링 전후 **한 글자도 다르지 않게** 유지 — Phase 0의 캐릭터라이제이션 테스트로 매 스텝마다 자동 검증
- 호환성 판정 결과(`run`/`test` 양쪽) 동일
- pytest 기반 유닛테스트, 호환성 규칙 + 상태 전이 커버리지 확보
- 확장 시 코드 수정은 허용하되, 규칙은 한 곳(해당 부품 클래스)에서만 관리
- Out of scope: 신규 차량 타입/부품 실제 추가, UI/UX 변경, 다국어화

## 파일 구조 (최종 목표)

```
car_assembly/
  __init__.py
  car_type.py       # CarType Enum + 라벨
  parts.py          # Part(템플릿 베이스) + CarTypeConstrained(믹스인)
                     # + EnginePart/BrakePart/SteeringPart 계열 + *_BY_CODE 팩토리
  car.py            # CarBuild (선택된 부품 객체 보관 + 리포트)
  cli.py            # 메뉴 출력, 상태 전이, main() 루프
assembly.py         # 얇은 entry point: cli.main() 호출만
tests/
  test_assembly_characterization.py  # Phase 0 - 원본 동작 고정용 안전망
  test_car_type.py
  test_parts.py
  test_car.py
  test_cli_state.py
```

## Phase 개요

| Phase | 내용 | car_assembly 변경 | assembly.py 통합 |
|---|---|---|---|
| 0 | 캐릭터라이제이션 테스트 | - | - (안전망만 추가) |
| 1 | CarType | car_type.py 생성 | select_car_type, run_produced_car 차량타입 라인 |
| 2 | Part 템플릿 베이스 | parts.py 생성 | 없음(구체 부품 없음) |
| 3 | CarTypeConstrained 믹스인 | parts.py 확장 | 없음(구체 부품 없음) |
| 4 | EnginePart 계열 | parts.py 확장 | select_engine, run_produced_car 엔진 라인 |
| 5 | BrakePart 계열 | parts.py 확장 | select_brake, run_produced_car 브레이크 라인 |
| 6 | SteeringPart 계열 | parts.py 확장 | select_steering, run_produced_car 조향 라인 |
| 7 | CarBuild | car.py 생성 | is_valid_check / run_produced_car(호환성) / test_produced_car |
| 8 | advance_step | cli.py 생성(부분) | main()의 step 이동 로직 |
| 9 | 잔여 정리 | cli.py 완성(show_menu/is_valid_range 이관) | 전역변수 q0~q4 제거, main()이 CarBuild 하나만 사용 |
| 10 | 최종 슬림화 | - | assembly.py를 얇은 entry point로 축소, 문서 정리 |

---

## Phase 0: 캐릭터라이제이션 테스트 작성

원본 assembly.py를 서브프로세스로 실행해 stdin을 흘려보내고 stdout을 검증하는 안전망을 가장 먼저 만든다. 상세 코드/체크리스트는 `doc/design/phase0.md` 참고.

- [x] 0.1 `tests/test_assembly_characterization.py` 작성 (16개 시나리오: 호환성 규칙 5개, 고장난 엔진 quirk, 뒤로가기, 범위 오류, 종료)
- [x] 실행 결과 16개 전부 PASS(원본 기준) 확인 후 커밋

## Phase 1: `CarType` + assembly.py 통합

상세 코드는 `doc/design/phase1.md` 참고.

- [x] 1.1 `car_assembly/__init__.py` 생성
- [x] 1.2 `car_assembly/car_type.py`에 `CarType` enum + `CAR_TYPE_LABEL` 작성(TDD: 테스트 먼저 실패 확인 -> 구현 -> 통과)
- [x] 1.3 **assembly.py 통합**: `select_car_type()`의 if/elif 메시지 분기를 `CAR_TYPE_LABEL[CarType(a)]` 한 줄로, `run_produced_car()`의 `Car Type :` 분기도 동일하게 교체. 통합 전/후 캐릭터라이제이션 테스트 PASS 확인 후 커밋.

## Phase 2: `Part` 템플릿 베이스

상세 코드는 `doc/design/phase2.md` 참고. 아직 구체적인 부품 클래스가 없어 assembly.py에 연결할 대상이 없다 — 통합 없이 순수 추가만 진행.

- [x] 2.1 `car_assembly/parts.py`에 `Part` 추상 베이스(`selection_message`/`run_label`) 작성
- [x] assembly.py 통합 없음(사유: 통합 대상 부재)

## Phase 3: `CarTypeConstrained` 믹스인

상세 코드는 `doc/design/phase3.md` 참고. Phase 2와 동일한 사유로 통합 없음.

- [x] 3.1 `car_assembly/parts.py`에 `CarTypeConstrained` 믹스인 작성
- [x] assembly.py 통합 없음(사유: 통합 대상 부재)

## Phase 4: `EnginePart` 계열 + assembly.py 통합

상세 코드는 `doc/design/phase4.md` 참고.

- [x] 4.1~4.5 `EnginePart`, `GMEngine`/`ToyotaEngine`/`WIAEngine`/`BrokenEngine`, `ENGINE_BY_CODE` 작성(TDD)
- [x] 4.6 **assembly.py 통합**: `select_engine()`을 `ENGINE_BY_CODE[a]().selection_message()`로, `run_produced_car()`의 엔진 출력 분기를 `ENGINE_BY_CODE[q1]().run_label()`(None이면 줄 생략)로 교체. 캐릭터라이제이션 테스트로 회귀 확인 후 커밋.

## Phase 5: `BrakePart` 계열 + assembly.py 통합

상세 코드는 `doc/design/phase5.md` 참고.

- [x] 5.1~5.4 `BrakePart`, `MandoBrake`/`ContinentalBrake`/`BoschBrake`, `BRAKE_BY_CODE` 작성(TDD)
- [x] 5.5 **assembly.py 통합**: `select_brake()`와 `run_produced_car()`의 브레이크 출력 분기를 `BRAKE_BY_CODE` 위임으로 교체. 캐릭터라이제이션 테스트로 회귀 확인 후 커밋.

## Phase 6: `SteeringPart` 계열 + assembly.py 통합

상세 코드는 `doc/design/phase6.md` 참고.

- [ ] 6.1~6.3 `SteeringPart`, `BoschSteering`/`MobisSteering`, `STEERING_BY_CODE` 작성(TDD)
- [ ] 6.4 **assembly.py 통합**: `select_steering()`과 `run_produced_car()`의 조향장치 출력 분기를 `STEERING_BY_CODE` 위임으로 교체. 캐릭터라이제이션 테스트로 회귀 확인 후 커밋.

## Phase 7: `CarBuild` + assembly.py 핵심 판정 로직 통합

상세 코드는 `doc/design/phase7.md` 참고. 이 Phase가 원본에서 가장 위험했던 부분(교차 부품 호환성 판정)을 다루지만, 이미 부품 4종이 전부 assembly.py에 연결되어 있어 통합 범위가 함수 3개로 작고 명확하다.

- [ ] 7.1~7.4 `CarBuild` 데이터클래스(선택 보관 + `first_incompatibility`/`is_compatible`/`run_report`/`test_report`) 작성(TDD)
- [ ] 7.5 **assembly.py 통합 (1/3)**: `is_valid_check()`를 `CarBuild(...).is_compatible()` 위임으로 교체
- [ ] 7.6 **assembly.py 통합 (2/3)**: `test_produced_car()`를 `CarBuild(...).test_report()` 위임으로 교체
- [ ] 7.7 **assembly.py 통합 (3/3)**: `run_produced_car()`를 `CarBuild(...).run_report()` 위임으로 교체
- [ ] 7.8 **정리**: 이제 아무도 호출하지 않는 `is_valid_check()`와 원본 호환성 상수(`SEDAN`~`MOBIS`)를 삭제(사용자의 변경이 만든 미사용 코드 제거 원칙)

## Phase 8: `advance_step` + assembly.py 상태 전이 통합

상세 코드는 `doc/design/phase8.md` 참고.

- [ ] 8.1~8.3 `car_assembly/cli.py`에 `advance_step(step, ans)` 순수 함수 작성(TDD)
- [ ] 8.4 **assembly.py 통합**: `main()`의 `0` 뒤로가기 분기와 각 단계 끝의 수동 `step = step + 1` 증가 코드를 `step = advance_step(step, ans)` 호출로 교체. 캐릭터라이제이션 테스트로 회귀 확인 후 커밋.

## Phase 9: 잔여 정리 (메뉴/상태를 car_assembly로 완전 이관)

상세 코드는 `doc/design/phase9.md` 참고.

- [ ] 9.1 `show_menu`를 `car_assembly/cli.py`로 이동(순수 추가) + assembly.py는 import로 대체
- [ ] 9.2 `is_valid_range`를 `car_assembly/cli.py`로 이동 + assembly.py는 import로 대체
- [ ] 9.3 `car_type_selection_message` 헬퍼를 `car_assembly/cli.py`에 추가 + `select_car_type()`이 이를 사용하도록 교체
- [ ] 9.4 **전역 상태 통합**: 모듈 전역 `q0~q4` int를 전부 제거하고 단일 `build = CarBuild()` 전역 객체로 교체. `select_*` 함수들이 `build.car_type`/`build.engine`/... 필드에 직접 대입하도록 수정하고, `is_valid_check`/`run_produced_car`/`test_produced_car`가 매번 int로부터 재구성하던 로직(`build_from_globals`)을 제거하고 `build`를 직접 사용하도록 수정

각 스텝마다 캐릭터라이제이션 테스트로 회귀 확인 후 커밋.

## Phase 10: 최종 슬림화 + 회귀 + 문서

상세 코드는 `doc/design/phase10.md` 참고. Phase 9까지 끝나면 assembly.py의 모든 함수가 이미 car_assembly에 위임하고 있으므로, 이 Phase는 "내용을 옮기고 얇게 만드는" 저위험 마무리 작업이다.

- [ ] 10.1 `main()` 루프(및 이미 위임 상태인 나머지 함수)를 `car_assembly/cli.py`로 옮긴다
- [ ] 10.2 `assembly.py`를 `from car_assembly.cli import main` + `if __name__ == "__main__": main()` 4줄로 축소
- [ ] 10.3 캐릭터라이제이션 테스트 + 전체 pytest 스위트 최종 실행(전부 PASS 확인)
- [ ] 10.4 CLAUDE.md 최종 점검(이미 `pytest` 명령 반영되어 있음 - 추가 변경 불필요하면 스킵)
- [ ] 10.5 푸시

## Self-Review 체크리스트

- PRD.md의 5개 호환성 규칙 전부 Phase 4~7에서 부품 클래스 단위 pytest + Phase 0 캐릭터라이제이션 테스트로 이중 커버됨
- "동작 유지"는 Phase 0 캐릭터라이제이션 테스트가 Phase 1부터 Phase 10까지 매 통합 스텝마다 자동으로 재확인 — 더 이상 "마지막에 한번" 수동 회귀에 의존하지 않음
- 중복 제거: `selection_message`/`run_label`은 `Part`에만, 차량 타입 제약은 `CarTypeConstrained`에만 존재
- 확장성: 새 부품 추가 시 서브클래스 + `*_BY_CODE` 항목 하나만 추가하면 반영됨
- 오버엔지니어링 방지: State/Builder/Factory 클래스 도입하지 않은 이유는 상단 "설계 노트"에 명시
- Out of scope(신규 타입/부품 추가, UI 변경, 다국어화)는 어떤 Phase에도 포함하지 않음
