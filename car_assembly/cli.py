import sys
import time

from car_assembly.car import CarBuild
from car_assembly.car_type import CAR_TYPE_LABEL, CarType
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE

CLEAR_SCREEN = "\033[H\033[2J"


def delay(ms):
    time.sleep(ms / 1000.0)


def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()


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


STEP_CAR_TYPE = 0
STEP_ENGINE = 1
STEP_BRAKE = 2
STEP_STEERING = 3
STEP_RUN_TEST = 4


def show_menu(step):
    clear()
    if step == STEP_CAR_TYPE:
        print("        ______________")
        print("       /|            |")
        print("  ____/_|_____________|____")
        print(" |                      O  |")
        print(" '-(@)----------------(@)--'")
        print("===============================")
        print("어떤 차량 타입을 선택할까요?")
        print("1. Sedan")
        print("2. SUV")
        print("3. Truck")
    elif step == STEP_ENGINE:
        print("어떤 엔진을 탑재할까요?")
        print("0. 뒤로가기")
        print("1. GM")
        print("2. TOYOTA")
        print("3. WIA")
        print("4. 고장난 엔진")
    elif step == STEP_BRAKE:
        print("어떤 제동장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. MANDO")
        print("2. CONTINENTAL")
        print("3. BOSCH")
    elif step == STEP_STEERING:
        print("어떤 조향장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. BOSCH")
        print("2. MOBIS")
    elif step == STEP_RUN_TEST:
        print("멋진 차량이 완성되었습니다.")
        print("0. 처음 화면으로 돌아가기")
        print("1. RUN")
        print("2. Test")
    print("===============================")


def is_valid_range(step, ans):
    if step == STEP_CAR_TYPE and not (1 <= ans <= 3):
        print("ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능")
        return False
    if step == STEP_ENGINE and not (0 <= ans <= 4):
        print("ERROR :: 엔진은 1 ~ 4 범위만 선택 가능")
        return False
    if step == STEP_BRAKE and not (0 <= ans <= 3):
        print("ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능")
        return False
    if step == STEP_STEERING and not (0 <= ans <= 2):
        print("ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능")
        return False
    if step == STEP_RUN_TEST and not (0 <= ans <= 2):
        print("ERROR :: Run 또는 Test 중 하나를 선택 필요")
        return False
    return True


def car_type_selection_message(car_type: CarType) -> str:
    return f"차량 타입으로 {CAR_TYPE_LABEL[car_type]}을 선택하셨습니다."


build = CarBuild()

def select_car_type(a):
    global build
    build.car_type = CarType(a)
    print(car_type_selection_message(build.car_type))

def select_engine(a):
    global build
    build.engine = ENGINE_BY_CODE[a]()
    print(build.engine.selection_message())

def select_brake(a):
    global build
    build.brake = BRAKE_BY_CODE[a]()
    print(build.brake.selection_message())

def select_steering(a):
    global build
    build.steering = STEERING_BY_CODE[a]()
    print(build.steering.selection_message())

def run_produced_car():
    for line in build.run_report():
        print(line)

def test_produced_car():
    print(build.test_report())

def main():
    step = 0
    while True:
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == 0:
            step = advance_step(step, ans)
            continue

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


if __name__ == "__main__":
    main()
