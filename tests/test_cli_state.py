from car_assembly.cli import advance_step


def test_back_navigation_from_step4_goes_to_0():
    assert advance_step(4, 0) == 0


def test_back_navigation_decrements_step():
    assert advance_step(2, 0) == 1
    assert advance_step(1, 0) == 0


def test_back_navigation_at_step0_stays():
    assert advance_step(0, 0) == 0
