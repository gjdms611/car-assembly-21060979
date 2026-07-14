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
