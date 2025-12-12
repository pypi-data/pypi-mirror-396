"""
This module provides classes for managing the capabilities of a Homey.
"""

from typing import LiteralString, TypeVar, type_check_only

from ..simple_class import SimpleClass

ChildEvent = TypeVar("ChildEvent", bound=LiteralString)

@type_check_only
class Manager(SimpleClass[ChildEvent]): ...
