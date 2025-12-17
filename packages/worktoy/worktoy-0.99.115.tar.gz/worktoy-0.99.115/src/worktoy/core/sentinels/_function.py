"""
Function is a special metaclass intended to represent objects that are
functions, builtin functions, or functions defined in class bodies,
but retrieved through instances or through the class itself.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...waitaminute.meta import IllegalInstantiation

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Never


class _Root:
  pass


class _MetaFunction(type):
  """
  Function is a special metaclass intended to represent objects that are
  functions, builtin functions, or functions defined in class bodies,
  but retrieved through instances or through the class itself.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __func_types__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _createFunctionTypes(mcls, ) -> None:
    """
    Creates and caches the list of types that are considered function
    types.
    """

    def foo() -> None:
      """If you just put 'pass', it is not considered covered lmao"""

    class Bar:
      @classmethod
      def baz(cls) -> None:
        """If you just put 'pass', it is not considered covered lmao"""

      @staticmethod
      def qux() -> None:
        """If you just put 'pass', it is not considered covered lmao"""

      def quux(self) -> None:
        """If you just put 'pass', it is not considered covered lmao"""

    mcls.__func_types__ = [
        type(lambda: None),
        type(print),
        type(foo),
        type(Bar.baz),
        type(Bar.qux),
        type(Bar.quux),
        type(Bar().baz),
        type(Bar().qux),
        type(Bar().quux),
    ]

  @classmethod
  def _getFuncTypes(mcls, **kwargs) -> list[type]:
    """
    Returns a list of the types that are considered function types.
    """
    if mcls.__func_types__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError
      mcls._createFunctionTypes()
      return mcls._getFuncTypes(_recursion=True)
    return mcls.__func_types__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instancecheck__(cls, instance: object) -> bool:
    """
    This method validates as instances functions, builtin functions,
    lambda or class body defined functions.
    """
    if not callable(instance):
      return False

    for type_ in cls._getFuncTypes():
      if isinstance(instance, type_):
        return True
    return False

  def __subclasscheck__(cls, subclass: Any) -> bool:
    """
    This method validates as subclasses any class that has at least one
    callable attribute that is a function, builtin function, lambda or
    class body defined function.
    """
    try:
      _ = issubclass(subclass, type)
    except TypeError as typeError:
      raise typeError
    funcTypes = cls._getFuncTypes()
    for type_ in funcTypes:
      if issubclass(subclass, type_):
        return True
    return False

  def __new__(mcls, name: str, bases: tuple, space: dict, **kwargs) -> Any:
    """
    Prevents instantiation of the metaclass.
    """
    if _Root in bases:
      return super().__new__(mcls, name, (), space, **kwargs)

    raise IllegalInstantiation(mcls)


class Function(_Root, metaclass=_MetaFunction, ):
  """
  Function is a special metaclass intended to represent objects that are
  functions, builtin functions, or functions defined in class bodies,
  but retrieved through instances or through the class itself.
  """
  pass
