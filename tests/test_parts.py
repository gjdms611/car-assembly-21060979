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


from car_assembly.parts import GMEngine


def test_gm_engine_label_and_message():
    engine = GMEngine()
    assert engine.selection_message() == "GM 엔진을 선택하셨습니다."
    assert engine.run_label() == "GM"
    assert engine.is_broken is False


def test_gm_engine_compatible_with_every_car_type():
    engine = GMEngine()
    assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
    assert engine.incompatibility_with_car_type(CarType.SUV) is None
    assert engine.incompatibility_with_car_type(CarType.TRUCK) is None


from car_assembly.parts import ToyotaEngine


def test_toyota_engine_incompatible_with_suv():
    engine = ToyotaEngine()
    assert engine.incompatibility_with_car_type(CarType.SUV) == "SUV에는 TOYOTA엔진 사용 불가"
    assert engine.incompatibility_with_car_type(CarType.SEDAN) is None
    assert engine.selection_message() == "TOYOTA 엔진을 선택하셨습니다."


from car_assembly.parts import WIAEngine


def test_wia_engine_incompatible_with_truck():
    engine = WIAEngine()
    assert engine.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 WIA엔진 사용 불가"
    assert engine.selection_message() == "WIA 엔진을 선택하셨습니다."


from car_assembly.parts import BrokenEngine


def test_broken_engine_is_broken_and_has_no_run_label():
    engine = BrokenEngine()
    assert engine.is_broken is True
    assert engine.run_label() is None
    assert engine.selection_message() == "고장난 엔진을 선택하셨습니다."
    assert engine.incompatibility_with_car_type(CarType.SEDAN) is None


from car_assembly.parts import ENGINE_BY_CODE, BrokenEngine, GMEngine, ToyotaEngine, WIAEngine


def test_engine_by_code_maps_input_number_to_class():
    assert ENGINE_BY_CODE[1] is GMEngine
    assert ENGINE_BY_CODE[2] is ToyotaEngine
    assert ENGINE_BY_CODE[3] is WIAEngine
    assert ENGINE_BY_CODE[4] is BrokenEngine


from car_assembly.parts import MandoBrake


def test_mando_brake_incompatible_with_truck():
    brake = MandoBrake()
    assert brake.incompatibility_with_car_type(CarType.TRUCK) == "Truck에는 Mando제동장치 사용 불가"
    assert brake.incompatibility_with_car_type(CarType.SEDAN) is None
    assert brake.selection_message() == "MANDO 제동장치를 선택하셨습니다."
    assert brake.run_label() == "Mando"


from car_assembly.parts import ContinentalBrake


def test_continental_brake_incompatible_with_sedan():
    brake = ContinentalBrake()
    assert brake.incompatibility_with_car_type(CarType.SEDAN) == "Sedan에는 Continental제동장치 사용 불가"
    assert brake.selection_message() == "CONTINENTAL 제동장치를 선택하셨습니다."
    assert brake.run_label() == "Continental"
