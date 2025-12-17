"""Test the new Hyper[T, Ge[2], Le[100]] syntax in type annotations."""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from hipr import Ge, Hyper, Le, configurable


@configurable
def constrained_function(
  value: float,
  period: Hyper[int, Ge[2], Le[100]] = 14,
  threshold: Hyper[float, Ge[0.0], Le[1.0]] = 0.5,
) -> float:
  """Test function with constraints in type annotations."""
  return value * period * threshold


def test_annotated_syntax_basic() -> None:
  """Test that the new syntax works for basic calls."""
  result = constrained_function(10.0)
  assert result == 70.0  # 10 * 14 * 0.5


def test_annotated_syntax_with_params() -> None:
  """Test calling with custom parameters."""
  result = constrained_function(10.0, period=5, threshold=0.2)
  assert result == 10.0  # 10 * 5 * 0.2


def test_annotated_syntax_config() -> None:
  """Test that Config class works with annotated syntax."""
  config = constrained_function.Config(period=10, threshold=0.8)
  assert config.period == 10
  assert config.threshold == 0.8


def test_annotated_syntax_validation() -> None:
  """Test that Field constraints from annotations are enforced."""
  # Valid values should work
  config = constrained_function.Config(period=50, threshold=0.5)
  assert config.period == 50

  # Test lower bound for period
  with pytest.raises(ValidationError):
    constrained_function.Config(period=1, threshold=0.5)

  # Test upper bound for period
  with pytest.raises(ValidationError):
    constrained_function.Config(period=101, threshold=0.5)

  # Test lower bound for threshold
  with pytest.raises(ValidationError):
    constrained_function.Config(period=10, threshold=-0.1)

  # Test upper bound for threshold
  with pytest.raises(ValidationError):
    constrained_function.Config(period=10, threshold=1.1)


def test_annotated_syntax_make() -> None:
  """Test that Config.make() works with annotated syntax."""
  config = constrained_function.Config(period=20, threshold=0.25)
  fn = config.make()
  result = fn(value=10.0)
  assert result == 50.0  # 10 * 20 * 0.25
