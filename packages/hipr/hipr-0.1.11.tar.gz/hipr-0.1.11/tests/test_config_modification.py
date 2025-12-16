"""Test runtime config modification patterns."""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from hipr import Ge, Hyper, Le, configurable


def test_config_dict_roundtrip() -> None:
  """Test config -> dict -> config roundtrip."""

  @configurable
  def process(
    period: Hyper[int, Ge[1]] = 14,
    alpha: Hyper[float, Ge[0.0], Le[1.0]] = 0.5,
  ) -> float:
    return period * alpha

  # Create config
  config1 = process.Config(period=20, alpha=0.8)

  # Convert to dict
  config_dict = config1.model_dump()
  assert config_dict == {"period": 20, "alpha": 0.8}

  # Recreate from dict
  config2 = process.Config(**config_dict)
  assert config2.period == 20
  assert config2.alpha == 0.8

  # Should produce same function behavior
  fn1 = config1.make()
  fn2 = config2.make()
  assert fn1() == fn2()


def test_config_copy_and_modify() -> None:
  """Test creating modified copies of configs."""

  @configurable
  def process(
    value: Hyper[int] = 10,
    multiplier: Hyper[float] = 2.0,
  ) -> float:
    return value * multiplier

  config1 = process.Config(value=10, multiplier=2.0)

  # Create a modified copy
  config2 = config1.model_copy(update={"value": 20})

  assert config1.value == 10
  assert config2.value == 20
  assert config2.multiplier == 2.0


def test_partial_config_update() -> None:
  """Test updating only some fields of a config."""

  @configurable
  def process(
    a: Hyper[int] = 1,
    b: Hyper[int] = 2,
    c: Hyper[int] = 3,
  ) -> int:
    return a + b + c

  config = process.Config(a=10, b=20, c=30)

  # Update only 'b'
  updated_config = config.model_copy(update={"b": 50})

  assert updated_config.a == 10
  assert updated_config.b == 50
  assert updated_config.c == 30


def test_config_validation_on_creation() -> None:
  """Test that validation happens at config creation time."""

  @configurable
  def process(value: Hyper[int, Ge[0], Le[100]] = 50) -> int:
    return value

  # Valid value should work
  config = process.Config(value=75)
  assert config.value == 75

  # Invalid value should fail immediately
  with pytest.raises(ValidationError):
    process.Config(value=200)


def test_json_serialization() -> None:
  """Test JSON serialization of configs."""

  @configurable
  def process(
    period: Hyper[int] = 14,
    threshold: Hyper[float] = 0.5,
  ) -> float:
    return period * threshold

  config = process.Config(period=20, threshold=0.8)

  # Convert to JSON
  json_str = config.model_dump_json()
  assert isinstance(json_str, str)
  assert "20" in json_str
  assert "0.8" in json_str

  # Parse from JSON
  import json

  parsed = json.loads(json_str)
  config2 = process.Config(**parsed)
  assert config2.period == 20
  assert config2.threshold == 0.8


def test_config_equality() -> None:
  """Test that configs with same values are equal."""

  @configurable
  def process(value: Hyper[int] = 10) -> int:
    return value

  config1 = process.Config(value=20)
  config2 = process.Config(value=20)
  config3 = process.Config(value=30)

  # Same values should be equal
  assert config1 == config2

  # Different values should not be equal
  assert config1 != config3


def test_config_immutability() -> None:
  """Test that config instances are immutable (frozen)."""

  @configurable
  def process(value: Hyper[int] = 10) -> int:
    return value

  config = process.Config(value=20)

  # Direct mutation should raise ValidationError
  with pytest.raises(ValidationError):
    config.value = 30

  # Value should remain unchanged
  assert config.value == 20


def test_config_hashability() -> None:
  """Test that config instances are hashable and can be used as dict keys."""

  @configurable
  def process(value: Hyper[int] = 10) -> int:
    return value

  config1 = process.Config(value=20)
  config2 = process.Config(value=20)
  config3 = process.Config(value=30)

  # Should be hashable
  assert hash(config1) == hash(config2)
  assert hash(config1) != hash(config3)

  # Should work as dict keys
  d = {config1: "first", config3: "third"}
  assert d[config2] == "first"  # config2 equals config1
  assert d[config3] == "third"

  # Should work in sets
  s = {config1, config2, config3}
  assert len(s) == 2  # config1 and config2 are equal
