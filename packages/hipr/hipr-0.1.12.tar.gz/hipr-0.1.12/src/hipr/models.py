"""Base model classes for hipr."""

from __future__ import annotations

from collections.abc import Callable
import functools
from types import UnionType
from typing import Any, get_args, get_origin, override

from pydantic import BaseModel, ConfigDict, PrivateAttr

__all__ = [
  "BoundFunction",
  "ConfigurableFunction",
  "MakeableModel",
  "is_makeable_model",
]


class MakeableModel[R](BaseModel):
  """
  Base class for generated Config classes.

  Provides:
  - Frozen (immutable) configuration
  - make() method to instantiate the target
  - Instance caching (in base class)
  - Arbitrary type support
  """

  model_config = ConfigDict(
    frozen=True,
    arbitrary_types_allowed=True,
  )

  _instance: R | None = PrivateAttr(default=None)

  def make(self) -> R:
    """Create an instance of the target from this config.

    Handles caching automatically. Subclasses should override _make_impl().
    """
    if self._instance is not None:
      return self._instance
    instance = self._make_impl()
    self._instance = instance
    return instance

  @override
  def __str__(self) -> str:
    return self.__repr__()

  def _make_impl(self) -> R:
    """Override this method to implement instance creation."""
    raise NotImplementedError("Subclasses must implement _make_impl()")


class BoundFunction[R]:
  """
  A callable wrapper that exposes hyperparameters as attributes.

  When a @configurable function's Config.make() is called, it returns
  a BoundFunction instead of a plain function. This allows accessing
  the bound hyperparameters:

      @configurable
      def process(data: pd.Series, window: Hyper[int] = 10) -> pd.Series:
          return data.rolling(window).mean()

      config = process.Config(window=20)
      fn = config.make()
      result = fn(data)      # Call it like a function
      print(fn.window)       # Access the bound hyperparameter (20)
  """

  __slots__ = ("_doc", "_func", "_hyper_kwargs", "_name")

  def __init__(
    self,
    func: Callable[..., R],
    hyper_kwargs: dict[str, Any],
  ) -> None:
    self._func = func
    self._hyper_kwargs = hyper_kwargs
    self._name = func.__name__
    self._doc = func.__doc__

  @property
  def __name__(self) -> str:
    return self._name

  @property
  @override
  def __doc__(self) -> str | None:  # pyright: ignore[reportIncompatibleVariableOverride]
    return self._doc

  @property
  def __wrapped__(self) -> Callable[..., R]:
    return self._func

  def __call__(self, *args: Any, **kwargs: Any) -> R:
    """Call the function with bound hyperparameters."""
    return self._func(*args, **self._hyper_kwargs, **kwargs)

  def __getattr__(self, name: str) -> Any:
    """Access bound hyperparameters as attributes."""
    if name.startswith("_"):
      raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
    try:
      return self._hyper_kwargs[name]
    except KeyError:
      raise AttributeError(
        f"'{type(self).__name__}' has no attribute '{name}'"
      ) from None

  @override
  def __repr__(self) -> str:
    params = ", ".join(f"{k}={v!r}" for k, v in self._hyper_kwargs.items())
    return f"<BoundFunction {self._name}({params})>"


def _create_type_proxy(
  func: Callable[..., Any],
  config_cls: type[MakeableModel[Any]],
) -> type:
  """Create a proxy type for type hinting nested function configs."""

  class _TypeProxy:
    Config = config_cls

  _TypeProxy.__name__ = f"{func.__name__}Type"
  _TypeProxy.__qualname__ = f"{func.__qualname__}.Type"
  return _TypeProxy


class _ConfigurableCallableBase[R]:
  """Base class for ConfigurableFunction and BoundConfigurableMethod."""

  __slots__ = ("_config_cls", "_func", "_type_proxy")  # pyright: ignore[reportUninitializedInstanceVariable]

  @property
  def Config(self) -> type[MakeableModel[Callable[..., R]]]:
    """Access the Config class for this function/method."""
    return self._config_cls

  @property
  def Type(self) -> type:
    """Proxy class for type hinting nested function configs.

    Use this when you want to nest a configurable function inside another:

        @configurable
        def inner(x: Hyper[int] = 1) -> int:
            return x

        @configurable
        def outer(
            data: list[float],
            inner_fn: Hyper[inner.Type] = DEFAULT,
        ) -> float:
            return inner_fn() * sum(data)
    """
    return self._type_proxy


class ConfigurableFunction[R](_ConfigurableCallableBase[R]):
  """
  Wrapper for decorated functions that separates Hyper args from call args.

  Remains directly callable while also providing .Config and .Type access.

  Attributes:
    Config: The generated Pydantic model class for this function's hyperparameters.
    Type: A proxy class that exposes .Config, useful for type hinting nested
          function configs (e.g., `inner_fn: Hyper[outer.Type] = DEFAULT`).
  """

  # Note: No __slots__ here - we need functools.update_wrapper to set __name__,
  # __module__, etc. directly on the instance for proper introspection
  __name__: str  # pyright: ignore[reportUninitializedInstanceVariable]

  def __init__(
    self,
    func: Callable[..., R],
    config_cls: type[MakeableModel[Callable[..., R]]],
  ) -> None:
    self._func = func
    self._config_cls = config_cls
    self._type_proxy = _create_type_proxy(func, config_cls)

    # Preserve function metadata (docstring, name, module, etc.)
    functools.update_wrapper(self, func)

  def __call__(self, *args: Any, **kwargs: Any) -> R:
    """Call the underlying function directly."""
    return self._func(*args, **kwargs)

  def __get__(
    self,
    obj: Any,
    objtype: type | None = None,
  ) -> ConfigurableFunction[R] | BoundConfigurableMethod[R]:
    """Descriptor protocol for method binding."""
    if obj is None:
      return self
    return BoundConfigurableMethod(self._func, self._config_cls, obj)

  @override
  def __repr__(self) -> str:
    fields = self._config_cls.model_fields
    if fields:
      field_strs: list[str] = []
      for name, info in fields.items():
        type_str = getattr(info.annotation, "__name__", str(info.annotation))
        field_strs.append(f"{name}: {type_str}")
      fields_repr = ", ".join(field_strs)
      return f"<ConfigurableFunction {self.__name__}({fields_repr})>"
    return f"<ConfigurableFunction {self.__name__}()>"


class BoundConfigurableMethod[R](_ConfigurableCallableBase[R]):
  """A configurable function bound to an instance."""

  __slots__ = ("_instance",)

  def __init__(
    self,
    func: Callable[..., R],
    config_cls: type[MakeableModel[Callable[..., R]]],
    instance: Any,
  ) -> None:
    self._func = func
    self._config_cls = config_cls
    self._instance = instance
    self._type_proxy = _create_type_proxy(func, config_cls)

  def __call__(self, *args: Any, **kwargs: Any) -> R:
    """Call the method with the bound instance."""
    return self._func(self._instance, *args, **kwargs)


def is_makeable_model(type_ann: Any) -> bool:
  """Check if a type annotation represents a MakeableModel."""
  if type_ann is None:
    return False

  # Direct class check
  if isinstance(type_ann, type) and issubclass(type_ann, MakeableModel):
    return True

  # Check Union types (T | T.Config)
  origin = get_origin(type_ann)
  if origin is UnionType:
    args = get_args(type_ann)
    return any(is_makeable_model(arg) for arg in args)

  return False
