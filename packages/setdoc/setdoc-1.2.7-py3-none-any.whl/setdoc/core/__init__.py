import dataclasses
import enum
import functools
import tomllib
from importlib import resources
from typing import *

__all__ = ["SetDoc", "setdoc", "basic", "getbasicdoc"]


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str = resources.read_text("setdoc.core", "cfg.toml")
        ans: dict = tomllib.loads(text)
        return ans


@dataclasses.dataclass
class SetDoc:
    "This class helps to set doc strings."

    doc: Any

    def __call__(self: Self, target: Any) -> Any:
        "This magic method implements calling the current instance. It sets the doc string of the passed target to the value stored in the doc field of the setdoc object."
        target.__doc__ = self.doc
        return target


setdoc = SetDoc  # legacy


def basic(value: Any) -> Any:
    "This decorator sets the docstring of the given value to what is suggested by its name."
    value.__doc__ = getbasicdoc(value.__name__)
    return value


def getbasicdoc(name: str) -> str:
    "This function returns the basic docstring for a given name."
    return Util.util.data["basic"][name]
