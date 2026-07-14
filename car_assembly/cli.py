import sys
import time

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
