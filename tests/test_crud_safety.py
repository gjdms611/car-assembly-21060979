import os

import pytest

from crud.repository import create_car, delete_car, find_cars_by_field, list_cars
from crud.storage import load_cars


@pytest.fixture
def data_path(tmp_path):
    return os.path.join(tmp_path, "cars.json")


def test_load_cars_corrupt_json_raises(tmp_path):
    path = os.path.join(tmp_path, "cars.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("{not valid json")

    with pytest.raises(Exception):
        load_cars(path)


def test_create_car_reuses_id_after_deleting_max_id(data_path):
    """next_id() derives from max(existing ids) + 1, so deleting the
    highest-id car frees that id for immediate reuse. This is current
    behavior, not necessarily desirable - locked in so a future change
    to id assignment is a deliberate decision, not an accident.
    """
    first, _ = create_car(1, 1, 1, 1, path=data_path)
    second, _ = create_car(2, 1, 1, 1, path=data_path)

    delete_car(second["id"], path=data_path)
    third, _ = create_car(1, 1, 1, 1, path=data_path)

    assert third["id"] == second["id"]
    assert [car["id"] for car in list_cars(path=data_path)] == [first["id"], third["id"]]


def test_create_car_does_not_reuse_id_after_deleting_non_max_id(data_path):
    first, _ = create_car(1, 1, 1, 1, path=data_path)
    second, _ = create_car(2, 1, 1, 1, path=data_path)

    delete_car(first["id"], path=data_path)
    third, _ = create_car(1, 1, 1, 1, path=data_path)

    assert third["id"] != first["id"]
    assert [car["id"] for car in list_cars(path=data_path)] == [second["id"], third["id"]]


def test_create_car_rejected_combination_does_not_change_file(data_path):
    create_car(1, 1, 1, 1, path=data_path)
    before = load_cars(data_path)

    car, err = create_car(1, 1, 2, 1, path=data_path)

    assert car is None
    assert err is not None
    assert load_cars(data_path) == before


def test_delete_car_missing_id_does_not_change_file(data_path):
    create_car(1, 1, 1, 1, path=data_path)
    before = load_cars(data_path)

    result = delete_car(999, path=data_path)

    assert result is False
    assert load_cars(data_path) == before


def test_find_cars_by_field_unknown_field_raises_key_error(data_path):
    create_car(1, 1, 1, 1, path=data_path)

    with pytest.raises(KeyError):
        find_cars_by_field("not_a_real_field", 1, path=data_path)
