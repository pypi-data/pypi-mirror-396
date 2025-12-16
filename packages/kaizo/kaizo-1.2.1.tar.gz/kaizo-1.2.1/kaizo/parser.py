import importlib
import os
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from .plugins import Plugin, PluginMetadata
from .utils import (
    DictEntry,
    Entry,
    FieldEntry,
    FnWithKwargs,
    ListEntry,
    ModuleEntry,
    extract_variable,
)


class ConfigParser:
    config: dict[str]
    local: ModuleType | None
    variables: DictEntry[str]
    kwargs: dict[str]
    modules: dict[str, "ConfigParser"] | None
    plugins: dict[str, FnWithKwargs[Plugin]] | None

    def __init__(self, config_path: str | Path, kwargs: dict[str] | None = None) -> None:
        root, _ = os.path.split(config_path)

        root = Path(root)

        self.variables = DictEntry(resolve=False)
        self.kwargs = kwargs or {}

        with Path.open(config_path) as file:
            self.config = yaml.safe_load(file)

        if "local" in self.config:
            local_path = Path(self.config.pop("local"))

            if not local_path.is_absolute():
                local_path = root / local_path

            self.local = self._load_python_module(local_path)
        else:
            self.local = None

        if "import" in self.config:
            modules = self.config.pop("import")

            if not isinstance(modules, dict):
                msg = f"import module should be a dict, got {type(modules)}"
                raise TypeError(msg)

            self.modules = self._import_modules(root, modules, kwargs)
        else:
            self.modules = None

        if "plugins" in self.config:
            plugins = self.config.pop("plugins")

            if not isinstance(plugins, dict):
                msg = f"plugins should be a dict, got {type(plugins)}"
                raise TypeError(msg)

            self.plugins = self._import_plugins(plugins)
        else:
            self.plugins = None

    def _load_python_module(self, path: Path) -> ModuleType:
        if not path.is_file():
            msg = f"Local Python file not found: {path}"
            raise FileNotFoundError(msg)

        module_name = path.stem
        spec = spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            msg = f"Failed to load module from: {path}"
            raise ImportError(msg)

        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _import_modules(
        self,
        root: Path,
        modules: dict[str, str],
        kwargs: dict[str] | None = None,
    ) -> dict[str, "ConfigParser"]:
        module_dict = {}

        for module_name, module_path_str in modules.items():
            module_path = Path(module_path_str)

            if not module_path.is_absolute():
                module_path = root / module_path

            parser = ConfigParser(module_path, kwargs)
            parser.parse()

            module_dict[module_name] = parser

        return module_dict

    def _import_plugins(
        self,
        plugins: dict[str],
    ) -> dict[str, FnWithKwargs[Plugin]]:
        metadata = PluginMetadata()
        plugin_dict = {}

        for plugin_name, plugin_module in plugins.items():
            plugin_path = f"kaizo.plugins.{plugin_name}"

            if isinstance(plugin_module, dict):
                source = plugin_module.get("source")
                args = plugin_module.get("args", {})

                resolved_args = self._resolve_args(plugin_name, args)
                metadata.args = resolved_args

                if source is None:
                    msg = f"source is required for {plugin_name} plugin"
                    raise ValueError(msg)

                plugin = self._load_object(plugin_path, source)

            elif isinstance(plugin_module, str):
                plugin = self._load_object(plugin_path, plugin_module)

            else:
                msg = f"plugin {plugin_name} is not a valid type"
                raise TypeError(msg)

            if not issubclass(plugin, Plugin):
                msg = f"loaded {plugin_name} is not a `Plugin`"
                raise TypeError(msg)

            obj = FnWithKwargs[Plugin](fn=plugin.dispatch, kwargs={"metadata": metadata})

            plugin_dict[plugin_name] = obj

        return plugin_dict

    def _load_object(self, module_path: str, object_name: str) -> Any:
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, object_name):
                msg = f"Module '{module_path}' has no attribute '{object_name}'"
                raise AttributeError(msg)
            return getattr(module, object_name)
        except ModuleNotFoundError as e:
            msg = f"Could not import module '{module_path}': {e}"
            raise ImportError(msg) from e

    def _load_symbol_from_module(self, module_path: str, symbol_name: str) -> Any:
        if module_path == "local":
            if self.local is None:
                msg = "local module is not given"
                raise ValueError(msg)

            return getattr(self.local, symbol_name)

        if module_path == "plugin":
            if self.plugins is None:
                msg = "plugins are not given"
                raise ValueError(msg)

            obj = self.plugins.get(symbol_name)

            if obj is None:
                msg = f"plugin {symbol_name} not found"
                raise ValueError(msg)

            return obj.__call__()

        return self._load_object(module_path, symbol_name)

    def _resolve_string(self, key: str, entry: str) -> Entry:
        entry_key, entry_value = extract_variable(entry)

        if entry_key is None:
            return FieldEntry(key=key, value=entry)

        if not entry_key:
            if entry_value in self.kwargs:
                return FieldEntry(key=entry_value, value=self.kwargs[entry_value])

            parsed_entry = self.variables.get(entry_value)

        else:
            if self.modules is None:
                msg = "import module is not given"
                raise ValueError(msg)

            module = self.modules.get(entry_key)

            if module is None:
                msg = f"keyword not found, got {entry_key}"
                raise ValueError(msg)

            parsed_entry = module.variables.get(entry_value)

        if parsed_entry is None:
            msg = f"entry not found, got {entry_value}"
            raise KeyError(msg)

        return parsed_entry

    def _resolve_list(self, key: str, entry: list) -> FieldEntry[list]:
        return FieldEntry(
            key=key,
            value=ListEntry([self._resolve_entry(key, e) for e in entry]),
        )

    def _resolve_args(self, key: str, args: Any) -> DictEntry[str] | ListEntry:
        if isinstance(args, dict):
            resolved = DictEntry()
            for k, v in args.items():
                value = (
                    FieldEntry(key=key, value=self.kwargs[k])
                    if k in self.kwargs
                    else self._resolve_entry(key, v)
                )

                resolved[k] = value
                self.variables[k] = value

        if isinstance(args, list):
            resolved = ListEntry()
            for v in args:
                resolved.append(self._resolve_entry(key, v))

        return resolved

    def _resolve_dict(self, key: str, entry: dict[str]) -> Entry:
        module_path = entry.get("module")
        symbol_name = entry.get("source")

        if module_path is None or symbol_name is None:
            return FieldEntry(
                key=key,
                value=DictEntry({k: self._resolve_entry(key, v) for k, v in entry.items()}),
            )

        call = entry.get("call", True)
        lazy = entry.get("lazy", False)
        args = entry.get("args", {})
        cache = entry.get("cache", True)

        obj = self._load_symbol_from_module(module_path, symbol_name)

        resolved_args = self._resolve_args(key, args)

        return ModuleEntry(
            key=key,
            obj=obj,
            call=call,
            lazy=lazy,
            args=resolved_args,
            cache=cache,
        )

    def _resolve_entry(self, key: str, entry: Any) -> Entry:
        if isinstance(entry, str):
            return self._resolve_string(key, entry)

        if isinstance(entry, list):
            return self._resolve_list(key, entry)

        if isinstance(entry, dict):
            return self._resolve_dict(key, entry)

        return FieldEntry(key=key, value=entry)

    def parse(self) -> DictEntry[str]:
        res = DictEntry()

        for k in self.config:
            value = self._resolve_entry(k, self.config[k])

            res[k] = value
            self.variables[k] = value

        return res
