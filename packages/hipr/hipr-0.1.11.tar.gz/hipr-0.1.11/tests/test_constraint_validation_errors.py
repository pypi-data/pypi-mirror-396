"""Test constraint validation error handling at constraint creation time."""

from __future__ import annotations

import pytest

from hipr import Ge, Gt, Le, Lt, MaxLen, MinLen, MultipleOf, Pattern


def test_ge_requires_numeric_value() -> None:
  """Test that Ge raises TypeError for non-numeric values."""
  with pytest.raises(TypeError, match="numeric value"):
    Ge["invalid"]

  with pytest.raises(TypeError, match="numeric value"):
    Ge[None]


def test_le_requires_numeric_value() -> None:
  """Test that Le raises TypeError for non-numeric values."""
  with pytest.raises(TypeError, match="numeric value"):
    Le["invalid"]

  with pytest.raises(TypeError, match="numeric value"):
    Le[None]


def test_gt_requires_numeric_value() -> None:
  """Test that Gt raises TypeError for non-numeric values."""
  with pytest.raises(TypeError, match="numeric value"):
    Gt["invalid"]

  with pytest.raises(TypeError, match="numeric value"):
    Gt[None]


def test_lt_requires_numeric_value() -> None:
  """Test that Lt raises TypeError for non-numeric values."""
  with pytest.raises(TypeError, match="numeric value"):
    Lt["invalid"]

  with pytest.raises(TypeError, match="numeric value"):
    Lt[None]


def test_minlen_requires_integer() -> None:
  """Test that MinLen raises TypeError for non-integer values."""
  with pytest.raises(TypeError, match="integer"):
    MinLen[3.5]

  with pytest.raises(TypeError, match="integer"):
    MinLen["invalid"]


def test_minlen_requires_non_negative() -> None:
  """Test that MinLen raises ValueError for negative values."""
  with pytest.raises(ValueError, match="non-negative"):
    MinLen[-1]

  with pytest.raises(ValueError, match="non-negative"):
    MinLen[-100]


def test_maxlen_requires_integer() -> None:
  """Test that MaxLen raises TypeError for non-integer values."""
  with pytest.raises(TypeError, match="integer"):
    MaxLen[3.5]

  with pytest.raises(TypeError, match="integer"):
    MaxLen["invalid"]


def test_maxlen_requires_non_negative() -> None:
  """Test that MaxLen raises ValueError for negative values."""
  with pytest.raises(ValueError, match="non-negative"):
    MaxLen[-1]

  with pytest.raises(ValueError, match="non-negative"):
    MaxLen[-100]


def test_pattern_requires_string() -> None:
  """Test that Pattern raises TypeError for non-string values."""
  with pytest.raises(TypeError, match="string"):
    Pattern[123]

  with pytest.raises(TypeError, match="string"):
    Pattern[None]


def test_pattern_validates_regex() -> None:
  """Test that Pattern raises ValueError for invalid regex."""
  from hipr.constraints import InvalidPatternError

  with pytest.raises(InvalidPatternError, match="Invalid regex pattern"):
    Pattern["[invalid"]  # Unclosed bracket

  with pytest.raises(InvalidPatternError, match="Invalid regex pattern"):
    Pattern["(unclosed"]  # Unclosed paren

  with pytest.raises(InvalidPatternError, match="Invalid regex pattern"):
    Pattern["*invalid"]  # Invalid quantifier


def test_multipleof_requires_numeric_value() -> None:
  """Test that MultipleOf raises TypeError for non-numeric values."""
  with pytest.raises(TypeError, match="numeric value"):
    MultipleOf["invalid"]

  with pytest.raises(TypeError, match="numeric value"):
    MultipleOf[None]


def test_multipleof_requires_positive_value() -> None:
  """Test that MultipleOf raises ValueError for zero or negative values."""
  with pytest.raises(ValueError, match="positive"):
    MultipleOf[0]

  with pytest.raises(ValueError, match="positive"):
    MultipleOf[-5]

  with pytest.raises(ValueError, match="positive"):
    MultipleOf[-0.5]


def test_numeric_constraints_accept_int_and_float() -> None:
  """Test that numeric constraints accept both int and float."""
  # Should not raise
  ge_int = Ge[5]
  ge_float = Ge[5.5]
  assert ge_int.ge == 5
  assert ge_float.ge == 5.5

  le_int = Le[10]
  le_float = Le[10.5]
  assert le_int.le == 10
  assert le_float.le == 10.5

  gt_int = Gt[0]
  gt_float = Gt[0.1]
  assert gt_int.gt == 0
  assert gt_float.gt == 0.1

  lt_int = Lt[100]
  lt_float = Lt[100.5]
  assert lt_int.lt == 100
  assert lt_float.lt == 100.5

  mo_int = MultipleOf[5]
  mo_float = MultipleOf[2.5]
  assert mo_int.multiple_of == 5
  assert mo_float.multiple_of == 2.5


def test_length_constraints_accept_zero() -> None:
  """Test that MinLen and MaxLen accept zero as valid."""
  # Should not raise
  min_zero = MinLen[0]
  max_zero = MaxLen[0]
  assert min_zero.min_length == 0
  assert max_zero.max_length == 0


def test_pattern_accepts_valid_regex() -> None:
  """Test that Pattern accepts valid regex patterns."""
  from hipr.constraints import PatternConstraint

  # Should not raise
  pattern1 = Pattern[r"^[a-z]+$"]
  pattern2 = Pattern[r"\d{3}-\d{4}"]
  pattern3 = Pattern[r"[A-Z]{2,5}"]

  assert isinstance(pattern1, PatternConstraint)
  assert pattern1.pattern == r"^[a-z]+$"
  assert isinstance(pattern2, PatternConstraint)
  assert pattern2.pattern == r"\d{3}-\d{4}"
  assert isinstance(pattern3, PatternConstraint)
  assert pattern3.pattern == r"[A-Z]{2,5}"
