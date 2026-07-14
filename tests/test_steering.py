from car_assembly.steering import STEERING_BY_CODE


def test_steering_codes():
    assert STEERING_BY_CODE[1] == "BOSCH"
    assert STEERING_BY_CODE[2] == "MOBIS"
