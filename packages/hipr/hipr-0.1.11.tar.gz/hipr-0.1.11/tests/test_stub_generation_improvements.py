"""Tests for stub generation improvements.

Tests for:
- @override decorator on make() methods
- Import filtering (only used imports)
- TYPE_CHECKING block handling
- Public items inclusion (classes, functions, constants)
- Config field skipping
- Constants and type alias formatting
"""

from pathlib import Path
from textwrap import dedent

from hipr.stubs.generator import generate_stub_content
from hipr.stubs.scanner import scan_module


class TestOverrideDecorator:
  """Tests for @override decorator on make() methods."""

  def test_class_config_has_override(self, tmp_path: Path) -> None:
    """Test that class Config.make() has @override decorator."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        @configurable
        class MyClass:
            def __init__(self, x: Hyper[int] = 10):
                self.x = x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "@override" in content
    assert "from typing import override" in content
    # Check override appears before make
    lines = content.split("\n")
    for i, line in enumerate(lines):
      if "def make(self)" in line and i > 0:
        assert "@override" in lines[i - 1]

  def test_function_config_has_override(self, tmp_path: Path) -> None:
    """Test that function Config.make() has @override decorator."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        @configurable
        def my_func(data: list, x: Hyper[int] = 10) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "@override" in content
    # Check override appears before make
    lines = content.split("\n")
    for i, line in enumerate(lines):
      if "def make(self)" in line and i > 0:
        assert "@override" in lines[i - 1]


class TestImportFiltering:
  """Tests for import filtering - only keep used imports."""

  def test_unused_imports_removed(self, tmp_path: Path) -> None:
    """Test that unused imports are not included in stub."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from typing import List, Dict, Optional, Any
        from collections import OrderedDict
        from hipr import configurable, Hyper, Ge, Le, DEFAULT

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # These should NOT be in the stub (unused)
    assert "List" not in content
    assert "Dict" not in content
    assert "Optional" not in content
    assert "Any" not in content
    assert "OrderedDict" not in content
    assert "Ge" not in content
    assert "Le" not in content

    # These SHOULD be in the stub
    assert "MakeableModel" in content
    assert "override" in content

  def test_used_imports_kept(self, tmp_path: Path) -> None:
    """Test that used imports are kept in stub."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        import numpy as np
        from typing import Optional
        from hipr import configurable, Hyper

        @configurable
        def my_func(x: Hyper[int] = 10) -> Optional[np.ndarray]:
            return None
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # These should be in the stub (used in return type)
    assert "import numpy as np" in content
    assert "Optional" in content

  def test_type_checking_block_filtered(self, tmp_path: Path) -> None:
    """Test that TYPE_CHECKING imports don't duplicate top-level imports."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from __future__ import annotations
        from typing import TYPE_CHECKING
        from collections.abc import Callable
        from hipr import configurable, Hyper

        if TYPE_CHECKING:
            from collections.abc import Callable  # duplicate

        @configurable
        def my_func(x: Hyper[int] = 10, cb: Callable[[int], int] | None = None) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # Callable should appear only once (not duplicated from TYPE_CHECKING)
    assert content.count("from collections.abc import Callable") == 1

  def test_hipr_imports_not_duplicated(self, tmp_path: Path) -> None:
    """Test that hipr imports from source don't duplicate our generated ones."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper, DEFAULT, MakeableModel

        @configurable
        class MyClass:
            def __init__(self, x: Hyper[int] = 10):
                self.x = x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # Should only have one hipr import line
    assert content.count("from hipr import") == 1


