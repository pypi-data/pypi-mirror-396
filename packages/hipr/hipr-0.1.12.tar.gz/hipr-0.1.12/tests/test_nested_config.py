"""Test nested configs at module level (real-world usage)."""

from __future__ import annotations

import pandas as pd

from hipr import Hyper, configurable


@configurable
def inner_fn(
  data: pd.Series,
  multiplier: Hyper[float] = 2.0,
) -> float:
  sum_value: float = data.sum().item()
  return sum_value * multiplier


InnerConfig = inner_fn.Config


_DEFAULT_INNER_CONFIG = InnerConfig()


@configurable
def outer_fn(
  data: pd.Series,
  offset: Hyper[float] = 10.0,
  inner_fn_made: Hyper[InnerConfig] = _DEFAULT_INNER_CONFIG,
) -> float:
  # inner_fn_made is auto-made by _recursive_make
  inner_result: float = inner_fn_made(data=data)
  return inner_result + offset


def test_module_level_nested_config() -> None:
  """Verify nested configs work at module level."""
  # Test with defaults
  config = outer_fn.Config()
  fn = config.make()
  test_series = pd.Series([1.0, 2.0, 3.0])
  result: float = fn(data=test_series)
  # inner: (1+2+3) * 2.0 = 12.0, outer: 12.0 + 10.0 = 22.0
  assert result == 22.0

  # Test with overrides
  # Note: Type checker doesn't know about dynamically generated Config classes,
  # so the parameters below will show as type errors, but they work at runtime
  config2 = outer_fn.Config(
    offset=5.0,
    inner_fn_made=inner_fn.Config(multiplier=3.0),
  )
  fn2 = config2.make()
  result2: float = fn2(data=test_series)
  # inner: (1+2+3) * 3.0 = 18.0, outer: 18.0 + 5.0 = 23.0
  assert result2 == 23.0
