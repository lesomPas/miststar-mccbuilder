from internal.exceptions import CommandException
from exceptions import MiststarException


def test_command_exception_inherits_miststar_exception() -> None:
    assert issubclass(CommandException, MiststarException)
