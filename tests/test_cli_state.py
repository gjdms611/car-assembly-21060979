from car_assembly.cli import advance_step


def test_back_navigation_from_step4_goes_to_0():
    assert advance_step(4, 0) == 0
