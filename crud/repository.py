from car_assembly.car_type import CarType
from crud.quicksort import quicksort
from crud.storage import DEFAULT_DATA_FILE, load_cars, save_cars

SEDAN = CarType.SEDAN.value
SUV = CarType.SUV.value
TRUCK = CarType.TRUCK.value

TOYOTA_ENGINE = 2
WIA_ENGINE = 3

MANDO_BRAKE = 1
CONTINENTAL_BRAKE = 2
BOSCH_BRAKE = 3

BOSCH_STEERING = 1


def is_valid_combination(car_type, engine_code, brake_code, steering_code):
    if car_type == SEDAN and brake_code == CONTINENTAL_BRAKE:
        return False, "Sedan에는 Continental제동장치 사용 불가"
    if car_type == SUV and engine_code == TOYOTA_ENGINE:
        return False, "SUV에는 TOYOTA엔진 사용 불가"
    if car_type == TRUCK and engine_code == WIA_ENGINE:
        return False, "Truck에는 WIA엔진 사용 불가"
    if car_type == TRUCK and brake_code == MANDO_BRAKE:
        return False, "Truck에는 Mando제동장치 사용 불가"
    if brake_code == BOSCH_BRAKE and steering_code != BOSCH_STEERING:
        return False, "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"
    return True, None


def next_id(cars):
    if not cars:
        return 1
    return max(car["id"] for car in cars) + 1


def create_car(car_type, engine_code, brake_code, steering_code, path=DEFAULT_DATA_FILE):
    valid, reason = is_valid_combination(car_type, engine_code, brake_code, steering_code)
    if not valid:
        return None, reason

    cars = load_cars(path)
    car = {
        "id": next_id(cars),
        "car_type": car_type,
        "engine_code": engine_code,
        "brake_code": brake_code,
        "steering_code": steering_code,
    }
    cars.append(car)
    save_cars(cars, path)
    return car, None


def list_cars(sort_key="id", path=DEFAULT_DATA_FILE):
    return quicksort(load_cars(path), sort_key)


def find_car(car_id, path=DEFAULT_DATA_FILE):
    for car in load_cars(path):
        if car["id"] == car_id:
            return car
    return None


def update_car(car_id, field, value, path=DEFAULT_DATA_FILE):
    cars = load_cars(path)
    target = None
    for car in cars:
        if car["id"] == car_id:
            target = car
            break

    if target is None:
        return None, "해당 ID 없음"

    candidate = dict(target)
    candidate[field] = value
    valid, reason = is_valid_combination(
        candidate["car_type"],
        candidate["engine_code"],
        candidate["brake_code"],
        candidate["steering_code"],
    )
    if not valid:
        return None, reason

    target[field] = value
    save_cars(cars, path)
    return target, None


def delete_car(car_id, path=DEFAULT_DATA_FILE):
    cars = load_cars(path)
    remaining = [car for car in cars if car["id"] != car_id]

    if len(remaining) == len(cars):
        return False

    save_cars(remaining, path)
    return True
