from dataclasses import dataclass

from hipr import Hyper, configurable


def test_config_str_matches_repr() -> None:
  @configurable
  @dataclass
  class MyModel:
    x: Hyper[int] = 1
    y: Hyper[str] = "foo"

  config = MyModel.Config(x=10)

  # Check that repr output is as expected (Pydantic style)
  repr_output = repr(config)
  assert "MyModelConfig" in repr_output
  assert "x=10" in repr_output

  # Check that str output matches repr output
  # This is what the user requested ("as pretty as __repr__")
  assert str(config) == repr(config)


def test_function_config_str_matches_repr() -> None:
  @configurable
  def my_func(a: Hyper[int] = 1) -> int:
    return a

  func_config = my_func.Config(a=5)
  assert "MyFuncConfig" in repr(func_config)
  assert str(func_config) == repr(func_config)
