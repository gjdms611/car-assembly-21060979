from car_assembly.parts import Part


class _DummyPart(Part):
    label = "Dummy"
    unit_label = "테스트를"


def test_part_selection_message_uppercases_label():
    assert _DummyPart().selection_message() == "DUMMY 테스트를 선택하셨습니다."


def test_part_run_label_defaults_to_label():
    assert _DummyPart().run_label() == "Dummy"
