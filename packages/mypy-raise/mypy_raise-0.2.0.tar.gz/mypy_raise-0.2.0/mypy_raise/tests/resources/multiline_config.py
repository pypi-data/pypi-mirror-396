import third_party_lib  # type: ignore

from mypy_raise import raising


@raising(exceptions=[])
def use_multiline_config():
    # This should trigger an error because third_party_lib.process
    # will be configured to raise ValueError in multiline_mypy.ini
    third_party_lib.process()
