from mypy_raise import raising


@raising(exceptions=[ValueError])
def level3():
    raise ValueError('Level 3 error')


@raising(exceptions=[ValueError])
def level2():
    level3()


@raising(exceptions=[])  # ERROR: indirectly raises ValueError through level2 -> level3
def level1():
    level2()
