# Phase 10: assembly.py entry point 축소

## 목적

원본 assembly.py에 있던 모든 로직(Phase 1~9에서 car_assembly 패키지로 이미 옮김)을 제거하고, assembly.py를 car_assembly.cli.main()을 호출하는 얇은 진입점으로 축소한다.

## 사전 조건

Phase 9(CLI 이식) 완료 - car_assembly.cli.main()이 완성되어 있어야 함.

## 구현 절차

### 태스크 10.1: assembly.py 전체 교체

1. 구현 - assembly.py 파일의 기존 내용을 전부 지우고 아래 내용으로 완전히 교체한다:

   ```python
   from car_assembly.cli import main

   if __name__ == "__main__":
       main()
   ```

   원본에 있던 CLEAR_SCREEN, 각종 상수, delay/clear/show_menu/is_valid_range/select_*/run_produced_car/test_produced_car/main 함수 정의는 전부 제거한다. 이 파일에는 위 4줄만 남아야 한다.

2. 실행: pytest -v (프로젝트 전체 테스트)
   기대 결과: 지금까지 작성된 모든 테스트가 전부 PASS.

3. 커밋: git commit -am "refactor: slim assembly.py down to a thin entry point"

## 이 Phase가 끝나면 존재해야 하는 것

- assembly.py - 정확히 아래 4줄(빈 줄 포함)만 존재:
  ```python
  from car_assembly.cli import main

  if __name__ == "__main__":
      main()
  ```
- git 커밋 1개(누적 29개)

## 구현 확인 체크리스트 (사람 리뷰용)

- [ ] assembly.py에 원본 로직(전역 상수, show_menu, is_valid_range, select_*, run_produced_car, test_produced_car, main 함수 본문)이 전혀 남아있지 않은지 확인 - car_assembly.cli.main import 및 호출 코드만 있어야 함
- [ ] pytest -v (전체 스위트) 실행 결과 전부 PASS
- [ ] python assembly.py로 직접 실행했을 때 원본과 동일하게 동작하는지 확인(자세한 시나리오는 Phase 11에서 진행)
