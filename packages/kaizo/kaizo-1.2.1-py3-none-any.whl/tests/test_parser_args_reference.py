from pathlib import Path

from kaizo import ConfigParser

VAL = 4

config = """
val: {VAL}
use_args:
  module: math
  source: sqrt
  call: true
  args:
    - .{val}
"""


def test_args_reference(tmp_path: Path) -> None:
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(
        config.format(
            VAL=VAL,
            val="{val}",
        )
    )

    parser = ConfigParser(cfg_file)
    out = parser.parse()

    assert out["val"] == VAL
    assert out["use_args"] == VAL**0.5
