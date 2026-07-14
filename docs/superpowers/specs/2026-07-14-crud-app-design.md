# CRUD 콘솔 애플리케이션 설계

## 배경 / 목적

`doc/PRD-crud.md`에 정의된 사전 지식 PoC(JSON 파싱/저장, QuickSort 알고리즘)를 실제로 구현해보고, 이를 활용해
JSON 파일 기반 CRUD 콘솔 애플리케이션을 만든다. 관리 대상 데이터는 이 저장소의 차량 조립 도메인
(차종/엔진/제동장치/조향장치 조합)을 그대로 사용한다. 본 작업은 `feature/crud-json-poc` 브랜치에서 진행한다.

## 언어 / 실행 환경

Python 3, 표준 라이브러리(`json`)만 사용. 외부 패키지 의존성 없음.

## 프로젝트 구조

```
car-assembly-21060979/
  car_assembly/
    car_type.py                    # 기존 (변경 없음, 그대로 재사용)
    parts.py                       # 기존 (변경 없음, 그대로 재사용)
    steering.py                    # 신규: 조향장치 코드/라벨
  crud/
    crud_app.py                    # 진입점, 메뉴 루프
    storage.py                     # JSON 파일 load/save
    quicksort.py                   # QuickSort 구현 (정렬 기준 필드 파라미터화)
    repository.py                  # CRUD 로직 (Create/Read/Update/Delete)
    data/cars.json                 # 런타임 저장 파일 (최초 실행 시 자동 생성)
  tests/
    test_crud_storage.py
    test_crud_quicksort.py
    test_crud_repository.py
  doc/PRD-crud.md
  docs/superpowers/specs/          # 본 설계 문서
```

## 도메인 재사용 (car_assembly 패키지)

같은 저장소이므로 별도 연동(submodule 등) 불필요. `crud/` 하위 모듈은 기존 `car_assembly.car_type`,
`car_assembly.parts`를 그대로 import한다.

- `car_type.py`: `CarType` enum, `CAR_TYPE_LABEL` 딕셔너리
- `parts.py`: `ENGINE_BY_CODE`, `BRAKE_BY_CODE` 딕셔너리, `Part.label` / `.selection_message()` / `.run_label()`
- steering(조향장치)은 아직 모듈화되어 있지 않으므로(assembly.py에 하드코딩) `car_assembly/steering.py`를
  신규로 추가한다: `STEERING_BY_CODE = {1: "BOSCH", 2: "MOBIS"}` 형태. 기존 `assembly.py`는 변경하지 않는다.

## 레코드 스키마

```json
{"id": 1, "car_type": 1, "engine_code": 1, "brake_code": 1, "steering_code": 1}
```

- `car_type`: 1=Sedan, 2=SUV, 3=Truck (`CarType`)
- `engine_code`: 1=GM, 2=TOYOTA, 3=WIA, 4=고장난엔진 (`ENGINE_BY_CODE`)
- `brake_code`: 1=MANDO, 2=CONTINENTAL, 3=BOSCH (`BRAKE_BY_CODE`)
- `steering_code`: 1=BOSCH, 2=MOBIS (`STEERING_BY_CODE`, 신규 모듈)
- `id`: 자동 증가 정수. 신규 생성 시 `max(existing ids) + 1` (레코드 없으면 1).

Create 단계에서 기존 `assembly.py`의 `is_valid_check` 부적합 조합 검사를 동일한 규칙으로 재사용한다:
- Sedan + Continental 불가
- SUV + Toyota 불가
- Truck + WIA 불가
- Truck + Mando 불가
- Bosch 브레이크는 Bosch 조향만 허용

## 메뉴 흐름 (car-assembly 스타일: 번호 입력 + 화면 clear + step state machine)

```
메인 메뉴
1. Create
   - 4단계 마법사: 차종 -> 엔진 -> 제동장치 -> 조향장치 (assembly.py의 show_menu/select_* 로직 재사용)
   - 부적합 조합이면 경고 후 해당 단계 재입력
   - 완료 시 id 자동 증가 부여 후 JSON 저장
2. Read
   1. 전체 목록: 정렬 기준 선택(id/car_type/engine_code/brake_code/steering_code) -> QuickSort로 정렬 후 출력
   2. ID로 검색: ID 입력 -> 일치 레코드 출력, 없으면 "해당 ID 없음"
3. Update
   - ID 입력 -> 레코드 표시 -> 수정할 필드 선택(car_type/engine_code/brake_code/steering_code) -> 새 값 입력 -> 유효성 재검사 -> 저장
4. Delete
   - ID 입력 -> 레코드 표시 -> 삭제 확인(y/n) -> 확인 시 삭제 후 저장
5. Exit
```

## 에러 처리

- `crud/data/cars.json` 없음: 빈 리스트로 시작 (최초 저장 시 파일 생성)
- 숫자가 아닌 입력, 범위 밖 입력: 기존 `is_valid_range` 패턴처럼 에러 메시지 출력 후 같은 단계 재입력
- 존재하지 않는 ID로 조회/수정/삭제: "해당 ID 없음" 메시지 후 메뉴 복귀 (예외 아님, 정상 흐름)
- Create/Update 시 부적합 부품 조합: 경고 메시지 후 해당 단계 재입력 (저장하지 않음)

## 테스트

pytest 스타일, 기존 `tests/test_car_type.py`처럼 plain assert 사용.

- `test_crud_storage.py`: JSON load/save 왕복, 파일 없을 때 빈 리스트 반환
- `test_crud_quicksort.py`: 정렬 정확성(빈 리스트, 단일 원소, 중복 값, 다양한 key 필드 기준)
- `test_crud_repository.py`: create(id 자동 증가), read(전체/검색), update(필드 수정, 존재하지 않는 id), delete(존재/미존재 id)

## 범위 제외

- 동시성/멀티유저 고려 없음 (단일 프로세스, 단일 파일)
- 인증/권한 없음
- 기존 `assembly.py` 로직 변경 없음 (steering.py 신규 추가만 발생)
