def undecorated_function() -> None:
    print('I have no @raising decorator')
    raise ValueError('Oops')


def another_undecorated() -> None:
    pass
