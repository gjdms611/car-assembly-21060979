from car_assembly.parts import Part


class _DummyPart(Part):
    label = "Dummy"
    unit_label = "테스트를"


def test_part_selection_message_uppercases_label():
    assert _DummyPart().selection_message() == "DUMMY 테스트를 선택하셨습니다."


def test_part_run_label_defaults_to_label():
    assert _DummyPart().run_label() == "Dummy"


from car_assembly.car_type import CarType
from car_assembly.parts import CarTypeConstrained, Part


class _DummyConstrainedPart(CarTypeConstrained, Part):
    label = "Dummy"
    unit_label = "테스트를"
    car_type_conflict_noun = "부품"
    unsupported_car_type = CarType.TRUCK


def test_car_type_constrained_reports_conflict():
    part = _DummyConstrainedPart()
    assert part.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 Dummy부품 사용 불가"


def test_car_type_constrained_allows_other_car_types():
    part = _DummyConstrainedPart()
    assert part.incompatibility_with_car_type(CarType.SEDAN) is None
