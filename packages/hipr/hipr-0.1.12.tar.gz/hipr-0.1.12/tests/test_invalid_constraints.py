"""Test contradictory and impossible constraint combinations."""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from hipr import (
  Ge,
  Gt,
  Hyper,
  Le,
  Lt,
  MaxLen,
  MinLen,
  Pattern,
  configurable,
)


def test_impossible_constraint_combination() -> None:
  """Test constraint where no value can satisfy both."""
  # Ge[10] and Lt[10] means >= 10 and < 10, which is impossible
  # This should now be caught at decoration time
  with pytest.raises(ValueError, match="Conflicting constraints"):

    @configurable
    def process(
      value: Hyper[int, Ge[10], Lt[10]] = 10,
    ) -> int:
      return value


def test_contradictory_le_and_ge() -> None:
  """Test Le[x] with Ge[y] where y > x."""
  # No value can be >= 100 and <= 50
  # This should now be caught at decoration time
  with pytest.raises(ValueError, match="Conflicting constraints"):

    @configurable
    def process(
      value: Hyper[int, Ge[100], Le[50]] = 75,
    ) -> int:
      return value


def test_minlen_greater_than_maxlen() -> None:
  """Test MinLen > MaxLen which makes string impossible."""
  # No string can satisfy both constraints
  # This should now be caught at decoration time
  with pytest.raises(ValueError, match="Conflicting constraints"):

    @configurable
    def process(
      text: Hyper[str, MinLen[10], MaxLen[5]] = "hello",
    ) -> str:
      return text


def test_multiple_ge_constraints() -> None:
  """Test multiple Ge constraints (should use most restrictive)."""

  @configurable
  def process(
    value: Hyper[int, Ge[5], Ge[10]] = 15,
  ) -> int:
    return value

  # Should use Ge[10] (most restrictive)
  config = process.Config(value=10)
  assert config.value == 10

  # Value less than 10 should fail
  with pytest.raises(ValidationError):
    process.Config(value=7)


def test_gt_and_ge_on_same_value() -> None:
  """Test Gt[5] and Ge[5] together (Gt is more restrictive)."""

  @configurable
  def process(
    value: Hyper[int, Gt[5], Ge[5]] = 6,
  ) -> int:
    return value

  # Gt[5] is more restrictive, so 5 should fail
  with pytest.raises(ValidationError):
    process.Config(value=5)

  # 6 should pass
  config = process.Config(value=6)
  assert config.value == 6


def test_invalid_pattern_regex() -> None:
  """Test that invalid regex pattern raises ValueError."""
  with pytest.raises(ValueError, match="Invalid regex pattern"):
    # "[a-z" is an invalid regex (missing closing bracket)
    _ = Pattern["[a-z"]


def test_required_hyper_with_constraints() -> None:
  """Test that required Hyper parameters with constraints work correctly."""

  @configurable
  def func(p: Hyper[int, Ge[0], Le[100]]) -> int:
    return p

  # Must provide the required param
  config = func.Config(p=50)
  fn = config.make()
  assert fn() == 50

  # Constraints are still enforced
  with pytest.raises(ValidationError):
    func.Config(p=-5)  # Less than Ge[0]


def test_overlapping_lt_and_le() -> None:
  """Test Lt and Le with same value (Lt is more restrictive)."""

  @configurable
  def process(
    value: Hyper[int, Lt[10], Le[10]] = 5,
  ) -> int:
    return value

  # Lt[10] is more restrictive, so 10 should fail
  with pytest.raises(ValidationError):
    process.Config(value=10)

  # 9 should pass
  config = process.Config(value=9)
  assert config.value == 9
