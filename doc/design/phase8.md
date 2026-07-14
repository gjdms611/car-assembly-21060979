# Phase 8: 상태 전이 순수 함수 (advance_step)

## 목적

원본 main()의 step 이동 로직(뒤로가기 포함)을 input() 없이 테스트 가능한 순수 함수로 분리한다. CLI 5단계는 선형 흐름뿐이라 State 클래스 계층 대신 함수 하나로 충분하다고 판단했다(오버엔지니어링 방지).

## 사전 조건

Phase 7(CarBuild) 완료.

## 구현 절차

### 태스크 8.1: 뒤로가기: STEP 4 -> 0

1. Test 작성 - tests/test_cli_state.py 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
   from car_assembly.cli import advance_step


   def test_back_navigation_from_step4_goes_to_0():
       assert advance_step(4, 0) == 0
   ```

2. 실행: pytest tests/test_cli_state.py -v
   기대 결과: ModuleNotFoundError로 실패.

3. 구현 - car_assembly/cli.py 파일을 새로 생성하고 아래 내용을 그대로 넣는다:

   ```python
   def advance_step(step: int, ans: int) -> int:
       if ans == 0 and step == 4:
           return 0
       return step
   ```

4. 실행: pytest tests/test_cli_state.py -v -> PASS 확인
5. 커밋:
   git add car_assembly/cli.py tests/test_cli_state.py
   git commit -m "feat: add advance_step step4-to-0 back navigation"

### 태스크 8.2: 뒤로가기: 일반 단계 -1

1. Test 추가 - tests/test_cli_state.py 파일 끝에 추가:

   ```python
   def test_back_navigation_decrements_step():
       assert advance_step(2, 0) == 1
       assert advance_step(1, 0) == 0


   def test_back_navigation_at_step0_stays():
       assert advance_step(0, 0) == 0
   ```

2. 실행: pytest tests/test_cli_state.py -v
   기대 결과: test_back_navigation_decrements_step 실패(현재는 ans==0이면 step==4일 때만 0을 반환하고 그 외엔 step을 그대로 반환하므로).

3. 구현 - car_assembly/cli.py의 advance_step 함수 전체를 아래로 교체:

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

4. 실행: pytest tests/test_cli_state.py -v -> PASS 확인
5. 커밋: git commit -am "feat: add advance_step generic back navigation"

### 태스크 8.3: 정방향 이동

1. Test 추가 - tests/test_cli_state.py 파일 끝에 추가:

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

2. 실행: pytest tests/test_cli_state.py -v
   기대 결과: test_forward_navigation_increments_step 실패(현재는 ans!=0이면 항상 step을 그대로 반환하므로).

3. 구현 - car_assembly/cli.py의 advance_step 함수 마지막 return 문(맨 끝의 "return step")을 아래로 교체:

   ```python
       if step in (0, 1, 2, 3):
           return step + 1
       return step
   ```

   교체 후 advance_step 함수 전체는 다음과 같아야 한다:

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

4. 실행: pytest tests/test_cli_state.py -v -> 전체 PASS 확인
5. 커밋: git commit -am "feat: add advance_step forward navigation"

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/cli.py - advance_step(step, ans) 함수 하나만 포함(다른 CLI 함수는 아직 없음 - Phase 9에서 추가)
- tests/test_cli_state.py - 위 7개 테스트
- git 커밋 3개(누적 23개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] advance_step이 원본 main() 루프의 다음 규칙을 정확히 재현하는지 확인:
  - ans==0 이고 step==4 이면 -> 0으로 이동(처음 화면)
  - ans==0 이고 step>0 이면 -> step-1로 이동(한 단계 뒤로)
  - ans==0 이고 step==0 이면 -> 제자리(더 뒤로 갈 곳 없음)
  - ans!=0 이고 step이 0,1,2,3 중 하나면 -> step+1로 이동(다음 단계)
  - ans!=0 이고 step==4 이면 -> 제자리(RUN/TEST 화면은 계속 유지)
- [ ] advance_step이 input()이나 print()를 전혀 호출하지 않는 순수 함수인지 확인(부수효과 없음)
- [ ] pytest tests/test_cli_state.py -v 실행 결과 7개 테스트 모두 PASS
- [ ] car_assembly/cli.py에 아직 show_menu, is_valid_range, main 등이 없는지 확인(Phase 9에서 추가됨)
