"""crud/repository.is_valid_combination duplicates the compatibility rules
already expressed via car_assembly.parts / car_assembly.car.CarBuild. These
two independent rule implementations must stay in sync - this test is the
regression net that catches drift between them.
"""

from car_assembly.car import CarBuild
from car_assembly.car_type import CarType
from car_assembly.parts import BRAKE_BY_CODE, ENGINE_BY_CODE, STEERING_BY_CODE
from crud.repository import is_valid_combination


def test_is_valid_combination_matches_car_assembly_for_all_combinations():
    mismatches = []

    for car_type in (CarType.SEDAN, CarType.SUV, CarType.TRUCK):
        for engine_code, engine_cls in ENGINE_BY_CODE.items():
            for brake_code, brake_cls in BRAKE_BY_CODE.items():
                for steering_code, steering_cls in STEERING_BY_CODE.items():
                    build = CarBuild(
                        car_type=car_type,
                        engine=engine_cls(),
                        brake=brake_cls(),
                        steering=steering_cls(),
                    )
                    expected = build.is_compatible()

                    actual, _ = is_valid_combination(
                        car_type.value, engine_code, brake_code, steering_code
                    )

                    if actual != expected:
                        mismatches.append(
                            (car_type, engine_code, brake_code, steering_code, expected, actual)
                        )

    assert mismatches == []
