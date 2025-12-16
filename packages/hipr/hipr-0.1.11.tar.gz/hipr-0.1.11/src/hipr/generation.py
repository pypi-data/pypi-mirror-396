"""The configurable decorator and related utilities."""

from __future__ import annotations

from collections.abc import Callable
import inspect
import threading
from typing import TYPE_CHECKING, Any, get_args, get_origin, overload

from pydantic import create_model

from hipr.extraction import (
  extract_class_params,
  extract_function_hyper_params,
  get_public_fields,
  get_type_hints_safe,
)
from hipr.models import BoundFunction, ConfigurableFunction, MakeableModel

if TYPE_CHECKING:
  from pydantic.fields import FieldInfo

__all__ = ["configurable"]

# Lock for thread-safe decoration
_decoration_lock = threading.Lock()

# Reserved Pydantic field names that cannot be used as Config field names
_RESERVED_PYDANTIC_NAMES = {"model_config", "model_fields", "model_computed_fields"}


def _to_pascal_case(name: str) -> str:
  """Convert snake_case or other naming to PascalCase.

  Examples:
    my_func -> MyFunc
    myFunc -> Myfunc
    my_function_name -> MyFunctionName
  """
  return "".join(word.capitalize() for word in name.split("_"))


@overload
def configurable[T](target: type[T]) -> type[T]: ...  # pyright: ignore[reportOverlappingOverload]


@overload
def configurable(target: Callable[..., Any]) -> ConfigurableFunction[Any]: ...


def configurable[T](
  target: type[T] | Callable[..., Any],
) -> type[T] | ConfigurableFunction[Any]:
  """
  Make a class or function configurable.

  For classes/dataclasses:
      - Creates a Config class as target.Config
      - Config.make() returns an instance of the class
      - The original class can still be instantiated directly

  For functions:
      - Separates Hyper-annotated args from regular args
      - Hyper args become Config fields
      - Regular args remain call-time arguments
      - Config.make() returns a callable with Hyper args bound

  Examples:
      @configurable
      @dataclass
      class Model:
          learning_rate: Hyper[float, Ge[0], Le[1]] = 0.01
          num_layers: Hyper[int, Ge[1]] = 3

      config = Model.Config(learning_rate=0.001)
      model = config.make()

      @configurable
      def train(
          data: Dataset,  # Call-time arg
          epochs: Hyper[int, Ge[1]] = 10,  # Config arg
      ) -> Metrics:
          ...

      config = train.Config(epochs=20)
      trainer = config.make()  # Returns callable
      result = trainer(my_dataset)  # Calls train(my_dataset, epochs=20)
  """
  if isinstance(target, type):
    return _configurable_class(target)  # pyright: ignore[reportUnknownVariableType]
  if callable(target):
    return _configurable_function(target)
  raise TypeError(f"configurable requires a class or function, got {type(target)}")


def _configurable_class[T](cls: type[T]) -> type[T]:
  """Apply configurable to a class or dataclass."""
  # Fast path: check if THIS class has its OWN Config (not inherited)
  if "Config" in cls.__dict__:
    config_attr = cls.__dict__["Config"]
    if isinstance(config_attr, type) and issubclass(config_attr, MakeableModel):
      return cls

  with _decoration_lock:
    # Double-check after acquiring lock - check cls.__dict__ to avoid inherited Config
    if "Config" in cls.__dict__:
      config_attr = cls.__dict__["Config"]
      if isinstance(config_attr, type) and issubclass(config_attr, MakeableModel):
        return cls

    # Extract parameters
    params = extract_class_params(cls)

    # Create the Config class
    config_cls = _create_class_config(cls, params)

    # Attach to the original class
    cls.Config = config_cls  # type: ignore[attr-defined]

    return cls


def _create_class_config[T](
  cls: type[T],
  params: dict[str, tuple[Any, FieldInfo]],
) -> type[MakeableModel[T]]:
  """Create a Config class for a target class."""
  # Check for reserved Pydantic field names
  for name in params:
    if name in _RESERVED_PYDANTIC_NAMES:
      raise ValueError(
        f"Parameter '{name}' is reserved by Pydantic and cannot be used as a Config field"
      )

  # Create the model dynamically - pyright can't infer the type here
  config_cls: type[MakeableModel[T]] = create_model(  # pyright: ignore[reportUnknownVariableType]
    f"{cls.__name__}Config",
    __base__=MakeableModel[cls],  # type: ignore[valid-type]
    **params,  # type: ignore[arg-type]
  )

  # Add the _make_impl method (base class handles caching in make())
  config_cls._make_impl = _create_class_make_impl(cls)  # type: ignore[method-assign]

  return config_cls  # pyright: ignore[reportUnknownVariableType]


