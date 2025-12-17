"""Tests for stub generation."""

import ast
from pathlib import Path
from textwrap import dedent

import pytest

from hipr.cli.generate_stubs import main
from hipr.constraints import validate_constraint_conflicts
from hipr.stubs import (
  ConfigurableInfo,
  HyperParam,
  generate_stub_for_file,
  scan_module,
)
from hipr.stubs.generator import (
  _generate_class_stub,
  _generate_config_class,
  _generate_function_stub,
  generate_stub_content,
)
from hipr.stubs.scanner import (
  _extract_default,
  _get_annotation_str,
  _is_configurable_decorator,
  _is_hyper_annotation,
  _scan_class,
  _scan_function,
  _unwrap_hyper,
)


@pytest.fixture
def temp_source_file(tmp_path: Path) -> Path:
  source_code = dedent("""
        from hipr import configurable, Hyper, Ge

        @configurable
        def my_func(
            data: list[float],
            period: Hyper[int, Ge[1]] = 14,
            alpha: float = 0.5,
        ) -> list[float]:
            return [x * alpha for x in data]

        @configurable
        class MyIndicator:
            def __init__(self, window: Hyper[int] = 10):
                self.window = window

            def __call__(self, data: list[float]) -> list[float]:
                return data
    """)
  file_path = tmp_path / "test_source.py"
  file_path.write_text(source_code, encoding="utf-8")
  return file_path


def test_is_configurable_decorated():
  code = "@configurable\ndef foo(): pass"
  tree = ast.parse(code)
  func_def = tree.body[0]
  assert isinstance(func_def, ast.FunctionDef)
  assert _is_configurable_decorator(func_def.decorator_list[0])

  code = "def bar(): pass"
  tree = ast.parse(code)
  func_def = tree.body[0]
  assert isinstance(func_def, ast.FunctionDef)
  assert len(func_def.decorator_list) == 0


def test_is_hyper_annotation():
  code = "def f(x: Hyper[int]): pass"
  tree = ast.parse(code)
  func = tree.body[0]
  assert isinstance(func, ast.FunctionDef)
  arg = func.args.args[0]
  assert _is_hyper_annotation(arg.annotation)


def test_unwrap_hyper():
  code = "def f(x: Hyper[int, Ge[0], Le[10]]): pass"
  tree = ast.parse(code)
  func = tree.body[0]
  assert isinstance(func, ast.FunctionDef)
  arg = func.args.args[0]
  inner = _unwrap_hyper(arg.annotation)
  assert inner == "int"


def test_scan_module(temp_source_file: Path):
  infos = scan_module(temp_source_file)
  # Should find both the function and the class
  assert len(infos) == 2

  # Check the function
  func_info = infos[0]
  assert func_info.name == "my_func"
  assert len(func_info.params) == 1
  assert func_info.params[0].name == "period"
  assert len(func_info.call_params) == 2  # data and alpha

  # Check the class
  class_info = infos[1]
  assert class_info.name == "MyIndicator"
  assert len(class_info.params) == 1
  assert class_info.params[0].name == "window"
  assert class_info.params[0].type_annotation == "int"
  assert class_info.params[0].default_value == "10"


def test_generate_config_class():
  info = ConfigurableInfo(
    name="my_func",
    is_class=False,
    params=[HyperParam("p1", "int", "1")],
    call_params=[("data", "list", None)],
    return_type="list[float]",
  )
  code = _generate_config_class(info)
  assert "class Config(MakeableModel" in code
  assert "p1: int" in code
  assert "def __init__(self, *, p1: int = ...) -> None: ..." in code


def test_generate_class_stub():
  info = ConfigurableInfo(
    name="MyClass",
    is_class=True,
    params=[HyperParam("window", "int", "10")],
    return_type="MyClass",
  )
  code = _generate_class_stub(info)
  assert "class MyClass:" in code
  assert "class Config(MakeableModel[MyClass]):" in code
  assert "window: int" in code


def test_generate_function_stub():
  info = ConfigurableInfo(
    name="my_func",
    is_class=False,
    params=[HyperParam("window", "int", "10")],
    call_params=[("data", "list", None)],
    return_type="float",
  )
  code = _generate_function_stub(info)
  assert "class my_func:" in code
  assert "class Config(MakeableModel" in code
  assert "def __call__(self, data: list, window: int = ...) -> float: ..." in code


