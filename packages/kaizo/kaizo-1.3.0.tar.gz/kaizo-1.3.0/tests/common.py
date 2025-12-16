import importlib
import shutil
import sys
from pathlib import Path


def create_fake_plugin(tmp_path: Path, name: str, body: str) -> Path:
    real_kaizo = importlib.import_module("kaizo")

    real_kaizo_path = Path(real_kaizo.__file__).parent

    dest_path = tmp_path / "kaizo"

    shutil.copytree(real_kaizo_path, dest_path)

    plugins_dir = dest_path / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)

    plugin_file = plugins_dir / f"{name}.py"
    plugin_file.write_text(body)

    if str(tmp_path) in sys.path:
        sys.path.remove(str(tmp_path))
    sys.path.insert(0, str(tmp_path))

    for mod in list(sys.modules):
        if mod == "kaizo" or mod.startswith("kaizo."):
            del sys.modules[mod]

    importlib.invalidate_caches()

    return plugin_file
