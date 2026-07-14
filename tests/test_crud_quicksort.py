from crud.quicksort import quicksort


def test_empty_list():
    assert quicksort([], "id") == []


def test_single_item():
    items = [{"id": 1}]
    assert quicksort(items, "id") == [{"id": 1}]


def test_sorts_ascending_by_key():
    items = [{"id": 3}, {"id": 1}, {"id": 2}]
    assert quicksort(items, "id") == [{"id": 1}, {"id": 2}, {"id": 3}]


def test_sorts_by_different_key():
    items = [
        {"id": 1, "car_type": 3},
        {"id": 2, "car_type": 1},
        {"id": 3, "car_type": 2},
    ]
    result = quicksort(items, "car_type")
    assert [item["id"] for item in result] == [2, 3, 1]


def test_handles_duplicate_keys():
    items = [{"id": 1}, {"id": 2}, {"id": 1}]
    result = quicksort(items, "id")
    assert [item["id"] for item in result] == [1, 1, 2]


def test_does_not_mutate_original_list():
    items = [{"id": 2}, {"id": 1}]
    quicksort(items, "id")
    assert items == [{"id": 2}, {"id": 1}]
