from abc import ABCMeta
from typing import override


class PrettyRepr(type):
    @override
    def __repr__(self) -> str:
        return f"vdata.{self.__name__}"


class PrettyReprABC(ABCMeta):
    @override
    def __repr__(self) -> str:
        return f"vdata.{self.__name__}"
