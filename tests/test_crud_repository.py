import os

import pytest

from crud.repository import (
    create_car,
    delete_car,
    find_car,
    find_cars_by_field,
    is_valid_combination,
    list_cars,
    next_id,
    update_car,
)


@pytest.fixture
def data_path(tmp_path):
    return os.path.join(tmp_path, "cars.json")


def test_is_valid_combination_rejects_sedan_continental():
    valid, reason = is_valid_combination(1, 1, 2, 1)
    assert valid is False
    assert reason == "Sedan에는 Continental제동장치 사용 불가"


def test_is_valid_combination_rejects_suv_toyota():
    valid, reason = is_valid_combination(2, 2, 1, 1)
    assert valid is False
    assert reason == "SUV에는 TOYOTA엔진 사용 불가"


def test_is_valid_combination_rejects_truck_wia():
    valid, reason = is_valid_combination(3, 3, 3, 1)
    assert valid is False
    assert reason == "Truck에는 WIA엔진 사용 불가"


def test_is_valid_combination_rejects_truck_mando():
    valid, reason = is_valid_combination(3, 1, 1, 1)
    assert valid is False
    assert reason == "Truck에는 Mando제동장치 사용 불가"


def test_is_valid_combination_rejects_bosch_brake_non_bosch_steering():
    valid, reason = is_valid_combination(2, 1, 3, 2)
    assert valid is False
    assert reason == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


def test_is_valid_combination_accepts_valid_combo():
    valid, reason = is_valid_combination(1, 1, 1, 1)
    assert valid is True
    assert reason is None


def test_next_id_empty_list():
    assert next_id([]) == 1


def test_next_id_increments_from_max():
    cars = [{"id": 1}, {"id": 3}, {"id": 2}]
    assert next_id(cars) == 4


def test_create_car_assigns_incrementing_id(data_path):
    first, err1 = create_car(1, 1, 1, 1, path=data_path)
    second, err2 = create_car(2, 1, 3, 1, path=data_path)

    assert err1 is None
    assert err2 is None
    assert first["id"] == 1
    assert second["id"] == 2


def test_create_car_rejects_invalid_combination(data_path):
    car, err = create_car(1, 1, 2, 1, path=data_path)

    assert car is None
    assert err == "Sedan에는 Continental제동장치 사용 불가"
    assert list_cars(path=data_path) == []


def test_list_cars_sorted_by_key(data_path):
    create_car(3, 1, 2, 1, path=data_path)
    create_car(1, 1, 1, 1, path=data_path)
    create_car(2, 1, 1, 1, path=data_path)

    result = list_cars(sort_key="car_type", path=data_path)

    assert [car["car_type"] for car in result] == [1, 2, 3]


def test_find_car_existing_and_missing(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    assert find_car(created["id"], path=data_path) == created
    assert find_car(999, path=data_path) is None


def test_update_car_modifies_field(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    updated, err = update_car(created["id"], "brake_code", 3, path=data_path)

    assert err is None
    assert updated["brake_code"] == 3
    assert find_car(created["id"], path=data_path)["brake_code"] == 3


def test_update_car_missing_id(data_path):
    updated, err = update_car(999, "brake_code", 3, path=data_path)

    assert updated is None
    assert err == "해당 ID 없음"


def test_update_car_rejects_invalid_combination(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    updated, err = update_car(created["id"], "brake_code", 2, path=data_path)

    assert updated is None
    assert err == "Sedan에는 Continental제동장치 사용 불가"
    assert find_car(created["id"], path=data_path)["brake_code"] == 1


def test_delete_car_existing_and_missing(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    assert delete_car(created["id"], path=data_path) is True
    assert find_car(created["id"], path=data_path) is None
    assert delete_car(created["id"], path=data_path) is False


def test_find_cars_by_field_matches_found(data_path):
    created, _ = create_car(1, 1, 1, 1, path=data_path)

    result = find_cars_by_field("engine_code", 1, path=data_path)

    assert result == [created]


def test_find_cars_by_field_no_matches(data_path):
    create_car(1, 1, 1, 1, path=data_path)

    result = find_cars_by_field("engine_code", 3, path=data_path)

    assert result == []


def test_find_cars_by_field_multiple_matches(data_path):
    first, _ = create_car(1, 1, 1, 1, path=data_path)
    second, _ = create_car(2, 1, 1, 1, path=data_path)
    create_car(3, 3, 3, 1, path=data_path)

    result = find_cars_by_field("engine_code", 1, path=data_path)

    assert result == [first, second]