def test_generate_stub_content(temp_source_file: Path):
  infos = scan_module(temp_source_file)
  content = generate_stub_content(infos, temp_source_file)
  assert "class Config(MakeableModel" in content
  assert "from hipr import MakeableModel" in content


def test_validate_constraint_conflicts_catches_contradictions():
  """Test that validation catches contradictory numeric bounds."""
  with pytest.raises(ValueError, match="Conflicting constraints"):
    validate_constraint_conflicts({"ge": 100, "le": 50}, "x")


def test_validate_constraint_conflicts_catches_strict_bounds():
  """Test that validation catches impossible strict/non-strict bounds."""
  with pytest.raises(ValueError, match="exclusive"):
    validate_constraint_conflicts({"ge": 50, "lt": 50}, "x")


def test_validate_constraint_conflicts_catches_length_issues():
  """Test that validation catches MinLen > MaxLen."""
  with pytest.raises(ValueError, match="Conflicting constraints"):
    validate_constraint_conflicts({"min_length": 10, "max_length": 5}, "text")


def test_validate_constraint_conflicts_allows_valid_constraints():
  """Test that validation allows valid constraints."""
  # These should not raise
  validate_constraint_conflicts({"ge": 10, "le": 100}, "x")
  validate_constraint_conflicts({"gt": 0, "lt": 100}, "x")
  validate_constraint_conflicts({"min_length": 5, "max_length": 50}, "text")


def test_scan_module_with_dataclass(tmp_path: Path):
  """Test that scan_module properly handles @dataclass decorated classes."""
  dataclass_file = tmp_path / "dataclass_test.py"
  dataclass_file.write_text(
    dedent("""
        from dataclasses import dataclass
        from hipr import configurable, Hyper, Ge

        @configurable
        @dataclass
        class DataConfig:
            learning_rate: Hyper[float, Ge[0.0]] = 0.01
            batch_size: Hyper[int, Ge[1]] = 32
            epochs: Hyper[int, Ge[1]] = 10
    """)
  )

  infos = scan_module(dataclass_file)
  assert len(infos) == 1

  class_info = infos[0]
  assert class_info.name == "DataConfig"
  assert len(class_info.params) == 3

  # Check learning_rate param
  assert class_info.params[0].name == "learning_rate"
  assert class_info.params[0].type_annotation == "float"
  assert class_info.params[0].default_value == "0.01"


def test_generate_stub_for_file(tmp_path: Path):
  """Test generate_stub_for_file creates stub."""
  source_file = tmp_path / "source.py"
  source_file.write_text(
    dedent("""
        from hipr import configurable, Hyper

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x
    """)
  )

  result = generate_stub_for_file(source_file)
  assert result is not None

  stub_file = tmp_path / "source.pyi"
  assert stub_file.exists()
  stub_content = stub_file.read_text()
  assert "class Config(MakeableModel" in stub_content


def test_generate_stub_for_file_without_configurable(tmp_path: Path):
  """Test generate_stub_for_file returns None for file without @configurable."""
  source_file = tmp_path / "plain.py"
  source_file.write_text(
    dedent("""
        def regular_func(x: int) -> int:
            return x
    """)
  )

  result = generate_stub_for_file(source_file)
  assert result is None

  stub_file = tmp_path / "plain.pyi"
  assert not stub_file.exists()


def test_main_with_directory(tmp_path: Path):
  """Test main() with directory."""
  test_dir = tmp_path / "custom"
  test_dir.mkdir()

  test_file = test_dir / "module.py"
  test_file.write_text(
    dedent("""
        from hipr import configurable, Hyper

        @configurable
        def func(x: Hyper[int] = 5) -> int:
            return x
    """)
  )

  exit_code = main([str(test_dir)])
  assert exit_code == 0

  stub_file = test_dir / "module.pyi"
  assert stub_file.exists()


def test_main_nonexistent_directory(tmp_path: Path):
  """Test main() with nonexistent pattern."""
  nonexistent = tmp_path / "does_not_exist"

  exit_code = main([str(nonexistent)])
  assert exit_code == 1  # No files found


def test_main_single_file(tmp_path: Path):
  """Test main() with a single Python file."""
  test_file = tmp_path / "single_module.py"
  test_file.write_text(
    dedent("""
        from hipr import configurable, Hyper

        @configurable
        def single_func(x: Hyper[int] = 10) -> int:
            return x
    """)
  )

  exit_code = main([str(test_file)])
  assert exit_code == 0

  stub_file = tmp_path / "single_module.pyi"
  assert stub_file.exists()


