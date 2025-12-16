from pathlib import Path
from textwrap import dedent

from hipr.stubs.generator import generate_stub_content
from hipr.stubs.scanner import scan_module


def test_generate_stub_content_copies_imports(tmp_path: Path):
  """Test that imports are copied from source to stub."""
  source_file = tmp_path / "imports_test.py"
  source_file.write_text(
    dedent(
      """
        import numpy as np
        from typing import List, Optional
        from my_module import MyType
        from hipr import configurable, Hyper

        @configurable
        def my_func(
            x: Hyper[int] = 10,
            y: Optional[List[MyType]] = None
        ) -> np.ndarray:
            return np.array([x])
    """
    )
  )

  functions = scan_module(source_file)
  content = generate_stub_content(functions, source_file)

  # Check that imports are present
  assert "import numpy as np" in content
  assert "from typing import List, Optional" in content
  assert "from my_module import MyType" in content

  # Check that hipr imports are handled correctly
  assert "from hipr import MakeableModel" in content
