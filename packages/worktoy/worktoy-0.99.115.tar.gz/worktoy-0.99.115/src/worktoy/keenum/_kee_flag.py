"""
KeeFlag provides a singular enumeration in the KeeFlags class. Like the
'KeeNum' class, it is itself an enumeration, but where the 'KeeNum' class
provides only singular members, the 'KeeFlags' populate the enumeration
with the 'NULL' enumeration, the 'FULL' enumeration and all possible
combinations of the singular members.

Where the 'Kee' class allows the novel syntactic sugar of 'Kee[int](1)',
'KeeFlag' requires the owning 'KeeFlags' class to specify the type of the
'value' of each member. While duplicate 'name' attributes between members
are disallowed, duplicate 'value' attributes are allowed. Please note
however that when retrieving members by value, the member having the
lowest index is used.

Attributes (becomes attributes of the instances of the owning 'KeeFlags'
class):
- name: The name of the member. It is this name that is passed to the
'__set_name__' method during class creation.
- value: The value of the member. See note about value instantiation.
- 'index': The number of previously defined members when this member was
being defined (received '__set_name__' call). By default, 'KeeFlags'
auto-generates a member named 'NULL' with index 0.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..desc import Field
from ..utilities import textFmt, maybe
from ..waitaminute import MissingVariable, TypeException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Tuple, Self, Iterator
  from ..keenum import KeeFlagsMeta


class KeeFlag:
  """
  KeeFlag provides a singular enumeration in the KeeFlags class. Like the
  'KeeNum' class, it is itself an enumeration, but where the 'KeeNum' class
  provides only singular members, the 'KeeFlags' populate the enumeration
  with the 'NULL' enumeration, the 'FULL' enumeration and all possible
  combinations of the singular members.

  Please note that the actual instances of this class are *not* the
  members of the enumeration. 'KeeFlags' manages a container of these.
  Then the members are created as wrappers on these instances.

  Where the 'Kee' class allows the novel syntactic sugar of 'Kee[int](1)',
  'KeeFlag' requires the owning 'KeeFlags' class to specify the type of the
  'value' of each member. While duplicate 'name' attributes between members
  are disallowed, duplicate 'value' attributes are allowed. Please note
  however that when retrieving members by value, the member having the
  lowest index is used.

  Attributes (becomes attributes of the instances of the owning 'KeeFlags'
  class):
  - name: The name of the member. It is this name that is passed to the
    '__set_name__' method during class creation.
  - value: The value of the member. See note about value instantiation.
  - 'index': The number of previously defined members when this member was
    being defined (received '__set_name__' call). By default, 'KeeFlags'
    auto-generates a member named 'NULL' with index 0. Please note that
    this value gets assigned by the metaclass machinery *before* the
    KeeFlags class is created.
  - 'args': Positional arguments passed to the constructor.
  - 'kwargs': Keyword arguments passed to the constructor.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Type hints for the benefit of linters
  value: Any
  lows: tuple
  highs: tuple
  names: tuple[str, ...]

  #  Class Variables

  #  Fallback Variables

  #  Private Variables
  __field_name__ = None
  __field_owner__ = None
  __member_index__ = None
  __member_name__ = None
  __pos_args__ = None
  __key_args__ = None

  #  Public Variables
  fieldName = Field()
  fieldOwner = Field()
  index = Field()
  name = Field()
  args = Field()
  kwargs = Field()

  #  Virtual Variables
  valueType = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @fieldName.GET
  def _getFieldName(self, ) -> str:
    if self.__field_name__ is None:
      raise MissingVariable(self, '__field_name__', str)
    if isinstance(self.__field_name__, str):
      return self.__field_name__
    raise TypeException('__field_name__', self.__field_name__, str)

  @fieldOwner.GET
  def _getFieldOwner(self, ) -> type:
    if self.__field_owner__ is None:
      from . import KeeFlagsMeta
      raise MissingVariable(self, '__field_owner__', KeeFlagsMeta)
    if isinstance(self.__field_owner__, type):
      return self.__field_owner__
    name, value = '__field_owner__', self.__field_owner__
    from . import KeeFlagsMeta
    raise TypeException(name, value, KeeFlagsMeta)

  @index.GET
  def _getIndex(self, ) -> int:
    if self.__member_index__ is None:
      raise MissingVariable(self, '__member_index__', int)
    if isinstance(self.__member_index__, int):
      return self.__member_index__
    raise TypeException('__member_index__', self.__member_index__, int)

  @name.GET
  def _getName(self, ) -> str:
    if self.__member_name__ is None:
      raise MissingVariable(self, '__member_name__', str)
    if isinstance(self.__member_name__, str):
      return self.__member_name__
    raise TypeException('__member_name__', self.__member_name__, str)

  @args.GET
  def _getArgs(self, ) -> Tuple[Any, ...]:
    return maybe(self.__pos_args__, ())

  @kwargs.GET
  def _getKwargs(self, ) -> dict[str, Any]:
    return maybe(self.__key_args__, {})

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __set_name__(self, owner: KeeFlagsMeta, name: str) -> None:
    self.__field_owner__ = owner
    self.__field_name__ = name

  def __str__(self, ) -> str:
    if self.__field_owner__ is None:
      return object.__str__(self)
    infoSpec = """%s.%s  [%d]"""
    clsName = self.fieldOwner.__name__
    return textFmt(infoSpec % (clsName, self.name, self.index))

  def __repr__(self, ) -> str:
    if self.__field_owner__ is None:
      return object.__repr__(self)
    infoSpec = """%s.%s [%d]: %s(%s)"""
    ownerName = self.fieldOwner.__name__
    fieldName = self.fieldName
    index = self.index
    clsName = type(self).__name__
    argStr = ', '.join(repr(a) for a in self.args)
    kwSpec = """%s=%s"""
    kwStr = ', '.join(kwSpec % (k, repr(v)) for k, v in self.kwargs.items())
    allArgs = []
    if argStr:
      allArgs.append(argStr)
    if kwStr:
      allArgs.append(kwStr)
    allArgStr = ', '.join(allArgs)
    info = infoSpec % (ownerName, fieldName, index, clsName, allArgStr)
    return textFmt(info)

  def __int__(self, ) -> int:
    return self._getIndex()

  def __iter__(self, ) -> Iterator[Self]:
    raise TypeError('KeeFlag is not iterable!')

  def __eq__(self, other: Self, **kwargs) -> bool:
    cls = type(self)
    selfOwner = self.__field_owner__
    otherOwner = other.__field_owner__
    if selfOwner != otherOwner:
      return NotImplemented
    return True if self.index == other.index else False

  def __hash__(self, ) -> int:
    return hash((self.__field_owner__, self.__field_name__, self.index))

  __index__ = _getIndex

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, *args: Any, **kwargs: Any) -> None:
    self.__pos_args__ = args
    self.__key_args__ = kwargs

  def clone(self, owner: type, index: int = None) -> Self:
    """Creates a clone of this KeeFlag for the specified owner."""
    cls = type(self)
    cloned = cls(*self.args, **self.kwargs)
    cloned.__field_owner__ = owner
    cloned.__field_name__ = self.__field_name__
    cloned.__member_index__ = maybe(index, self.__member_index__)
    cloned.__member_name__ = self.__member_name__
    return cloned

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
