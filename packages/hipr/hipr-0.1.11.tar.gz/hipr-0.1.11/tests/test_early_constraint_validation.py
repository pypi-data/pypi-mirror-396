"""Test that contradictory constraints are caught at decoration time."""

from __future__ import annotations

import pytest

from hipr import Ge, Gt, Hyper, Le, Lt, MaxLen, MinLen, configurable


def test_contradictory_ge_lt_caught_at_decoration() -> None:
  """Test that Ge[10] and Lt[10] is caught when decorator is applied."""
  with pytest.raises(ValueError, match="Conflicting constraints.*exclusive"):

    @configurable
    def func(x: Hyper[int, Ge[10], Lt[10]] = 10) -> int:
      return x


def test_contradictory_ge_le_caught_at_decoration() -> None:
  """Test that Ge[100] and Le[50] is caught when decorator is applied."""
  with pytest.raises(
    ValueError, match="Conflicting constraints.*lower bound.*upper bound"
  ):

    @configurable
    def func(x: Hyper[int, Ge[100], Le[50]] = 75) -> int:
      return x


def test_contradictory_gt_le_caught_at_decoration() -> None:
  """Test that Gt[100] and Le[100] is caught when decorator is applied."""
  with pytest.raises(ValueError, match="Conflicting constraints.*exclusive"):

    @configurable
    def func(x: Hyper[int, Gt[100], Le[100]] = 101) -> int:
      return x


def test_contradictory_ge_lt_same_value_caught() -> None:
  """Test that Ge[50] and Lt[50] is caught (no value satisfies both)."""
  with pytest.raises(ValueError, match="Conflicting constraints.*exclusive"):

    @configurable
    def func(x: Hyper[int, Ge[50], Lt[50]] = 50) -> int:
      return x


def test_contradictory_minlen_maxlen_caught_at_decoration() -> None:
  """Test that MinLen[10] and MaxLen[5] is caught when decorator is applied."""
  with pytest.raises(
    ValueError, match="Conflicting constraints.*min_length.*max_length"
  ):

    @configurable
    def func(text: Hyper[str, MinLen[10], MaxLen[5]] = "hello") -> str:
      return text


def test_valid_overlapping_constraints_allowed() -> None:
  """Test that valid overlapping constraints are allowed."""
  # These should not raise - they have valid ranges

  @configurable
  def func1(x: Hyper[int, Ge[5], Le[100]] = 50) -> int:
    return x

  @configurable
  def func2(x: Hyper[int, Gt[0], Lt[100]] = 50) -> int:
    return x

  @configurable
  def func3(text: Hyper[str, MinLen[5], MaxLen[10]] = "hello") -> str:
    return text

  # Should work fine
  assert func1(x=50) == 50
  assert func2(x=50) == 50
  assert func3(text="hello") == "hello"


def test_multiple_ge_constraints_allowed() -> None:
  """Test that multiple Ge constraints are allowed (most restrictive wins)."""

  # Should not raise - Ge[10] is more restrictive
  @configurable
  def func(x: Hyper[int, Ge[5], Ge[10]] = 15) -> int:
    return x

  assert func(x=15) == 15


def test_same_bound_ge_le_allowed() -> None:
  """Test that Ge[50] and Le[50] is allowed (only 50 is valid)."""

  # Should not raise - value 50 satisfies both
  @configurable
  def func(x: Hyper[int, Ge[50], Le[50]] = 50) -> int:
    return x

  config = func.Config(x=50)
  assert config.x == 50


def test_same_minlen_maxlen_allowed() -> None:
  """Test that MinLen[5] and MaxLen[5] is allowed (fixed length)."""

  # Should not raise - exactly length 5 strings are valid
  @configurable
  def func(text: Hyper[str, MinLen[5], MaxLen[5]] = "hello") -> str:
    return text

  config = func.Config(text="world")
  assert config.text == "world"


def test_error_message_includes_parameter_name() -> None:
  """Test that error messages include the parameter name for clarity."""
  with pytest.raises(ValueError, match=r"my_param"):

    @configurable
    def func(my_param: Hyper[int, Ge[100], Le[50]] = 75) -> int:
      return my_param


def test_error_message_includes_bound_values() -> None:
  """Test that error messages include the actual bound values."""
  with pytest.raises(ValueError, match=r"100.*50"):

    @configurable
    def func(x: Hyper[int, Ge[100], Le[50]] = 75) -> int:
      return x


def test_class_constraint_validation() -> None:
  """Test that constraint validation works for class __init__ parameters."""
  with pytest.raises(ValueError, match="Conflicting constraints"):

    @configurable
    class MyClass:
      def __init__(self, value: Hyper[int, Ge[100], Lt[50]] = 75) -> None:
        self.value = value


def test_dataclass_constraint_validation() -> None:
  """Test that constraint validation works for dataclass fields."""
  from dataclasses import dataclass

  with pytest.raises(ValueError, match="Conflicting constraints"):

    @configurable
    @dataclass
    class MyDataclass:
      value: Hyper[int, Ge[100], Le[50]] = 75
