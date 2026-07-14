# Phase 10: 최종 슬림화 + 회귀 + 문서

## 목적

Phase 9까지 끝나면 assembly.py의 select_*/run_produced_car/test_produced_car/main()을 제외한 모든 함수가 이미 car_assembly에서 import되고 있다. 이 Phase는 남은 main() 루프까지 car_assembly.cli로 옮기고 assembly.py를 얇은 entry point로 축소하는 저위험 마무리 작업이다.

## 사전 조건

Phase 9(잔여 정리) 완료. pytest tests/test_assembly_characterization.py -v 실행해 전부 PASS 확인.

## 구현 절차

### 태스크 10.1: main()을 car_assembly.cli로 이동

1. 통합 전 확인: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인
2. assembly.py의 select_car_type/select_engine/select_brake/select_steering/run_produced_car/test_produced_car/main() 함수 전체와 `build = CarBuild()` 전역 선언을, car_assembly/cli.py 파일 끝으로 그대로 옮긴다(내용은 한 글자도 바꾸지 않는다 - 단순히 파일 위치만 이동).
3. car_assembly/cli.py 파일 상단 import 영역에 이 함수들이 필요로 하는 나머지 심볼을 추가한다:

   ```python
   from car_assembly.car import CarBuild
   from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE
   ```

   (CarType, CAR_TYPE_LABEL, car_type_selection_message, delay, clear, show_menu, is_valid_range, advance_step은 이미 Phase 8~9에서 car_assembly/cli.py 안에 있으므로 추가 import가 필요 없다.)

4. car_assembly/cli.py 맨 끝에 아래를 추가(이미 있다면 유지):

   ```python
   if __name__ == "__main__":
       main()
   ```

### 태스크 10.2: assembly.py를 얇은 entry point로 축소

1. assembly.py 파일 전체를 아래 4줄로 완전히 교체한다:

   ```python
   from car_assembly.cli import main

   if __name__ == "__main__":
       main()
   ```

2. 실행: pytest tests/test_assembly_characterization.py -v -> 전부 PASS 확인(assembly.py가 car_assembly.cli.main을 그대로 호출하므로 동일하게 동작해야 함)
3. 실행: pytest -v (전체 스위트) -> 지금까지 작성한 모든 테스트(캐릭터라이제이션 + car_type + parts + car + cli_state) 전부 PASS 확인
4. 커밋:
   ```bash
   git add assembly.py car_assembly/cli.py
   git commit -m "refactor: move main() into car_assembly.cli and slim assembly.py to a thin entry point"
   ```

### 태스크 10.3: 문서 정리

1. CLAUDE.md의 `## 명령어` 섹션에 `pytest` 명령이 이미 반영되어 있는지 확인한다(반영되어 있지 않다면 `- 테스트 실행: \`pytest\`` 한 줄을 추가한다).
2. 변경 사항이 있다면 커밋: `git add CLAUDE.md && git commit -m "docs: confirm pytest command in CLAUDE.md after final refactor"`

### 태스크 10.4: 최종 수동 확인 (선택)

자동화된 캐릭터라이제이션 테스트가 이미 모든 시나리오를 커버하므로 필수는 아니지만, 마지막으로 한 번 `python assembly.py`를 직접 실행해 콘솔 화면이 실제로도 원본과 동일하게 보이는지(색/커서/화면 클리어 등 텍스트 비교로는 확인하기 애매한 부분) 눈으로 확인한다.

### 태스크 10.5: 푸시

```bash
git push
```

## 이 Phase가 끝나면 존재해야 하는 것

- `assembly.py` - 정확히 4줄(빈 줄 포함)만 존재:
  ```python
  from car_assembly.cli import main

  if __name__ == "__main__":
      main()
  ```
- `car_assembly/cli.py` - 원본 assembly.py의 모든 로직(상수 없음, 부품 클래스에 위임된 select_*/run/test, advance_step 기반 main 루프) 보유
- 전체 pytest 스위트(캐릭터라이제이션 16개 + car_type 2개 + parts 다수 + car 다수 + cli_state 다수) 전부 PASS
- git 커밋 2~3개, 원격 저장소에 push 완료

## 구현 확인 체크리스트 (사람 리뷰용) - 최종 검수

- [ ] `assembly.py`에 `from car_assembly.cli import main` 외 다른 로직이 전혀 없는지 확인
- [ ] `pytest -v` 전체 실행 결과 모든 테스트 PASS
- [ ] `git log --oneline`으로 Phase 0부터 10까지, 매 assembly.py 통합 스텝이 "통합 전 PASS -> 변경 -> 통합 후 PASS -> 커밋" 순서를 지켰는지 확인 - 큰 스왑 커밋 하나가 아니라 작은 커밋들의 연속인지가 이번 재설계의 핵심 검증 포인트
- [ ] `git status`에 미커밋 변경 사항이 없는지 확인
- [ ] PRD.md의 Out of scope(신규 타입/부품 추가, UI 변경, 다국어화)에 해당하는 변경이 섞여 들어가지 않았는지 최종 확인
