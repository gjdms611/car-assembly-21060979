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
