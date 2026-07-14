from car_assembly.car_type import CAR_TYPE_LABEL, CarType
from car_assembly.car import CarBuild
from car_assembly.cli import advance_step, clear, delay, is_valid_range, show_menu
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE

q0 = 0
q1 = 0
q2 = 0
q3 = 0
q4 = 0

def select_car_type(a):
    global q0
    q0 = a
    print(f"차량 타입으로 {CAR_TYPE_LABEL[CarType(a)]}을 선택하셨습니다.")

def select_engine(a):
    global q1
    q1 = a
    print(ENGINE_BY_CODE[a]().selection_message())

def select_brake(a):
    global q2
    q2 = a
    print(BRAKE_BY_CODE[a]().selection_message())

def select_steering(a):
    global q3
    q3 = a
    print(STEERING_BY_CODE[a]().selection_message())

def build_from_globals():
    return CarBuild(
        car_type=CarType(q0),
        engine=ENGINE_BY_CODE[q1](),
        brake=BRAKE_BY_CODE[q2](),
        steering=STEERING_BY_CODE[q3](),
    )

def run_produced_car():
    for line in build_from_globals().run_report():
        print(line)

def test_produced_car():
    print(build_from_globals().test_report())

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