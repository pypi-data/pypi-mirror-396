from pathlib import Path

from kaizo import ConfigParser

X = 5

config = """
call_me:
  module: math
  source: pow
  call: true
  args:
    - .{injected}
    - 2
"""


def test_kwargs_injection(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(config)

    parser = ConfigParser(cfg_file, kwargs={"injected": X})
    out = parser.parse()
    assert out["call_me"] == X**2
