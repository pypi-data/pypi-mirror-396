import importlib
from pathlib import Path

import pytest

from kaizo import ConfigParser
from kaizo.utils import FnWithKwargs

VAL = 9

false_call_config = """
math_sqrt:
  module: math
  source: sqrt
  call: false
"""

not_callable_py = """
x = 2
"""
not_callable_config = """
local: main.py
not_callable:
  module: local
  source: x
"""

bad_attribute_config = """
math_sqrt:
  module: math
  source: bad_attribute
"""

not_callable_explicit_py = """
class Dummy:
  x = 2
"""
not_callable_explicit_config = """
local: main.py
not_callable:
  module: local
  source: Dummy
  call: x
"""

lazy_call_config = f"""
fn:
  module: math
  source: sqrt
  lazy: true
  args:
    - {VAL}
"""


def test_false_call(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(false_call_config)

    math = importlib.import_module("math")

    parser = ConfigParser(cfg_file)
    out = parser.parse()

    entry = out["math_sqrt"]

    assert entry is math.sqrt


def test_not_callable(tmp_path: Path) -> None:
    module = tmp_path / "main.py"
    module.write_text(not_callable_py)

    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(not_callable_config)

    parser = ConfigParser(cfg_file)

    with pytest.raises(TypeError):
        parser.parse()


def test_bad_attribute(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(bad_attribute_config)

    parser = ConfigParser(cfg_file)

    with pytest.raises(AttributeError):
        parser.parse()


def test_not_callable_explicit(tmp_path: Path) -> None:
    module = tmp_path / "main.py"
    module.write_text(not_callable_explicit_py)

    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(not_callable_explicit_config)

    parser = ConfigParser(cfg_file)

    with pytest.raises(TypeError):
        parser.parse()


def test_lazy_call(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(lazy_call_config)

    parser = ConfigParser(cfg_file)
    out = parser.parse()

    entry = out["fn"]
    assert isinstance(entry, FnWithKwargs)

    assert entry() == VAL**0.5
