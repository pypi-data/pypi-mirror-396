from typing import override

from vdata.IO import logger


class VBaseError(BaseException):
    """
    Base class for custom error. Error messages are redirected to the logger instead of being printed directly.
    """

    def __init__(self, msg: str = ""):
        super().__init__(msg)
        self.msg: str = msg

    @override
    def __str__(self) -> str:
        logger.generalLogger.error(self.msg)
        return self.msg


class ShapeError(VBaseError):
    """
    Custom error for errors in variable shapes.
    """


class IncoherenceError(VBaseError):
    """
    Custom error for incoherent data formats.
    """


class VLockError(VBaseError):
    """
    Custom error for tdf lock errors.
    """


class VReadOnlyError(VBaseError):
    """
    Custom error for modifications on read only data.
    """

    def __init__(self, msg: str = ""):
        super().__init__(msg="Read-only file !")


class InvalidVDataFileError(VBaseError):
    """
    File or directory is not valid as a VData storage
    """

    msg: str = "File or directory is not a valid VData"
