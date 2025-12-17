"""
KeeFlags enumerations all combinations of boolean valued flags. It
dynamically adds instances of KeeFlags for each boolean valued entry. The
result is a KeeNum-like enumeration consisting of all possible combinations
of boolean flags.

Each enumeration of the KeeFlags class is created at class creation time.
This means that the number of enumerations increase exponentially with
number of flags included. This presents no problem for the intended uses.
For example the FileAccess enumeration used in the test suite:


class FileAccess(KeeFlags):
  #  FileAccess demonstrates real-world bitmask flags for file permissions.

  #  Enumerations
  READ = Kee[int](0b0001)
  WRITE = Kee[int](0b0010)
  EXECUTE = Kee[int](0b0100)
  DELETE = Kee[int](0b1000)

  __null_value__ = 0b1111

  - The NULL Member -
While KeeNum enumerations may implement a member called 'NULL', KeeFlags
enumerations automatically has a member called 'NULL' which equals the
bitwise negation of all flags defined in the enumeration. KeeFlags
enumerations may provide a specific value '__null_value__'. If this value
is passed to the member resolution workflow, and no member equals it,
the 'fromValue' method will return the NULL member. If the
'__null_value__' does equal the value of a member, that member is returned
instead.

  - Flags and Names -
Each KeeFlags enumeration has a unique combination of flags that are HIGH.
The 'flags' and 'names' descriptors when accessed through a member returns
a list of the flags or names respectively that are HIGH for that member.

For example, 'FileAccess.READ_WRITE.flags' returns the '.READ' and
'.WRITE' single bit flags that are HIGH for the 'FileAccess.READ_WRITE'
member. The 'names' descriptor returns the names of the flags that
are HIGH for the member, such as 'READ' and 'WRITE'.

  - Flexibility -
Each enumeration of flags is generated automatically. This raises a
question of naming. Is it 'FileAccess.READ_EXECUTE' or is it
'FileAccess.EXECUTE_READ'? It follows the order of appearance in the class
body. However, while

"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..desc import Field
from ..utilities import textFmt
from ..waitaminute import MissingVariable, TypeException

from . import KeeFlag, KeeFlagsMeta

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Iterator, Self


class KeeFlags(metaclass=KeeFlagsMeta):
  """
  KeeFlags is a metaclass that dynamically creates instances of KeeFlags
  for each boolean valued entry. It allows for the creation of an
  enumeration consisting of all possible combinations of boolean flags.

  Important Attributes:
  - flags: A descriptor returning the flags of a particular enumeration
  that are HIGH.

  Entries must be integer valued.

  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables (type hints)
  __member_list__: list[Self]
  __member_dict__: dict[frozenset[str], Self]

  #  Private Variables
  __member_index__ = None
  __member_value__ = None
  __frozen_state__ = None

  #  Public Variables
  index = Field()

  #  Virtual Variables
  lows = Field()
  highs = Field()
  value = Field()
  name = Field()
  names = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @value.GET
  def _getValue(self) -> Any:
    """
    Returns the object at the 'value' attribute of the member. The base
    implementation provides for retrieving a member from the class from a
    given value. Other than this, the attribute provides no further
    functionality. Subclasses may override this method to provide any
    object from any member. While not enforced, it is recommended that
    that member values should be of the same type and that the type should
    be immutable. Subclasses are free to grant multiple members the same
    value. In this case, the 'fromValue' method returns the first member
    having the given value.

    By default, the value is the index of the member.
    """
    return self.index

  @lows.GET
  def _getLows(self) -> Iterator[KeeFlag]:
    if self.__member_index__:
      for flag in type(self).flags:
        if self.index & (1 << flag.index):
          continue
        yield flag
    else:
      yield from type(self).flags

  @highs.GET
  def _getHighs(self) -> Iterator[KeeFlag]:
    if self.__member_index__:
      for flag in type(self).flags:
        if self.index & (1 << flag.index):
          yield flag
    else:
      yield from ()

  @index.GET
  def _getIndex(self) -> int:
    if self.__member_index__ is None:
      raise MissingVariable(self, '__member_index__', int)
    if isinstance(self.__member_index__, int):
      return self.__member_index__
    raise TypeException('__member_index__', self.__member_index__, int)

  @name.GET
  def _getName(self) -> str:
    return '_'.join(f.name for f in self.highs) or 'NULL'

  @names.GET
  def _getNames(self, ) -> frozenset:
    return frozenset(f.name for f in self.highs)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __iter__(self) -> Iterator[Self]:
    yield from self.highs

  def __str__(self, ) -> str:
    infoSpec = """%s.%s [%d]"""
    clsName = type(self).__name__
    info = infoSpec % (clsName, self.name, self.index)
    return textFmt(info)

  __repr__ = __str__

  def __eq__(self, other: Any) -> bool:
    if not isinstance(type(other), KeeFlagsMeta):
      return NotImplemented
    if self.__field_owner__ == other.__field_owner__:
      return True if self.index == other.index else False
    return False

  def __hash__(self, ) -> int:
    return hash((hash(type(self)), *self.highs))

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, index: int) -> None:
    self.__member_index__ = index
