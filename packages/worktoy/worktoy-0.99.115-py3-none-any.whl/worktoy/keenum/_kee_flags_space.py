"""
KeeFlagsSpace subclasses KeeSpace from the worktoy.keenum package
providing the namespace object required for KeeFlags.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls import BaseSpace, AbstractNamespace
from ..utilities import maybe
from ..waitaminute.keenum import KeeDuplicate

from . import KeeFlag, KeeFlagsHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import Self, Type, TypeAlias, Callable, Self

  from . import KeeFlags
  from . import KeeFlagsMeta

  KFMType: TypeAlias = Type[KeeFlagsMeta]
  Bases: TypeAlias = tuple[Type, ...]
  GetKeeFlags: TypeAlias = Callable[[Self], dict[str, KeeFlag]]


class KeeFlagsSpace(BaseSpace):
  """
  KeeFlagsSpace subclasses KeeSpace from the worktoy.keenum package
  providing the namespace object required for KeeFlags.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __kee_flags__ = None
  __base_flags__ = None

  #  Space Hooks
  keeFlagsHook = KeeFlagsHook()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _getBaseFlags(self, ) -> dict[str, KeeFlag]:
    return maybe(self.__base_flags__, dict())

  def getKeeFlags(self, ) -> dict[str, KeeFlag]:
    baseFlags = self._getBaseFlags()
    keeFlags = maybe(self.__kee_flags__, dict())
    for name, keeFlag in keeFlags.items():
      baseFlags[name] = keeFlag
    return baseFlags

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addBaseFlag(self, name: str, keeFlag: KeeFlag, **kwargs) -> None:
    """Adds a """
    existing = self._getBaseFlags()
    existing[name] = keeFlag
    self.__base_flags__ = existing

  def addKeeFlag(self, name: str, keeFlag: KeeFlag, **kwargs) -> None:
    baseFlags = self._getBaseFlags()
    keeFlags = self.getKeeFlags()
    if name in maybe(self.__kee_flags__, dict()):
      raise KeeDuplicate(name, keeFlag)
    keeFlag.__member_index__ = len(baseFlags) + len(keeFlags)
    keeFlag.__member_name__ = name
    keeFlag.__field_name__ = name
    keeFlags[name] = keeFlag
    self.__kee_flags__ = keeFlags

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, mcls: KFMType, name: str, bases: Bases, **kw) -> None:
    if name == 'KeeFlags':
      BaseSpace.__init__(self, mcls, name, bases, **kw)
    else:
      AbstractNamespace.__init__(
        self,
        mcls,
        name,
        bases,
        _strictMRO=False,
        **kw
      )
      self.__kee_flags__ = None
      cls = type(self)
      for base in bases:
        baseSpace = getattr(base, '__namespace__', None)
        for name, keeFlag in baseSpace.getKeeFlags().items():
          self.addBaseFlag(name, keeFlag)
      for space in self.getMRONamespaces():
        for name, sigFunc in getattr(space, '__overload_map__', ).items():
          self.__overload_map__[name] = dict()
          for sig, func in sigFunc.items():
            self.__overload_map__[name][sig] = func
        for name, func in getattr(space, '__fallback_map__', ).items():
          existing = maybe(self.__fallback_map__, dict())
          existing[name] = func
          self.__fallback_map__ = existing
        for name, func in getattr(space, '__finalizer_map__', ).items():
          existing = maybe(self.__finalizer_map__, dict())
          existing[name] = func
          self.__finalizer_map__ = existing

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _getKeeFlagsFactory(cls, ) -> GetKeeFlags:
    """
    Factory function creating the getter function for the dictionary of
    the 'KeeFlag' objects forming the basis of the 'KeeFlags' class.
    """

    def func(cls_: Type[KeeFlags]) -> dict[str, KeeFlag]:
      out = dict()
      for i, (name, flag) in enumerate(cls_.__kee_flags__.items()):
        out[name] = flag.clone(cls_, i)
      return out

    setattr(func, '__name__', 'getKeeFlags')
    docSpec = """Getter function for the flags dictionary."""
    setattr(func, '__doc__', docSpec)
    return func

  def postCompile(self, namespace: dict) -> dict:
    """
    Post compile is called after the class has been created.
    This method is used to finalize the namespace.
    """
    namespace = BaseSpace.postCompile(self, namespace)
    if self.getClassName() == 'KeeFlags':
      return namespace
    namespace['__kee_flags__'] = self.getKeeFlags()
    namespace['__kee_members__'] = None
    namespace['getKeeFlags'] = classmethod(self._getKeeFlagsFactory())
    return namespace
