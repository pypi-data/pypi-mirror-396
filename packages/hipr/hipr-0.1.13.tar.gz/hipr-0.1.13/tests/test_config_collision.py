import pytest

from hipr import Hyper, configurable


def test_model_config_parameter_raises_error():
  """Test that defining a parameter named 'model_config' raises ValueError.

  'model_config' is reserved by Pydantic for model configuration and
  cannot be used as a Config field name.
  """

  # Test with function
  with pytest.raises(ValueError, match="reserved by Pydantic"):

    @configurable
    def my_func(model_config: Hyper[int] = 1):
      pass

  # Test with class
  with pytest.raises(ValueError, match="reserved by Pydantic"):

    @configurable
    class MyClass:
      def __init__(self, model_config: Hyper[int] = 1):
        pass
