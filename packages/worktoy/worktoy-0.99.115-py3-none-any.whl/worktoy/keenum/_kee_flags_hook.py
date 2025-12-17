"""
KeeFlagsHook provides a namespace hook for the 'KeeFlagsSpace' class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls.space_hooks import AbstractSpaceHook

from . import KeeFlag

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeFlagsHook(AbstractSpaceHook):
  """
  KeeFlagsHook provides a namespace hook for the 'KeeFlagsSpace' class.

  It intercepts key, KeeFlag pairs and redirects them to the 'addKeeFlag'
  method on the 'KeeFlagsSpace' instance.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def setItemPhase(self, key: str, val: Any, old: Any = None, ) -> bool:
    """
    Hook for setItem. This is called before the __setitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False.
    """
    if isinstance(val, KeeFlag):
      self.space.addKeeFlag(key, val)
      return True
    return False
