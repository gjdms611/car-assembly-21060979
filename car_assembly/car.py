from dataclasses import dataclass
from typing import Optional

from car_assembly.car_type import CAR_TYPE_LABEL, CarType
from car_assembly.parts import BrakePart, EnginePart, SteeringPart


@dataclass
class CarBuild:
    car_type: Optional[CarType] = None
    engine: Optional[EnginePart] = None
    brake: Optional[BrakePart] = None
    steering: Optional[SteeringPart] = None

    def is_engine_broken(self) -> bool:
        return self.engine is not None and self.engine.is_broken

    def first_incompatibility(self) -> Optional[str]:
        return (
            self.engine.incompatibility_with_car_type(self.car_type)
            or self.brake.incompatibility_with_car_type(self.car_type)
            or self.brake.incompatibility_with_steering(self.steering)
        )

    def is_compatible(self) -> bool:
        return self.first_incompatibility() is None

    def run_report(self) -> list[str]:
        if not self.is_compatible():
            return ["자동차가 동작되지 않습니다"]
        if self.is_engine_broken():
            return ["엔진이 고장나있습니다.", "자동차가 움직이지 않습니다."]

        lines = [f"Car Type : {CAR_TYPE_LABEL[self.car_type]}"]
        engine_label = self.engine.run_label()
        if engine_label is not None:
            lines.append(f"Engine   : {engine_label}")
        lines.append(f"Brake    : {self.brake.run_label()}")
        lines.append(f"Steering : {self.steering.run_label()}")
        lines.append("자동차가 동작됩니다.")
        return lines

    def test_report(self) -> str:
        message = self.first_incompatibility()
        if message is None:
            return "PASS"
        return f"FAIL\n{message}"
