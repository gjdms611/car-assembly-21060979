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
