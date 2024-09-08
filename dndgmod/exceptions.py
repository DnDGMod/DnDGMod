class DnDGModException(Exception):
    """A generic exception class for all exceptions raised by DnDGMod."""


class InvalidDnDGModZIPPackageFormatException(DnDGModException):
    """Raised when attempting to read a .zip as a DnDGMod Package but the format appears to be incorrect."""


class DnDGNotFoundException(DnDGModException, FileNotFoundError):
    """Raised when attempting to find where D&DG is installed, and it is not able be found"""


class InvalidModYamlException(DnDGModException):
    """Raised when attempting to parse a mod.yaml file but something seems incorrect."""


class InvalidCardsYamlException(DnDGModException):
    """Raised when attempting to parse a cards.yaml file but something seems incorrect."""

class InvalidTriggerYamlException(DnDGModException):
    """Raised when attempting to patch an invalid trigger."""
