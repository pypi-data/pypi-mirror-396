import importlib


def test_plugin_importable() -> None:
    hf = importlib.import_module("kaizo.plugins.hf")

    assert hf
