from __future__ import annotations

from typing import Annotated, Any
from unittest.mock import patch

import pytest

from hipr import Hyper, MakeableModel, configurable
from hipr.extraction import (
  create_field_info,
  get_type_hints_safe,
  unwrap_hyper,
)
from hipr.models import ConfigurableFunction
from hipr.typedefs import HyperMarker


def test_configurable_function_manual_usage():
  """Test manual instantiation and usage of ConfigurableFunction."""

  @configurable
  def my_func(x: Hyper[int] = 1) -> int:
    return x

  # configurable returns ConfigurableFunction now.
  # To test manual usage, we extract the underlying function and config.
  original_fn = my_func._func
  config_cls = my_func.Config

  indicator = ConfigurableFunction(original_fn, config_cls)

  # Test __call__
  assert indicator(x=5) == 5

  # Test __get__ (descriptor protocol)
  class MyClass:
    method = indicator

  obj = MyClass()
  bound_method = obj.method
  # Accessing on instance returns BoundConfigurableMethod
  assert hasattr(bound_method, "Config")
  # Accessing on class should return the indicator itself
  assert MyClass.method is indicator


def test_get_type_hints_name_error_on_class():
  """Test fallback logic when get_type_hints raises NameError for a class.

  When get_type_hints fails, get_type_hints_safe falls back to __annotations__.
  """

  class MyClass:
    pass

  # Mock get_type_hints to raise NameError
  call_count = 0

  def side_effect(*args, **kwargs):
    nonlocal call_count
    call_count += 1
    raise NameError("Mocked NameError")

  with patch("hipr.extraction.get_type_hints", side_effect=side_effect):
    hints = get_type_hints_safe(MyClass)

  assert hints == {}  # Falls back to __annotations__ which is empty
  assert call_count == 1  # Only one call, then fallback


def test_nested_config_instantiation_failure():
  """Test error handling when nested config instantiation fails."""

  class BrokenConfig(MakeableModel[Any]):
    def make(self) -> Any:
      return None

    def __init__(self, **data: Any):
      raise RuntimeError("Intentional failure")

  from hipr import DEFAULT

  # Create a field with DEFAULT - this should fail because BrokenConfig raises
  # on instantiation
  inner_type, constraints = unwrap_hyper(Annotated[BrokenConfig, HyperMarker])

  with pytest.raises((TypeError, RuntimeError)):
    create_field_info("param", inner_type, DEFAULT, constraints)


def test_unwrap_hyper():
  """Test unwrap_hyper function."""
  # Test simple Hyper[int]
  ann = Hyper[int]
  inner, constraints = unwrap_hyper(ann)
  assert inner is int
  assert constraints == ()

  # Test Hyper with constraints
  from hipr import Ge, Le

  ann2 = Hyper[int, Ge[0], Le[100]]
  inner2, constraints2 = unwrap_hyper(ann2)
  assert inner2 is int
  assert len(constraints2) == 2  # Ge[0] and Le[100]
