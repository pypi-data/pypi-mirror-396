from pathlib import Path

from kaizo import ConfigParser

cache_py = """
num_call = 0
def fn():
    global num_call

    num_call+=1
    return num_call
"""

cache_config = """
local: main.py
with_cache:
  module: local
  source: fn
  cache: true
without_cache:
  module: local
  source: fn
  cache: false
"""


def test_cache(tmp_path: Path) -> None:
    module = tmp_path / "main.py"
    module.write_text(cache_py)

    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(cache_config)

    parser = ConfigParser(cfg_file)
    out = parser.parse()

    with_cache_1 = out["with_cache"]
    with_cache_2 = out["with_cache"]
    without_cache_1 = out["without_cache"]
    without_cache_2 = out["without_cache"]

    assert with_cache_1 == with_cache_2
    assert without_cache_2 == without_cache_1 + 1
