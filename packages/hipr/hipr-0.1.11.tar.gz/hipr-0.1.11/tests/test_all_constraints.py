"""Test all available constraint markers."""

from __future__ import annotations

from typing import Literal

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
  MultipleOf,
  Pattern,
  configurable,
)


@configurable
def numeric_constraints(
  value: float,
  ge_val: Hyper[int, Ge[0]] = 5,
  le_val: Hyper[int, Le[100]] = 50,
  gt_val: Hyper[float, Gt[0.0]] = 1.5,
  lt_val: Hyper[float, Lt[10.0]] = 5.0,
) -> float:
  """Test function with numeric constraints."""
  return value + ge_val + le_val + gt_val + lt_val


@configurable
def string_constraints(
  text: Hyper[str, MinLen[2], MaxLen[10]] = "hello",
  # Use string literal for regex to avoid syntax error in forward ref
  email: Hyper[
    str, Pattern[Literal["^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"]]
  ] = "test@example.com",
) -> str:
  """Test function with string constraints."""
  return f"{text}: {email}"


def test_ge_constraint() -> None:
  """Test Ge (greater than or equal) constraint."""
  config = numeric_constraints.Config(ge_val=0)
  assert config.ge_val == 0

  with pytest.raises(ValidationError):
    numeric_constraints.Config(ge_val=-1)


def test_le_constraint() -> None:
  """Test Le (less than or equal) constraint."""
  config = numeric_constraints.Config(le_val=100)
  assert config.le_val == 100

  with pytest.raises(ValidationError):
    numeric_constraints.Config(le_val=101)


def test_gt_constraint() -> None:
  """Test Gt (greater than) constraint."""
  config = numeric_constraints.Config(gt_val=0.1)
  assert config.gt_val == 0.1

  with pytest.raises(ValidationError):
    numeric_constraints.Config(gt_val=0.0)


def test_lt_constraint() -> None:
  """Test Lt (less than) constraint."""
  config = numeric_constraints.Config(lt_val=9.9)
  assert config.lt_val == 9.9

  with pytest.raises(ValidationError):
    numeric_constraints.Config(lt_val=10.0)


def test_multiple_of_constraint() -> None:
  """Test MultipleOf constraint."""

  @configurable
  def with_multiple(val: Hyper[int, MultipleOf[5]] = 10) -> int:
    return val

  config = with_multiple.Config(val=15)
  assert config.val == 15

  with pytest.raises(ValidationError):
    with_multiple.Config(val=7)


def test_min_len_constraint() -> None:
  """Test MinLen constraint."""
  config = string_constraints.Config(text="ab")
  assert config.text == "ab"

  with pytest.raises(ValidationError):
    string_constraints.Config(text="a")


def test_max_len_constraint() -> None:
  """Test MaxLen constraint."""
  config = string_constraints.Config(text="1234567890")
  assert config.text == "1234567890"

  with pytest.raises(ValidationError):
    string_constraints.Config(text="12345678901")


def test_pattern_constraint() -> None:
  """Test Pattern constraint."""
  config = string_constraints.Config(email="user@domain.com")
  assert config.email == "user@domain.com"

  with pytest.raises(ValidationError):
    string_constraints.Config(email="invalid-email")


def test_combined_constraints() -> None:
  """Test using multiple constraints together."""
  config = numeric_constraints.Config(ge_val=10, le_val=90, gt_val=2.5, lt_val=8.0)
  assert config.ge_val == 10
  assert config.le_val == 90
  assert config.gt_val == 2.5
  assert config.lt_val == 8.0


def test_function_calls_with_constraints() -> None:
  """Test that functions work correctly with constrained values."""
  result = numeric_constraints(10.0)
  # 10.0 + 5 + 50 + 1.5 + 5.0 = 71.5
  assert result == 71.5

  result = string_constraints()
  assert result == "hello: test@example.com"
