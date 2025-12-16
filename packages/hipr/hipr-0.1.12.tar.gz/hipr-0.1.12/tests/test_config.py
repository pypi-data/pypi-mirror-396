"""Tests for the configurable decorator and configuration system."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ValidationError
import pytest

from hipr import (
  Hyper,
  MakeableModel,
  configurable,
)


def test_configurable_decorator_creates_correct_wrapper_and_config() -> None:
  """Verify @configurable creates a wrapper and a Pydantic model with correct fields."""

  @configurable
  def dummy_indicator(
    data: pd.Series,
    window: Hyper[int] = 10,
    name: Hyper[str] = "default_name",
  ) -> str:
    return f"{name}:{data.sum()}:{window}"

  # 1. Assert that the decorator returns a callable with a Config attribute
  assert callable(dummy_indicator)
  assert hasattr(dummy_indicator, "Config")

  # 2. Assert that the .Config class was created and attached
  config_cls = dummy_indicator.Config
  assert issubclass(config_cls, MakeableModel)
  assert issubclass(config_cls, BaseModel)

  # 3. Assert that the model has the correct fields and types
  fields = config_cls.model_fields
  assert list(fields.keys()) == ["window", "name"]
  assert fields["window"].annotation is int
  assert fields["name"].annotation is str
  # FieldInfo.default returns Any in pydantic-stubs, so we accept it
  window_default: int = fields["window"].default
  name_default: str = fields["name"].default
  assert window_default == 10
  assert name_default == "default_name"


def test_config_validation_is_enforced() -> None:
  """Verify that Pydantic validation catches invalid input."""

  @configurable
  def dummy_indicator(
    data: pd.Series,
    window: Hyper[int] = 10,
  ) -> int:
    # pandas .item() returns Any in stubs, so we annotate it
    sum_value: int = data.sum().item()
    return sum_value + window

  # This should raise a ValidationError because window is not an int
  with pytest.raises(ValidationError):
    dummy_indicator.Config(window="not_an_int")


def test_configurable_indicator_is_callable() -> None:
  """Verify the wrapper object is callable and passes through calls correctly."""

  @configurable
  def dummy_indicator(
    data: pd.Series,
    window: Hyper[int] = 10,
  ) -> int:
    sum_value: int = data.sum().item()
    return sum_value + window

  # The decorated object should be directly callable
  result: int | float = dummy_indicator(data=pd.Series([1, 2, 3]))
  assert result == (1 + 2 + 3) + 10


def test_config_make_returns_partial_function() -> None:
  """Verify .make() returns a partial function with config values bound."""

  @configurable
  def dummy_indicator(
    data: pd.Series,
    window: Hyper[int] = 10,
  ) -> float:
    sum_value: float = data.sum().item()
    return sum_value * window

  # Create a config instance with window=5
  config = dummy_indicator.Config(window=5)
  partial_fn = config.make()

  test_series = pd.Series([1.0, 2.0, 3.0])
  result: float = partial_fn(data=test_series)
  assert result == test_series.sum() * 5.0


def test_make_method_produces_correct_function() -> None:
  """Verify that the .make() method creates a correctly configured function."""

  @configurable
  def dummy_indicator(
    data: pd.Series,
    multiplier: Hyper[float] = 2.0,
  ) -> float:
    sum_value: float = data.sum().item()
    return sum_value * multiplier

  # Use Config to create an instance
  my_config = dummy_indicator.Config(multiplier=5.0)
  made_function = my_config.make()

  test_series = pd.Series([1.0, 2.0, 3.0])
  result: float = made_function(data=test_series)
  assert result == test_series.sum() * 5.0


def test_configurable_with_required_hyper_param() -> None:
  """Verify that Hyper parameters without defaults work as required fields."""

  @configurable
  def process(
    window: Hyper[int],
  ) -> int:
    return window * 2

  # Config class should have a required 'window' field
  config_cls = process.Config
  assert "window" in config_cls.model_fields

  # Must provide required param
  config = process.Config(window=5)
  fn = config.make()
  assert fn() == 10


def test_configurable_with_no_hyperparameters() -> None:
  """Verify correct behavior for a function with no hyperparameters."""

  @configurable
  def simple_function(
    data: pd.Series,
  ) -> pd.Series:
    return data

  assert hasattr(simple_function, "Config")
  config_cls = simple_function.Config
  assert not config_cls.model_fields

  config_instance = simple_function.Config()
  made_function = config_instance.make()

  test_series = pd.Series([1, 2])
  result_series: pd.Series = made_function(data=test_series)
  assert result_series.equals(test_series)