def test_main_handles_syntax_errors(tmp_path: Path):
  """Test main() handles files with syntax errors gracefully."""
  test_dir = tmp_path / "src"
  test_dir.mkdir()

  bad_file = test_dir / "bad_syntax.py"
  bad_file.write_text("def broken( # invalid syntax")

  # Should not crash, just skip the file
  exit_code = main([str(test_dir)])
  assert exit_code == 0


def test_main_skips_test_files(tmp_path: Path):
  """Test main() skips test_*.py files."""
  test_dir = tmp_path / "src"
  test_dir.mkdir()

  test_file = test_dir / "test_something.py"
  test_file.write_text(
    dedent("""
        from hipr import configurable, Hyper

        @configurable
        def test_func(x: Hyper[int] = 1) -> int:
            return x
    """)
  )

  exit_code = main([str(test_dir)])
  assert exit_code == 0

  # No stub should be created for test files
  stub_file = test_dir / "test_something.pyi"
  assert not stub_file.exists()


def test_extract_default():
  """Test _extract_default."""
  assert _extract_default(None) is None

  code = "10"
  tree = ast.parse(code, mode="eval")
  assert _extract_default(tree.body) == "10"


def test_get_annotation_str():
  """Test _get_annotation_str."""
  assert _get_annotation_str(None) == "Any"

  code = "int"
  tree = ast.parse(code, mode="eval")
  assert _get_annotation_str(tree.body) == "int"


def test_scan_function():
  """Test _scan_function."""
  code = dedent("""
        @configurable
        def my_func(x: Hyper[int] = 1) -> int:
            return x
    """)
  tree = ast.parse(code)
  func = tree.body[0]
  assert isinstance(func, ast.FunctionDef)

  info = _scan_function(func)
  assert info is not None
  assert info.name == "my_func"
  assert len(info.params) == 1
  assert info.params[0].name == "x"


def test_scan_class():
  """Test _scan_class."""
  code = dedent("""
        @configurable
        class MyClass:
            def __init__(self, x: Hyper[int] = 1):
                self.x = x
    """)
  tree = ast.parse(code)
  cls = tree.body[0]
  assert isinstance(cls, ast.ClassDef)

  info = _scan_class(cls)
  assert info is not None
  assert info.name == "MyClass"
  assert info.is_class is True
  assert len(info.params) == 1


def test_scan_class_with_dataclass_fields():
  """Test _scan_class with dataclass-style fields."""
  code = dedent("""
        @configurable
        @dataclass
        class MyClass:
            x: int = 1
            y: float = 0.5
    """)
  tree = ast.parse(code)
  cls = tree.body[0]
  assert isinstance(cls, ast.ClassDef)

  info = _scan_class(cls)
  assert info is not None
  assert len(info.params) == 2
  assert info.params[0].name == "x"
  assert info.params[1].name == "y"


def test_default_sentinel_in_stub_generation(tmp_path: Path):
  """Test that DEFAULT sentinel is properly handled in stub generation."""
  source_file = tmp_path / "with_default.py"
  source_file.write_text(
    dedent("""
        from hipr import configurable, Hyper, DEFAULT

        @configurable
        class InnerConfig:
            def __init__(self, param: Hyper[int] = 10):
                self.param = param

        @configurable
        def outer_func(
            data: list[float],
            inner: Hyper[InnerConfig.Config] = DEFAULT,
        ) -> float:
            return sum(data)
    """)
  )

  # Generate stub content
  infos = scan_module(source_file)
  stub_content = generate_stub_content(infos, source_file)

  # Verify DEFAULT is imported
  assert "DEFAULT" in stub_content

  # Verify the default value is preserved in the stub
  assert "inner: InnerConfig.Config = DEFAULT" in stub_content


def test_scan_module_rejects_contradictory_constraints(tmp_path: Path):
  """Test that scan_module raises error for contradictory constraints."""
  bad_file = tmp_path / "bad.py"
  bad_file.write_text(
    dedent("""
        from hipr import configurable, Hyper, Ge, Le

        @configurable
        def bad_func(x: Hyper[int, Ge[100], Le[50]] = 75) -> int:
            return x
    """)
  )

  with pytest.raises(ValueError, match="[Cc]onflict"):
    scan_module(bad_file)


