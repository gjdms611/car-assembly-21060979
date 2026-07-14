# crud/crud_app.py
import sys

from car_assembly.car_type import CAR_TYPE_LABEL, CarType
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE
from car_assembly.steering import STEERING_BY_CODE
from crud.repository import create_car, delete_car, find_car, list_cars, update_car

CLEAR_SCREEN = "\033[H\033[2J"

FIELD_LABEL = {
    "car_type": "차종",
    "engine_code": "엔진",
    "brake_code": "제동장치",
    "steering_code": "조향장치",
}


def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()


def read_int(prompt, low, high):
    while True:
        buf = input(prompt).strip()
        if buf == "exit":
            return None
        try:
            value = int(buf)
        except ValueError:
            print(f"ERROR :: {low} ~ {high} 범위의 숫자만 입력 가능")
            continue
        if value < low or value > high:
            print(f"ERROR :: {low} ~ {high} 범위만 선택 가능")
            continue
        return value


def describe_car(car):
    car_type_label = CAR_TYPE_LABEL[CarType(car["car_type"])]
    engine_label = ENGINE_BY_CODE[car["engine_code"]]().label
    brake_label = BRAKE_BY_CODE[car["brake_code"]]().label
    steering_label = STEERING_BY_CODE[car["steering_code"]]
    return (
        f"ID={car['id']} | 차종={car_type_label} | 엔진={engine_label} | "
        f"제동장치={brake_label} | 조향장치={steering_label}"
    )


def prompt_car_type():
    print("어떤 차량 타입을 선택할까요?")
    print("1. Sedan")
    print("2. SUV")
    print("3. Truck")
    return read_int("INPUT > ", 1, 3)


def prompt_engine():
    print("어떤 엔진을 탑재할까요?")
    print("1. GM")
    print("2. TOYOTA")
    print("3. WIA")
    print("4. 고장난 엔진")
    return read_int("INPUT > ", 1, 4)


def prompt_brake():
    print("어떤 제동장치를 선택할까요?")
    print("1. MANDO")
    print("2. CONTINENTAL")
    print("3. BOSCH")
    return read_int("INPUT > ", 1, 3)


def prompt_steering():
    print("어떤 조향장치를 선택할까요?")
    print("1. BOSCH")
    print("2. MOBIS")
    return read_int("INPUT > ", 1, 2)


def do_create():
    clear()
    car_type = prompt_car_type()
    if car_type is None:
        return
    engine_code = prompt_engine()
    if engine_code is None:
        return
    brake_code = prompt_brake()
    if brake_code is None:
        return
    steering_code = prompt_steering()
    if steering_code is None:
        return

    car, err = create_car(car_type, engine_code, brake_code, steering_code)
    if err is not None:
        print(f"ERROR :: {err}")
    else:
        print(f"생성됨 -> {describe_car(car)}")
    input("계속하려면 Enter > ")


def do_read():
    clear()
    print("1. 전체 목록")
    print("2. ID로 검색")
    choice = read_int("INPUT > ", 1, 2)
    if choice is None:
        return

    if choice == 1:
        print("정렬 기준을 선택하세요")
        print("1. id  2. car_type  3. engine_code  4. brake_code  5. steering_code")
        sort_choice = read_int("INPUT > ", 1, 5)
        if sort_choice is None:
            return
        sort_key = ["id", "car_type", "engine_code", "brake_code", "steering_code"][sort_choice - 1]
        cars = list_cars(sort_key=sort_key)
        if not cars:
            print("등록된 데이터 없음")
        for car in cars:
            print(describe_car(car))
    else:
        car_id = read_int("검색할 ID > ", 1, 10**9)
        if car_id is None:
            return
        car = find_car(car_id)
        print(describe_car(car) if car else "해당 ID 없음")

    input("계속하려면 Enter > ")


def do_update():
    clear()
    car_id = read_int("수정할 ID > ", 1, 10**9)
    if car_id is None:
        return
    car = find_car(car_id)
    if car is None:
        print("해당 ID 없음")
        input("계속하려면 Enter > ")
        return

    print(describe_car(car))
    print("수정할 필드를 선택하세요")
    print("1. car_type  2. engine_code  3. brake_code  4. steering_code")
    field_choice = read_int("INPUT > ", 1, 4)
    if field_choice is None:
        return
    field = ["car_type", "engine_code", "brake_code", "steering_code"][field_choice - 1]

    prompt_by_field = {
        "car_type": prompt_car_type,
        "engine_code": prompt_engine,
        "brake_code": prompt_brake,
        "steering_code": prompt_steering,
    }
    new_value = prompt_by_field[field]()
    if new_value is None:
        return

    updated, err = update_car(car_id, field, new_value)
    if err is not None:
        print(f"ERROR :: {err}")
    else:
        print(f"수정됨 -> {describe_car(updated)}")
    input("계속하려면 Enter > ")


def do_delete():
    clear()
    car_id = read_int("삭제할 ID > ", 1, 10**9)
    if car_id is None:
        return
    car = find_car(car_id)
    if car is None:
        print("해당 ID 없음")
        input("계속하려면 Enter > ")
        return

    print(describe_car(car))
    confirm = input("정말 삭제할까요? (y/n) > ").strip().lower()
    if confirm == "y":
        delete_car(car_id)
        print("삭제됨")
    else:
        print("취소됨")
    input("계속하려면 Enter > ")


def main():
    while True:
        clear()
        print("메인 메뉴")
        print("1. Create")
        print("2. Read")
        print("3. Update")
        print("4. Delete")
        print("5. Exit")
        choice = input("INPUT > ").strip()

        if choice == "exit" or choice == "5":
            print("바이바이")
            break
        try:
            choice_num = int(choice)
        except ValueError:
            continue
        if choice_num == 1:
            do_create()
        elif choice_num == 2:
            do_read()
        elif choice_num == 3:
            do_update()
        elif choice_num == 4:
            do_delete()


if __name__ == "__main__":
    main()
