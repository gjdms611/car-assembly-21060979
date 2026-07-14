from car_assembly.cli import advance_step


def test_back_navigation_from_step4_goes_to_0():
    assert advance_step(4, 0) == 0


def test_back_navigation_decrements_step():
    assert advance_step(2, 0) == 1
    assert advance_step(1, 0) == 0


def test_back_navigation_at_step0_stays():
    assert advance_step(0, 0) == 0


def test_forward_navigation_increments_step():
    assert advance_step(0, 1) == 1
    assert advance_step(1, 2) == 2
    assert advance_step(2, 3) == 3
    assert advance_step(3, 1) == 4


def test_step4_non_zero_answer_stays_on_step4():
    assert advance_step(4, 1) == 4
    assert advance_step(4, 2) == 4