def test_scan_module_accepts_valid_constraints(tmp_path: Path):
  """Test that scan_module works with valid constraints."""
  good_file = tmp_path / "good.py"
  good_file.write_text(
    dedent("""
        from hipr import configurable, Hyper, Ge, Le

        @configurable
        def good_func(x: Hyper[int, Ge[10], Le[100]] = 50) -> int:
            return x
    """)
  )

  functions = scan_module(good_file)
  assert len(functions) == 1
  assert functions[0].name == "good_func"


def test_scan_module_with_methods(tmp_path: Path):
  """Test that scan_module properly handles instance, class, and static methods."""
  methods_file = tmp_path / "methods_test.py"
  methods_file.write_text(
    dedent("""
        from hipr import configurable, Hyper, Ge

        class MyClass:
            @configurable
            def instance_method(
                self, data: list[float], window: Hyper[int, Ge[1]] = 10
            ) -> float:
                return sum(data) / window

            @classmethod
            @configurable
            def class_method(
                cls, data: list[float], alpha: Hyper[float, Ge[0.0]] = 0.5
            ) -> float:
                return sum(data) * alpha

            @staticmethod
            @configurable
            def static_method(
                data: list[float], beta: Hyper[float] = 1.0
            ) -> float:
                return sum(data) + beta
    """)
  )

  functions = scan_module(methods_file)
  # Should find all 3 methods
  assert len(functions) == 3
  names = {f.name for f in functions}
  assert "instance_method" in names
  assert "class_method" in names
  assert "static_method" in names


def test_main_verbose_mode(tmp_path: Path):
  """Test main() with verbose flag."""
  test_dir = tmp_path / "src"
  test_dir.mkdir()

  test_file = test_dir / "verbose_test.py"
  test_file.write_text(
    dedent("""
        from hipr import configurable, Hyper

        @configurable
        def verbose_func(x: Hyper[int] = 1) -> int:
            return x
    """)
  )

  # Run with verbose flag
  exit_code = main([str(test_dir), "--verbose"])
  assert exit_code == 0

  stub_file = test_dir / "verbose_test.pyi"
  assert stub_file.exists()


def test_nested_config_type_transformation(tmp_path: Path):
  """Test that nested configurable types are transformed to .Config in Config class."""
  source_file = tmp_path / "nested_configs.py"
  source_file.write_text(
    dedent("""
        from hipr import configurable, Hyper, DEFAULT

        @configurable
        class InnerOptimizer:
            learning_rate: Hyper[float] = 0.01

        @configurable
        class OuterModel:
            hidden_size: Hyper[int] = 128
            optimizer: Hyper[InnerOptimizer] = DEFAULT

        @configurable
        def train(
            data: list[float],
            epochs: Hyper[int] = 10,
            model: Hyper[OuterModel] = DEFAULT,
        ) -> float:
            return sum(data)
    """)
  )

  infos = scan_module(source_file)
  stub_content = generate_stub_content(infos, source_file)

  # The Config class's __init__ should use .Config types for nested configurables
  # This is critical for type-correct nested config instantiation

  # For OuterModel.Config, the optimizer param should be InnerOptimizer.Config
  assert "optimizer: InnerOptimizer.Config" in stub_content
  assert "optimizer: InnerOptimizer.Config = DEFAULT" in stub_content

  # For train.Config, the model param should be OuterModel.Config
  assert "model: OuterModel.Config" in stub_content
  assert "model: OuterModel.Config = DEFAULT" in stub_content

  # Primitive types should NOT be transformed
  assert "hidden_size: int" in stub_content
  assert "epochs: int" in stub_content
  assert "learning_rate: float" in stub_content


def test_required_nested_config_type_transformation(tmp_path: Path):
  """Test that REQUIRED nested configurables (no DEFAULT) are also transformed."""
  source_file = tmp_path / "required_nested.py"
  source_file.write_text(
    dedent("""
        from hipr import configurable, Hyper

        @configurable
        class Optimizer:
            lr: Hyper[float] = 0.01

        @configurable
        class Model:
            # Required nested config - no DEFAULT
            optimizer: Hyper[Optimizer]
            hidden_size: Hyper[int] = 128
    """)
  )

  infos = scan_module(source_file)
  stub_content = generate_stub_content(infos, source_file)

  # Even without DEFAULT, non-primitive Hyper types should become .Config
  # because you always pass Config objects to Config.__init__
  assert "optimizer: Optimizer.Config" in stub_content

  # Primitive types unchanged
  assert "hidden_size: int" in stub_content
  assert "lr: float" in stub_content
