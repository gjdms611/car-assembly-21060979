# Phase 11: 수동 회귀 테스트 + 문서 정리

## 목적

pytest로는 검증하지 않은(또는 못하는) 실제 콘솔 실행 흐름을, 리팩토링 전 원본 assembly.py의 동작과 직접 비교해 최종 확인한다. 이 Phase가 끝나면 리팩토링이 완료된다.

## 사전 조건

Phase 10(assembly.py entry point 축소) 완료 - pytest -v 전체가 PASS 상태여야 함.

## 구현 절차

### 태스크 11.1: 수동 시나리오 - 정상 RUN

1. 실행: python assembly.py
2. 입력 순서: 1(Sedan) -> Enter -> 1(GM) -> Enter -> 1(Mando) -> Enter -> 2(Mobis) -> Enter -> 1(RUN)
3. 확인할 출력(순서대로):
   ```
   Car Type : Sedan
   Engine   : GM
   Brake    : Mando
   Steering : Mobis
   자동차가 동작됩니다.
   ```
4. 이 출력이 리팩토링 전 원본 assembly.py로 동일한 입력을 넣었을 때의 출력과 한 글자도 다르지 않은지 확인한다(원본은 `git show HEAD~29:assembly.py > /tmp/original_assembly.py` 등으로 꺼내 임시 비교 가능. 단, 이 비교용 임시 파일은 커밋하지 않는다).

### 태스크 11.2: 수동 시나리오 - 비호환 RUN/TEST

1. 실행: python assembly.py
2. 입력 순서: 1(Sedan) -> 1(GM) -> 2(Continental) -> 2(Mobis) -> 1(RUN)
3. 확인: `자동차가 동작되지 않습니다` 출력
4. 다시 실행해 동일 조합에서 마지막에 2(Test) 입력
5. 확인:
   ```
   Test...
   FAIL
   Sedan에는 Continental제동장치 사용 불가
   ```

### 태스크 11.3: 수동 시나리오 - 고장난 엔진 quirk

1. 실행: python assembly.py
2. 입력 순서: 1(Sedan) -> 4(고장난 엔진) -> 1(Mando) -> 2(Mobis) -> 1(RUN)
3. 확인:
   ```
   엔진이 고장나있습니다.
   자동차가 움직이지 않습니다.
   ```
4. 다시 실행해 동일 조합에서 마지막에 2(Test) 입력
5. 확인: `Test...` 다음 줄에 `PASS`가 출력되는지 확인한다(엔진이 고장났는데도 TEST는 PASS로 나오는 것이 원본의 quirk이며, 정상적인 동작이다 - 이 결과가 나오지 않으면 리팩토링 중 quirk가 깨진 것이므로 Phase 7의 test_report() 구현을 다시 확인해야 한다).

### 태스크 11.4: 수동 시나리오 - 네비게이션/에러/종료

1. 실행: python assembly.py
2. 차량 타입 단계에서 범위 밖 숫자(예: 9)를 입력 -> `ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능` 출력 확인 후 같은 화면 유지 확인
3. 1(Sedan) 입력 후 엔진 단계에서 0 입력 -> 차량 타입 선택 화면으로 돌아가는지 확인
4. 차량 타입 단계에서 0 입력 -> 에러 없이 같은 화면이 유지되는지 확인(원본에서 step 0에서 0 입력은 `is_valid_range(0, 0)`이 False를 반환해 에러 메시지가 뜨는 경로임 - `ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능` 출력 확인)
5. 1 -> 1 -> 1 -> 2 (조립 완료 화면)까지 진행한 뒤 0 입력 -> 차량 타입 선택 화면(처음)으로 돌아가는지 확인
6. 아무 단계에서나 `exit` 입력 -> `바이바이` 출력 후 프로그램 종료 확인

### 태스크 11.5: CLAUDE.md에 pytest 명령 추가

1. CLAUDE.md 파일을 열어 `## 명령어` 섹션을 찾는다.
2. 그 섹션의 기존 항목(`- 실행: ...`, `- 대화형 종료: ...`) 바로 아래에 새 줄로 아래 항목을 추가한다:

   ```markdown
   - 테스트 실행: `pytest`
   ```

3. 커밋:
   ```bash
   git add CLAUDE.md
   git commit -m "docs: add pytest command to CLAUDE.md after refactor"
   ```

### 태스크 11.6: 푸시

1. 실행: `git push`
2. 실행 결과에 에러가 없는지 확인(원격 저장소에 지금까지의 모든 커밋이 반영되어야 함).

## 이 Phase가 끝나면 존재해야 하는 것

- 위 11.1~11.4의 모든 수동 시나리오가 원본과 동일하게 동작함을 사람이 직접 확인
- CLAUDE.md에 `- 테스트 실행: \`pytest\`` 항목 추가
- git 커밋 1개(누적 30개), 원격 저장소에 push 완료

## 구현 확인 체크리스트 (사람 리뷰용) - 최종 검수

- [ ] 11.1~11.4의 4개 시나리오 전부 원본과 동일한 출력을 냈는지 직접 눈으로 확인(스크린샷 또는 터미널 로그로 남겨두면 좋음)
- [ ] `pytest -v` 전체 실행 결과 모든 테스트 PASS (Phase 1~9에서 작성한 테스트 총 30개 이상)
- [ ] `git log --oneline`으로 전체 커밋 히스토리가 Phase 1부터 11까지 TDD 순서(테스트 -> 구현 -> 커밋)를 따랐는지 확인
- [ ] `git status`에 미커밋 변경 사항이 없는지 확인
- [ ] `git push` 완료 후 원격 저장소(GitHub)에서 최신 커밋이 반영되었는지 확인
- [ ] PRD.md의 Out of scope(신규 타입/부품 추가, UI 변경, 다국어화)에 해당하는 변경이 실수로 섞여 들어가지 않았는지 최종 확인
