"""Core type definitions for hipr."""

from typing import TYPE_CHECKING, Annotated, Any, Never, override

__all__ = ["DEFAULT", "DefaultSentinel", "Hyper", "HyperMarker"]


class HyperMarker:
  """Sentinel class to mark parameters as hyperparameters."""

  __slots__ = ()


class DefaultSentinel:
  """Sentinel to indicate a field should use its type's default Config."""

  __slots__ = ()

  @override
  def __repr__(self) -> str:
    return "DEFAULT"


if TYPE_CHECKING:
  # At type-checking time, DEFAULT should be assignable to any type
  # Using Never makes it a bottom type that's assignable to anything
  DEFAULT: Never
else:
  DEFAULT = DefaultSentinel()


if TYPE_CHECKING:
  # At type-checking time, Hyper[T] is just T with metadata
  # This makes it fully transparent to type checkers
  type Hyper[T, *Args] = Annotated[T, HyperMarker, *Args]
else:

  class Hyper:
    """
    Type annotation for hyperparameters.

    Usage:
        x: Hyper[int]  # Simple hyperparameter
        x: Hyper[int, Ge[0], Le[100]]  # With constraints

    For classes/dataclasses: marks a field as a hyperparameter
    For functions: separates config args from call args
    """

    __slots__ = ()

    def __class_getitem__(cls, args: Any) -> Any:
      if not isinstance(args, tuple):
        # Single type: Hyper[int]
        return Annotated[args, HyperMarker]
      # Type with constraints: Hyper[int, Ge[0], Le[100]]
      inner_type = args[0]
      constraints = args[1:]
      return Annotated[inner_type, HyperMarker, *constraints]
