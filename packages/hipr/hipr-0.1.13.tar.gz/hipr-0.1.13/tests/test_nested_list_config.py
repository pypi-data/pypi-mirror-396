"""Test nested configs in containers - list, dict, Sequence, Mapping, etc."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from hipr import DEFAULT, configurable


@configurable
@dataclass
class Layer:
  scale: float = 1.0

  def __call__(self, data: float) -> float:
    return data * self.scale


# Test with list[T]
@configurable
@dataclass
class NetworkWithList:
  layers: list[Layer] = DEFAULT

  def __call__(self, data: float) -> float:
    for layer in self.layers:
      data = layer(data)
    return data


# Test with Sequence[T]
@configurable
@dataclass
class NetworkWithSequence:
  layers: Sequence[Layer] = DEFAULT

  def __call__(self, data: float) -> float:
    for layer in self.layers:
      data = layer(data)
    return data


# Test with dict[str, T]
@configurable
@dataclass
class NetworkWithDict:
  layers: dict[str, Layer] = DEFAULT

  def __call__(self, data: float) -> float:
    for layer in self.layers.values():
      data = layer(data)
    return data


# Test with Mapping[str, T]
@configurable
@dataclass
class NetworkWithMapping:
  layers: Mapping[str, Layer] = DEFAULT

  def __call__(self, data: float) -> float:
    for layer in self.layers.values():
      data = layer(data)
    return data


def test_list_with_default() -> None:
  """list[Layer] = DEFAULT uses empty list."""
  config = NetworkWithList.Config()
  network = config.make()
  assert network.layers == []
  assert network(10.0) == 10.0


def test_list_with_explicit_configs() -> None:
  """Explicit list of configs works."""
  config = NetworkWithList.Config(
    layers=[Layer.Config(scale=2.0), Layer.Config(scale=3.0)]
  )
  network = config.make()
  assert network(10.0) == 60.0  # 10 * 2 * 3


def test_sequence_with_default() -> None:
  """Sequence[Layer] = DEFAULT uses empty list."""
  config = NetworkWithSequence.Config()
  network = config.make()
  assert network.layers == []
  assert network(10.0) == 10.0


def test_sequence_with_explicit_configs() -> None:
  """Explicit sequence of configs works."""
  config = NetworkWithSequence.Config(
    layers=[Layer.Config(scale=2.0), Layer.Config(scale=0.5)]
  )
  network = config.make()
  assert network(10.0) == 10.0  # 10 * 2 * 0.5


def test_dict_with_default() -> None:
  """dict[str, Layer] = DEFAULT uses empty dict."""
  config = NetworkWithDict.Config()
  network = config.make()
  assert network.layers == {}
  assert network(10.0) == 10.0


def test_dict_with_explicit_configs() -> None:
  """Explicit dict of configs works."""
  config = NetworkWithDict.Config(
    layers={"first": Layer.Config(scale=2.0), "second": Layer.Config(scale=5.0)}
  )
  network = config.make()
  assert network(1.0) == 10.0  # 1 * 2 * 5


def test_mapping_with_default() -> None:
  """Mapping[str, Layer] = DEFAULT uses empty dict."""
  config = NetworkWithMapping.Config()
  network = config.make()
  assert network.layers == {}
  assert network(10.0) == 10.0


def test_mapping_with_explicit_configs() -> None:
  """Explicit mapping of configs works."""
  config = NetworkWithMapping.Config(
    layers={"a": Layer.Config(scale=3.0), "b": Layer.Config(scale=2.0)}
  )
  network = config.make()
  assert network(5.0) == 30.0  # 5 * 3 * 2
