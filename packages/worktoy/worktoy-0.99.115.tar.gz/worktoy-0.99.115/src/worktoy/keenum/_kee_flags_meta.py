"""KeeFlagsMeta provides the metaclass for KeeFlags."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..desc import Field
from ..mcls import BaseMeta
from ..utilities import textFmt, maybe

from . import KeeFlag
from . import KeeFlagsSpace as KFSpace

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Self, Any, Iterator

  Bases: TypeAlias = tuple[type, ...]

  from . import KeeFlags


class KeeFlagsMeta(BaseMeta):
  """
  KeeFlagsMeta is the metaclass for KeeFlags, providing additional
  functionality for handling flags.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __kee_class__ = None
  __kee_bases__ = None

  #  Private Variables
  __kee_flags__ = None
  __kee_members__ = None
  __allow_instantiation__ = None

  #  Public Variables
  flags = Field()
  memberList = Field()
  memberDict = Field()
  valueType = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @flags.GET
  def _getFlags(cls) -> list[KeeFlag]:
    return [flag for flag in cls.getKeeFlags().values()]

  @valueType.GET
  def _getValueType(cls) -> type:
    nullMember = cls.NULL
    return type(nullMember.value)

  @memberList.GET
  def _getMemberList(cls) -> list[KeeFlags]:
    return cls.__member_list__

  @memberDict.GET
  def _getMemberDict(cls) -> dict[str, KeeFlags]:
    return cls.__member_dict__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __subclasscheck__(cls, other: type, **kwargs) -> bool:
    if cls is other:
      return True
    if other is type(cls).__kee_class__:
      return False
    if not isinstance(other, type):
      raise TypeError('issubclass() arg 1 must be a class')
    otherKeeBases = getattr(other, '__kee_bases__', None)
    if otherKeeBases is None:
      return False
    out = None
    for base in otherKeeBases:
      if base is cls or cls.__subclasscheck__(base):
        return True
    return False

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kw) -> KFSpace:
    """Replaces the KeeSpace with KeeFlagsSpace"""
    bases = (*[b for b in bases if b.__name__ != '_InitSub'],)
    return KFSpace(mcls, name, bases, **kw)

  def __new__(mcls, name: str, bases: Bases, space: KFSpace, **kw) -> Self:
    """
    Creates a new instance of the class.
    This method is called when the class is created.
    """
    cls = BaseMeta.__new__(mcls, name, bases, space, **kw)
    if name == 'KeeFlags':
      setattr(cls, '__kee_bases__', bases)
      setattr(mcls, '__kee_class__', cls)
      return cls
    setattr(cls, '__kee_bases__', bases)
    cls.__allow_instantiation__ = True
    for flag in cls.flags:
      flag.__set_name__(cls, flag.name)
    memberList = []
    memberDict = dict()
    n = 2 ** len(cls.flags)
    for i in range(n):
      member = cls(i, )
      setattr(member, '__field_owner__', cls)
      setattr(member, '__field_name__', member.name)
      setattr(cls, member.name, member)
      memberList.append(member)
      memberDict[member.names] = member
    cls.__member_list__ = memberList
    cls.__member_dict__ = memberDict
    cls.__allow_instantiation__ = False
    customMRO = [cls, *bases, *cls.__mro__[1:]]
    valueGetter = None
    valueGetters = []
    for obj in customMRO:
      valueGetter = maybe(obj.__dict__.get('_getValue'), valueGetter)
      if valueGetter is None:
        continue
      if obj is mcls.__kee_class__:
        continue
      if valueGetter is getattr(mcls.__kee_class__, '_getValue'):
        continue
      valueGetters.append(valueGetter)
    valueGetters.append(getattr(mcls.__kee_class__, '_getValue'))
    setattr(cls, '_getValue', valueGetters[0])
    return cls

  def __call__(cls, *args, **kwargs) -> Any:
    if getattr(cls, '__allow_instantiation__', False):
      return BaseMeta.__call__(cls, *args, **kwargs)
    return cls._resolveMember(*args, **kwargs)

  def __len__(cls) -> int:
    return len(cls.memberList)

  def __iter__(cls, ) -> Iterator[KeeFlags]:
    yield from cls.memberList

  def __contains__(cls, identifier: Any) -> bool:
    try:
      _ = cls._resolveMember(identifier)
    except (IndexError, KeyError, ValueError, TypeError):
      return False
    else:
      return True

  def __getitem__(cls, identifier: Any) -> KeeFlags:
    return cls._resolveMember(identifier)

  def __eq__(cls, other: Any) -> bool:
    try:
      otherHash = hash(other)
    except TypeError as typeError:
      if 'hashable type' in str(typeError):
        return NotImplemented
      raise typeError
    else:
      return NotImplemented if otherHash == hash(cls) else False

  def __hash__(cls, ) -> int:
    return hash((cls.__name__, cls.__module__,))

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _resolveIndex(cls, index: int) -> KeeFlags:
    for member in cls:
      if member.index == index:
        return member
    infoSpec = """KeeFlags class '%s' has no member at index: '%d'!"""
    info = infoSpec % (cls.__name__, index,)
    raise IndexError(textFmt(info))

  def _resolveName(cls, name: str) -> KeeFlags:
    identifier = frozenset(name.upper().split('_'))
    for member in cls:
      if member.name == name or member.names == identifier:
        return member
    infoSpec = """KeeFlags class '%s' has no member with name: '%s'!"""
    info = infoSpec % (cls.__name__, name,)
    raise KeyError(textFmt(info))

  def _resolveNames(cls, *names: str) -> KeeFlags:
    return cls.memberDict[frozenset(names)]

  def _resolveValue(cls, value: Any) -> KeeFlags:
    for member in cls:
      if member.value == value:
        return member
    infoSpec = """KeeFlags class '%s' has no member with value: '%s'!"""
    info = infoSpec % (cls.__name__, value,)
    raise ValueError(textFmt(info))

  def _resolveMember(cls, *identifier: Any, **kwargs) -> KeeFlags:
    if not identifier:
      return cls(0, )
    if len(identifier) > 1:
      return cls._resolveNames(*identifier)
    identifier = identifier[0]
    if isinstance(identifier, (tuple, list, frozenset, set)):
      return cls._resolveNames(*identifier)
    if isinstance(identifier, int):
      return cls._resolveIndex(identifier)
    if isinstance(identifier, str):
      return cls._resolveName(identifier)
    return cls._resolveValue(identifier)
