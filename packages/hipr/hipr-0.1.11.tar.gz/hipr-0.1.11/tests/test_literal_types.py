"""Test support for Literal types in hyperparameters."""

from __future__ import annotations

from typing import Literal

from pydantic import ValidationError
import pytest

from hipr import Hyper, configurable


def test_literal_type_basic() -> None:
  """Test that Literal types work for string enums."""

  @configurable
  def process(
    mode: Hyper[Literal["fast", "slow", "medium"]] = "fast",
  ) -> str:
    return f"Processing in {mode} mode"

  # Default should work
  assert process() == "Processing in fast mode"

  # Valid values should work
  assert process(mode="slow") == "Processing in slow mode"
  assert process(mode="medium") == "Processing in medium mode"

  # Config should work
  config = process.Config(mode="slow")
  fn = config.make()
  assert fn() == "Processing in slow mode"


def test_literal_validation() -> None:
  """Test that Literal types validate correctly."""

  @configurable
  def process(
    mode: Hyper[Literal["fast", "slow"]] = "fast",
  ) -> str:
    return mode

  # Invalid value should raise ValidationError
  with pytest.raises(ValidationError) as exc_info:
    process.Config(mode="invalid")

  error_str = str(exc_info.value)
  assert "mode" in error_str.lower()


def test_literal_int_types() -> None:
  """Test Literal with integer values."""

  @configurable
  def process(
    level: Hyper[Literal[1, 2, 3]] = 1,
  ) -> int:
    return level * 10

  assert process() == 10
  assert process(level=2) == 20
  assert process(level=3) == 30

  # Invalid value
  with pytest.raises(ValidationError):
    process.Config(level=4)


def test_literal_mixed_types() -> None:
  """Test Literal with mixed types."""

  @configurable
  def process(
    value: Hyper[Literal[1, "auto", True]] = "auto",
  ) -> str:
    return str(value)

  assert process() == "auto"
  assert process(value=1) == "1"
  assert process(value=True) == "True"

  config = process.Config(value=1)
  fn = config.make()
  assert fn() == "1"


def test_literal_in_class() -> None:
  """Test Literal types in class configurations."""

  @configurable
  class Optimizer:
    def __init__(
      self,
      algorithm: Hyper[Literal["sgd", "adam", "rmsprop"]] = "adam",
    ) -> None:
      self.algorithm = algorithm

  # Default
  opt = Optimizer()
  assert opt.algorithm == "adam"

  # Custom config
  config = Optimizer.Config(algorithm="sgd")
  opt2 = config.make()  # Now returns instance directly
  assert isinstance(opt2, Optimizer)
  assert opt2.algorithm == "sgd"


def test_literal_serialization() -> None:
  """Test that Literal types serialize correctly."""

  @configurable
  def process(
    mode: Hyper[Literal["fast", "slow"]] = "fast",
  ) -> str:
    return mode

  config = process.Config(mode="slow")

  # Serialize to dict
  config_dict = config.model_dump()
  assert config_dict == {"mode": "slow"}

  # Serialize to JSON
  config_json = config.model_dump_json()
  assert '"mode":"slow"' in config_json or '"mode": "slow"' in config_json

  # Deserialize
  loaded = process.Config.model_validate_json(config_json)
  assert loaded.mode == "slow"
