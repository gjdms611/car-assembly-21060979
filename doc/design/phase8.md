# Phase 8: advance_step + assembly.py 상태 전이 통합

## 목적

원본 main()의 step 이동 로직(뒤로가기 포함, 각 elif 분기 끝의 수동 증가)을 input() 없이 테스트 가능한 순수 함수로 분리하고, 만들자마자 main()에 연결한다.

## 사전 조건

Phase 7(CarBuild + assembly.py 핵심 판정 통합) 완료. pytest tests/test_assembly_characterization.py -v 실행해 통합 전 전부 PASS 확인.

## 구현 절차

### 태스크 8.1: 뒤로가기 STEP 4 -> 0

1. Test 작성 - tests/test_cli_state.py 파일을 새로 생성:

   ```python
   from car_assembly.cli import advance_step


   def test_back_navigation_from_step4_goes_to_0():
       assert advance_step(4, 0) == 0
   ```

2. 실행: pytest tests/test_cli_state.py -v -> ModuleNotFoundError로 실패 확인

3. 구현 - car_assembly/cli.py 파일을 새로 생성:

   ```python
   def advance_step(step: int, ans: int) -> int:
       if ans == 0 and step == 4:
           return 0
       return step
   ```

4. 실행: pytest tests/test_cli_state.py -v -> PASS 확인
5. 커밋: git add car_assembly/cli.py tests/test_cli_state.py && git commit -m "feat: add advance_step step4-to-0 back navigation"

### 태스크 8.2: 뒤로가기 일반 단계 -1

1. Test 추가:

   ```python
   def test_back_navigation_decrements_step():
       assert advance_step(2, 0) == 1
       assert advance_step(1, 0) == 0


   def test_back_navigation_at_step0_stays():
       assert advance_step(0, 0) == 0
   ```

2. 구현 - advance_step 함수 전체를 아래로 교체:

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

3. 실행: pytest tests/test_cli_state.py -v -> PASS 확인
4. 커밋: git commit -am "feat: add advance_step generic back navigation"

### 태스크 8.3: 정방향 이동

1. Test 추가:

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

2. 구현 - advance_step 마지막 return 문 앞에 추가:

   ```python
       if step in (0, 1, 2, 3):
           return step + 1
       return step
   ```

3. 실행: pytest tests/test_cli_state.py -v -> 전체 PASS 확인
4. 커밋: git commit -am "feat: add advance_step forward navigation"

### 태스크 8.4: assembly.py 통합 (strangler-fig 컷오버)

1. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
2. assembly.py 최상단 import 영역에 추가:

   ```python
   from car_assembly.cli import advance_step
   ```

3. assembly.py의 main() 안에서 아래 블록:

   ```python
       if ans == 0:
           if step == 4:
               step = 0
           elif step > 0:
               step = step - 1
           continue
   ```

   을 아래로 교체:

   ```python
       if ans == 0:
           step = advance_step(step, ans)
           continue
   ```

4. main()의 각 elif 분기 끝에서 수동으로 step을 증가시키던 코드(`step = 1`, `step = 2`, `step = 3`, `step = 4`)를 전부 지우고, main() 루프의 `if step == 0:` ~ 마지막 `elif step == 4:` 블록 전체가 끝난 직후(while 루프 안, 다음 반복 전)에 아래 한 줄을 추가:

   ```python
       step = advance_step(step, ans)
   ```

   즉 main()의 분기 구조는 다음과 같아진다:

   ```python
       if step == 0:
           select_car_type(ans)
           delay(800)
       elif step == 1:
           select_engine(ans)
           delay(800)
       elif step == 2:
           select_brake(ans)
           delay(800)
       elif step == 3:
           select_steering(ans)
           delay(800)
       elif step == 4:
           if ans == 1:
               run_produced_car()
               delay(2000)
           elif ans == 2:
               print("Test...")
               delay(1500)
               test_produced_car()
               delay(2000)

       step = advance_step(step, ans)
   ```

5. 통합 후 확인: pytest tests/test_assembly_characterization.py -v -> 여전히 전부 PASS 확인
6. 커밋: git add assembly.py && git commit -m "Integrate advance_step into assembly.py main loop (strangler-fig cutover, small step)"

## 이 Phase가 끝나면 존재해야 하는 것

- car_assembly/cli.py - advance_step(step, ans) 함수 하나만 포함
- assembly.py의 main() 루프가 단계 이동 로직을 전부 advance_step에 위임하고, 각 분기 안에는 select_*/run/test 호출과 delay만 남음
- git 커밋 4개(car_assembly 쪽 3개 + 통합 1개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] advance_step이 뒤로가기(0 입력)/정방향 이동/STEP4 유지 규칙을 원본과 동일하게 재현하는지 확인
- [ ] main()의 각 분기에 더 이상 `step = N` 형태의 수동 증가 코드가 없는지 확인(전부 advance_step 호출로 대체)
- [ ] pytest tests/test_cli_state.py -v 전체 PASS
- [ ] pytest tests/test_assembly_characterization.py -v 실행 결과 통합 전후 모두 PASS(회귀 없음, 특히 뒤로가기/네비게이션 테스트 케이스)
