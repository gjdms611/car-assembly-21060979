from car_assembly.car_type import CAR_TYPE_LABEL, CarType


def test_car_type_values():
    assert CarType.SEDAN == 1
    assert CarType.SUV == 2
    assert CarType.TRUCK == 3


def test_car_type_labels():
    assert CAR_TYPE_LABEL[CarType.SEDAN] == "Sedan"
    assert CAR_TYPE_LABEL[CarType.SUV] == "SUV"
    assert CAR_TYPE_LABEL[CarType.TRUCK] == "Truck"
