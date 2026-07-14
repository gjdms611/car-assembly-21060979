def advance_step(step: int, ans: int) -> int:
    if ans == 0:
        if step == 4:
            return 0
        if step > 0:
            return step - 1
        return step
    if step in (0, 1, 2, 3):
        return step + 1
    return step
