from abc import ABC
from typing import Optional


class Part(ABC):
    """모든 부품이 공유하는 선택 메시지/리포트 라벨 동작(템플릿 메서드)."""

    label: str
    unit_label: str  # 예: "엔진을", "제동장치를", "조향장치를"

    def selection_message(self) -> str:
        return f"{self.label.upper()} {self.unit_label} 선택하셨습니다."

    def run_label(self) -> Optional[str]:
        return self.label


from car_assembly.car_type import CAR_TYPE_LABEL, CarType


class CarTypeConstrained:
    """특정 차량 타입과 호환되지 않는 부품(엔진/제동장치)이 공유하는 믹스인."""

    unsupported_car_type: Optional[CarType] = None
    car_type_conflict_noun: str = ""

    def incompatibility_with_car_type(self, car_type: CarType) -> Optional[str]:
        if self.unsupported_car_type is not None and car_type == self.unsupported_car_type:
            return f"{CAR_TYPE_LABEL[car_type]}에는 {self.label}{self.car_type_conflict_noun} 사용 불가"
        return None


class EnginePart(CarTypeConstrained, Part):
    unit_label = "엔진을"
    car_type_conflict_noun = "엔진"
    is_broken: bool = False


class GMEngine(EnginePart):
    label = "GM"


class ToyotaEngine(EnginePart):
    label = "TOYOTA"
    unsupported_car_type = CarType.SUV


class WIAEngine(EnginePart):
    label = "WIA"
    unsupported_car_type = CarType.TRUCK


class BrokenEngine(EnginePart):
    label = "고장난"
    is_broken = True

    def run_label(self) -> Optional[str]:
        return None


ENGINE_BY_CODE = {1: GMEngine, 2: ToyotaEngine, 3: WIAEngine, 4: BrokenEngine}


class BrakePart(CarTypeConstrained, Part):
    unit_label = "제동장치를"
    car_type_conflict_noun = "제동장치"
    requires_bosch_steering: bool = False

    def incompatibility_with_steering(self, steering) -> Optional[str]:
        if self.requires_bosch_steering and not steering.is_bosch:
            return "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"
        return None


class MandoBrake(BrakePart):
    label = "Mando"
    unsupported_car_type = CarType.TRUCK


class ContinentalBrake(BrakePart):
    label = "Continental"
    unsupported_car_type = CarType.SEDAN


class BoschBrake(BrakePart):
    label = "Bosch"
    requires_bosch_steering = True


BRAKE_BY_CODE = {1: MandoBrake, 2: ContinentalBrake, 3: BoschBrake}


class SteeringPart(Part):
    unit_label = "조향장치를"
    is_bosch: bool = False


class BoschSteering(SteeringPart):
    label = "Bosch"
    is_bosch = True


class MobisSteering(SteeringPart):
    label = "Mobis"
