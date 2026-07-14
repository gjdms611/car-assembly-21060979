from car_assembly.car_type import CarType
from car_assembly.car import CarBuild
from car_assembly.cli import advance_step, car_type_selection_message, clear, delay, is_valid_range, show_menu
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE

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