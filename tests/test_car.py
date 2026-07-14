from car_assembly.car import CarBuild
from car_assembly.car_type import CarType
from car_assembly.parts import BoschBrake, BrokenEngine, ContinentalBrake, GMEngine, MandoBrake, MobisSteering, WIAEngine


def test_carbuild_holds_selections():
    build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
    assert build.car_type == CarType.SEDAN
    assert isinstance(build.engine, GMEngine)


def test_carbuild_defaults_to_none():
    assert CarBuild().car_type is None


def test_is_engine_broken_true():
    build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
    assert build.is_engine_broken() is True


def test_is_engine_broken_false():
    build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
    assert build.is_engine_broken() is False


def test_first_incompatibility_engine_checked_before_brake():
    build = CarBuild(CarType.TRUCK, WIAEngine(), MandoBrake(), MobisSteering())
    assert build.first_incompatibility() == "Truck에는 WIA엔진 사용 불가"


def test_first_incompatibility_brake_car_type_rule():
    build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
    assert build.first_incompatibility() == "Sedan에는 Continental제동장치 사용 불가"


def test_first_incompatibility_brake_steering_rule():
    build = CarBuild(CarType.SEDAN, GMEngine(), BoschBrake(), MobisSteering())
    assert build.first_incompatibility() == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


def test_is_compatible_true_for_valid_build():
    build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
    assert build.is_compatible() is True


def test_is_compatible_false_for_invalid_build():
    build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
    assert build.is_compatible() is False


def test_run_report_incompatible():
    build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
    assert build.run_report() == ["자동차가 동작되지 않습니다"]


def test_run_report_broken_engine():
    build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
    assert build.run_report() == ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]


def test_run_report_success():
    build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
    assert build.run_report() == [
        "Car Type : Sedan",
        "Engine   : GM",
        "Brake    : Mando",
        "Steering : Mobis",
        "자동차가 동작됩니다.",
    ]


def test_test_report_fail():
    build = CarBuild(CarType.SEDAN, GMEngine(), ContinentalBrake(), MobisSteering())
    assert build.test_report() == "FAIL\nSedan에는 Continental제동장치 사용 불가"


def test_test_report_pass():
    build = CarBuild(CarType.SEDAN, GMEngine(), MandoBrake(), MobisSteering())
    assert build.test_report() == "PASS"


def test_test_report_pass_even_with_broken_engine():
    build = CarBuild(CarType.SEDAN, BrokenEngine(), MandoBrake(), MobisSteering())
    assert build.test_report() == "PASS"