def _create_class_make_impl[T](cls: type[T]) -> Callable[[MakeableModel[T]], T]:
  """Create the _make_impl() method for a class Config."""
  # Get init hints for recursive make decisions
  init_hints = get_type_hints_safe(cls.__init__) if hasattr(cls, "__init__") else {}

  def _make_impl(self: MakeableModel[T]) -> T:
    # Extract fields and recursively make nested configs
    kwargs = get_public_fields(self)
    made_kwargs: dict[str, Any] = {}

    for name, value in kwargs.items():
      expected_type = init_hints.get(name)
      made_kwargs[name] = _recursive_make(value, expected_type)

    # Create instance
    return cls(**made_kwargs)

  return _make_impl


def _configurable_function(func: Callable[..., Any]) -> ConfigurableFunction[Any]:
  """Apply configurable to a function."""
  # Check if it's a method (has self parameter)
  sig = inspect.signature(func)
  params = list(sig.parameters.keys())
  skip_first = bool(params and params[0] in ("self", "cls"))

  # Extract only Hyper parameters
  hyper_params = extract_function_hyper_params(func, skip_first=skip_first)

  # Create Config class
  config_cls = _create_function_config(func, hyper_params)

  # Return wrapper
  return ConfigurableFunction(func, config_cls)


def _create_function_config(
  func: Callable[..., Any],
  params: dict[str, tuple[Any, FieldInfo]],
) -> type[MakeableModel[Callable[..., Any]]]:
  """Create a Config class for a function."""
  # Check for reserved Pydantic field names
  for name in params:
    if name in _RESERVED_PYDANTIC_NAMES:
      raise ValueError(
        f"Parameter '{name}' is reserved by Pydantic and cannot be used as a Config field"
      )

  # The return type is a callable that takes non-Hyper args
  return_type = Callable[..., Any]

  # Create PascalCase config name (my_func -> MyFuncConfig)
  config_name = _to_pascal_case(func.__name__) + "Config"

  # Create the model dynamically - pyright can't infer the type here
  config_cls: type[MakeableModel[Callable[..., Any]]] = create_model(  # pyright: ignore[reportUnknownVariableType]
    config_name,
    __base__=MakeableModel[return_type],  # type: ignore[valid-type]
    **params,  # type: ignore[arg-type]
  )

  # Add the _make_impl method (base class handles caching in make())
  config_cls._make_impl = _create_function_make_impl(func)  # type: ignore[method-assign]

  return config_cls  # pyright: ignore[reportUnknownVariableType]


def _create_function_make_impl(
  func: Callable[..., Any],
) -> Callable[[MakeableModel[Any]], BoundFunction[Any]]:
  """Create the _make_impl() method for a function Config."""

  def _make_impl(self: MakeableModel[Any]) -> BoundFunction[Any]:
    # Extract hyper args
    hyper_kwargs = get_public_fields(self)

    # Recursively make nested configs
    made_kwargs: dict[str, Any] = {}
    for name, value in hyper_kwargs.items():
      made_kwargs[name] = _recursive_make(value, None)

    # Create BoundFunction that exposes hyper params as attributes
    return BoundFunction(func, made_kwargs)

  return _make_impl


def _recursive_make(
  value: Any,
  expected_type: Any = None,
) -> Any:
  """
  Recursively make nested config objects.

  If value is a MakeableModel, call make() on it.
  If value is a list/dict, recursively process elements.
  """
  _ = expected_type  # Used for future type-aware decisions

  # Make MakeableModel instances
  if isinstance(value, MakeableModel):
    return value.make()  # pyright: ignore[reportUnknownVariableType]

  # Recursively handle lists
  if isinstance(value, list):
    inner_type = _get_list_inner_type(expected_type)
    result_list: list[Any] = []
    for item in value:  # pyright: ignore[reportUnknownVariableType]
      result_list.append(_recursive_make(item, inner_type))
    return result_list

  # Recursively handle dicts
  if isinstance(value, dict):
    value_type = _get_dict_value_type(expected_type)
    result_dict: dict[Any, Any] = {}
    for k, v in value.items():  # pyright: ignore[reportUnknownVariableType]
      result_dict[k] = _recursive_make(v, value_type)
    return result_dict

  return value


def _get_list_inner_type(type_ann: Any) -> Any:
  """Get the inner type of a list annotation."""
  if type_ann is None:
    return None
  origin = get_origin(type_ann)
  if origin is list:
    args = get_args(type_ann)
    return args[0] if args else None
  return None


def _get_dict_value_type(type_ann: Any) -> Any:
  """Get the value type of a dict annotation."""
  if type_ann is None:
    return None
  origin = get_origin(type_ann)
  if origin is dict:
    args = get_args(type_ann)
    return args[1] if len(args) >= 2 else None  # noqa: PLR2004
  return None