class TestPublicItemsInclusion:
  """Tests for including all public items in stubs."""

  def test_public_function_included(self, tmp_path: Path) -> None:
    """Test that non-configurable public functions are included."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        def helper_func(x: int) -> int:
            return x * 2

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return helper_func(x)
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "def helper_func(x: int) -> int:" in content
    assert "..." in content  # Body should be ellipsis

  def test_private_function_excluded(self, tmp_path: Path) -> None:
    """Test that private functions are not included."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        def _private_helper(x: int) -> int:
            return x * 2

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return _private_helper(x)
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "_private_helper" not in content

  def test_public_class_included(self, tmp_path: Path) -> None:
    """Test that non-configurable public classes are included."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        class HelperClass:
            x: int
            def do_something(self, y: int) -> int:
                return self.x + y

        @configurable
        def my_func(helper: HelperClass, x: Hyper[int] = 10) -> int:
            return helper.do_something(x)
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "class HelperClass:" in content
    assert "x: int" in content
    assert "def do_something(self, y: int) -> int:" in content

  def test_main_function_included(self, tmp_path: Path) -> None:
    """Test that main() function is included (it's public, not private)."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x

        def main() -> None:
            result = my_func.Config().make()(10)
            print(result)
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "def main() -> None:" in content


class TestConfigFieldSkipping:
  """Tests for skipping Config: ClassVar fields."""

  def test_config_classvar_skipped_in_configurable(self, tmp_path: Path) -> None:
    """Test that Config: ClassVar fields are skipped in @configurable classes."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from typing import ClassVar
        from hipr import configurable, Hyper, MakeableModel

        @configurable
        class MyClass:
            Config: ClassVar[type[MakeableModel[object]]]

            def __init__(self, x: Hyper[int] = 10):
                self.x = x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # Should have class Config (our generated one)
    assert "class Config(MakeableModel[MyClass]):" in content
    # Should NOT have Config: ClassVar (the field declaration)
    assert "Config: ClassVar" not in content

  def test_config_classvar_skipped_in_public_class(self, tmp_path: Path) -> None:
    """Test that Config: ClassVar fields are skipped in non-configurable classes too."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from typing import ClassVar
        from hipr import configurable, Hyper, MakeableModel

        class HelperClass:
            Config: ClassVar[type[MakeableModel[object]]]
            x: int

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # Should have x: int but NOT Config: ClassVar
    assert "x: int" in content
    assert "Config: ClassVar" not in content


class TestConstantsAndTypeAliases:
  """Tests for constants and type alias handling."""

  def test_constants_use_ellipsis(self, tmp_path: Path) -> None:
    """Test that constants use name: ... format."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        WINDOW_SIZE = 10
        THRESHOLD = 0.75
        MODE = "fast"

        @configurable
        def my_func(x: Hyper[int] = WINDOW_SIZE) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # Constants should use ellipsis, not actual values
    assert "WINDOW_SIZE: ..." in content
    assert "THRESHOLD: ..." in content
    assert "MODE: ..." in content
    # Should NOT have actual values
    assert "= 10" not in content or "int = ..." in content
    assert "= 0.75" not in content
    assert '= "fast"' not in content

  def test_annotated_constants_use_ellipsis(self, tmp_path: Path) -> None:
    """Test that annotated constants use name: type = ... format."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        MAX_SIZE: int = 100
        RATIO: float = 0.5

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "MAX_SIZE: int = ..." in content
    assert "RATIO: float = ..." in content

  def test_type_aliases_preserved(self, tmp_path: Path) -> None:
    """Test that type aliases are preserved with their values."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        MyList = list[int]
        ResultDict = dict[str, list[float]]

        @configurable
        def my_func(x: Hyper[int] = 10) -> ResultDict:
            return {}
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    # Type aliases should preserve the value (needed for type checking)
    assert "MyList = list[int]" in content
    assert "ResultDict = dict[str, list[float]]" in content

  def test_private_constants_excluded(self, tmp_path: Path) -> None:
    """Test that private constants are not included."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        _INTERNAL_VALUE = 42
        PUBLIC_VALUE = 100

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert "_INTERNAL_VALUE" not in content
    assert "PUBLIC_VALUE" in content


class TestIfNameMainExcluded:
  """Tests for excluding if __name__ == '__main__' blocks."""

  def test_if_name_main_excluded(self, tmp_path: Path) -> None:
    """Test that if __name__ == '__main__' blocks are not in stub."""
    source_file = tmp_path / "test.py"
    source_file.write_text(
      dedent("""
        from hipr import configurable, Hyper

        @configurable
        def my_func(x: Hyper[int] = 10) -> int:
            return x

        if __name__ == "__main__":
            result = my_func.Config().make()(10)
            print(result)
      """)
    )

    infos = scan_module(source_file)
    content = generate_stub_content(infos, source_file)

    assert '__name__ == "__main__"' not in content
    assert "__name__" not in content or "def __" in content  # Allow dunder methods
