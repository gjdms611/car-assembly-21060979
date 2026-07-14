import os

from crud.storage import load_cars, save_cars


def test_load_cars_missing_file_returns_empty_list(tmp_path):
    path = os.path.join(tmp_path, "does_not_exist.json")
    assert load_cars(path) == []


def test_save_then_load_round_trip(tmp_path):
    path = os.path.join(tmp_path, "nested_dir", "cars.json")
    cars = [
        {"id": 1, "car_type": 1, "engine_code": 1, "brake_code": 1, "steering_code": 1},
        {"id": 2, "car_type": 2, "engine_code": 2, "brake_code": 3, "steering_code": 1},
    ]

    save_cars(cars, path)
    loaded = load_cars(path)

    assert loaded == cars
