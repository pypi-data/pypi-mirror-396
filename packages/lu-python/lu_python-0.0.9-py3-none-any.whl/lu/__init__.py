import os
import json
import importlib
import functools
import inspect
from typing import Dict, Any, Optional, List, Tuple
from .id import make_deterministic_id, make_deterministic_dict, method_args
from .io import _write_compressed_pickle, _read_compressed_pickle, _COMPRESSOR

try:
    import yaml
except ImportError:
    yaml = None


def parse_target(target: str) -> Tuple[Any, str]:
    parts = target.split('.')

    # Find the longest importable module prefix.
    module = None
    importable_index = 0
    for i in range(len(parts), 0, -1):
        module_path = '.'.join(parts[:i])
        try:
            module = importlib.import_module(module_path)
            importable_index = i
            break
        except ModuleNotFoundError:
            continue

    if module is None:
        raise ImportError(f"Could not import any prefix of target '{target}'")

    # Traverse remaining attribute names to reach the parent of the final attribute.
    parent = module
    for name in parts[importable_index:-1]:
        parent = getattr(parent, name)

    func_name = parts[-1]
    return parent, func_name


class Recorder:
    """Context manager that installs recording wrappers and writes a manifest
    at exit.
    """

    def __init__(self, targets: Dict[str, Any], recordings_dir: str, manifest_file: Optional[str] = None, short_hex_length: Optional[int] = None):
        self.targets = targets
        self.recordings_dir = recordings_dir
        self.manifest_file = manifest_file or os.path.join(recordings_dir, "recordings.json")
        self._originals = []  # list of tuples (parent, func_name, original_obj)
        self._manifest_entries: Dict[str, Any] = {}
        self.short_hex_length = short_hex_length

    def __enter__(self):
        os.makedirs(self.recordings_dir, exist_ok=True)

        for target, keys in self.targets.items():
            parent, func_name = parse_target(target)
            original_func_obj = getattr(parent, func_name)

            # Save original so we can restore on exit
            self._originals.append((parent, func_name, original_func_obj))

            # extract positional arg names and whether callable expects 'self'
            args_names, expects_self = method_args(original_func_obj)

            # create and install wrapper; bind variables into defaults to avoid late-binding
            def make_wrapper(__original=original_func_obj, _target=target, _keys=keys, _args_names=args_names, _expects_self=expects_self):
                # helper that builds call metadata
                def _build_meta(w_args, kwargs):
                    if _expects_self:
                        obj, *call_args = w_args
                        key_self = {k: v for k, v in obj.__dict__.items() if k in (_keys or [])}
                    else:
                        obj = None
                        call_args = list(w_args)
                        key_self = {}

                    key_args = {name:arg for name, arg in zip(_args_names, call_args) if name in (_keys or [])}
                    key_kwargs = {k: v for k, v in kwargs.items() if k in (_keys or [])}

                    params = key_self | key_args | key_kwargs  # consolidate all the params

                    entry_payload = make_deterministic_dict(_target, params)
                    entry_id = make_deterministic_id(_target, params, short_hex_length=self.short_hex_length)
                    ext = ".zst" if _COMPRESSOR == "zstd" else ".pkl.gz"
                    recording_file = os.path.join(self.recordings_dir, f"{entry_id}{ext}")

                    return obj, call_args, entry_payload, entry_id, recording_file

                async_flag = inspect.iscoroutinefunction(__original)

                # shared logic to handle existing recording or perform original call
                async def _handle_async(obj, call_args, kwargs, entry_payload, entry_id, recording_file):
                    if os.path.exists(recording_file):
                        loaded = _read_compressed_pickle(recording_file)
                        if isinstance(loaded, Exception):
                            self._set_entry(entry_id, _target, entry_payload, recording_file, is_exception=True)
                            raise loaded
                        return loaded

                    try:
                        if obj is not None:
                            result = await __original(obj, *call_args, **kwargs)
                        else:
                            result = await __original(*call_args, **kwargs)
                        _write_compressed_pickle(result, recording_file)
                        return result
                    except Exception as exc:
                        _write_compressed_pickle(exc, recording_file)
                        self._set_entry(entry_id, _target, entry_payload, recording_file, is_exception=True)
                        raise

                def _handle_sync(obj, call_args, kwargs, entry_payload, entry_id, recording_file):
                    if os.path.exists(recording_file):
                        loaded = _read_compressed_pickle(recording_file)
                        if isinstance(loaded, Exception):
                            self._set_entry(entry_id, _target, entry_payload, recording_file, is_exception=True)
                            raise loaded
                        return loaded

                    try:
                        if obj is not None:
                            result = __original(obj, *call_args, **kwargs)
                        else:
                            result = __original(*call_args, **kwargs)
                        _write_compressed_pickle(result, recording_file)
                        return result
                    except Exception as exc:
                        _write_compressed_pickle(exc, recording_file)
                        self._set_entry(entry_id, _target, entry_payload, recording_file, is_exception=True)
                        raise

                if async_flag:
                    @functools.wraps(__original)
                    async def wrapper(*w_args, **kwargs):
                        obj, call_args, entry_payload, entry_id, recording_file = _build_meta(w_args, kwargs)
                        result = await _handle_async(obj, call_args, kwargs, entry_payload, entry_id, recording_file)
                        self._set_entry(entry_id, _target, entry_payload, recording_file, is_exception=False)
                        return result

                    return wrapper
                else:
                    @functools.wraps(__original)
                    def wrapper(*w_args, **kwargs):
                        obj, call_args, entry_payload, entry_id, recording_file = _build_meta(w_args, kwargs)
                        result = _handle_sync(obj, call_args, kwargs, entry_payload, entry_id, recording_file)
                        self._set_entry(entry_id, _target, entry_payload, recording_file, is_exception=False)
                        return result

                    return wrapper

            wrapper = make_wrapper()
            setattr(parent, func_name, wrapper)

        return self

    def __exit__(self, exc_type, exc, tb):
        # restore originals
        for parent, func_name, original in self._originals:
            setattr(parent, func_name, original)

        # write manifest file by merging with what is already existing
        try:
            # Load existing manifest (if any) and merge entries, then write back.
            existing: Dict = {}
            if os.path.exists(self.manifest_file):
                try:
                    with open(self.manifest_file, 'r', encoding='utf-8') as mf:
                        loaded = json.load(mf)
                        if isinstance(loaded, dict):
                            existing = loaded
                except Exception:
                    # If the existing file is unreadable or malformed, ignore and overwrite
                    existing = {}

            # Update existing with current session entries (current entries take precedence)
            existing.update(self._manifest_entries)

            with open(self.manifest_file, 'w', encoding='utf-8') as mf:
                json.dump(existing, mf, indent=2, sort_keys=True, ensure_ascii=False)
        except Exception:
            # don't raise in __exit__; let test framework handle other exceptions
            pass


    def _set_entry(self, entry_id, _target, entry_payload, recording_file, is_exception):
        self._manifest_entries[entry_id] = {
            "target": _target,
            "params": entry_payload.get("params"),
            "file": recording_file,
            "format": "compressed_pickle",
            "compressor": _COMPRESSOR,
            "exception": is_exception,
        }


def record(targets: Dict[str, List[str]], recordings_dir: str, manifest_file: Optional[str] = None, short_hex_length: int = 6) -> Recorder:
    """Create and return a :class:`Recorder` context manager.

    Args:
        targets (Dict[str, List[str]]): Mapping from a dotted target string
            (e.g. ``'package.module.Class.method'``) to a list of argument
            names that should be considered when building the deterministic
            recording id.
        recordings_dir (str): Path to the directory where recordings and the
            manifest file will be written.
        manifest_file (Optional[str]): Optional path for the manifest JSON
            file. If ``None``, defaults to ``<recordings_dir>/recordings.json``.
        short_hex_length (int): Length for the shortened deterministic id
            hex component (controls filename length).

    Returns:
        Recorder: An instance of :class:`Recorder` which may be used as a
            context manager.

    Example:

        with record(targets, recordings_dir):
            # target code that will be recorded/replayed
            ...
    """
    return Recorder(targets, recordings_dir, manifest_file, short_hex_length)


def record2(yaml_file = 'lu.yaml') -> Recorder:
    """Create and return a :class:`Recorder` context manager from a YAML configuration file.

    Reads recording parameters from 'lu.yaml' and creates a Recorder instance.

    The YAML file should have the following structure:

    .. code-block:: yaml

        targets:
          package.module.Class.method: [arg1, arg2]
          package.module.function: null
        recordings_dir: path/to/recordings
        manifest_file: path/to/manifest.json  # optional
        short_hex_length: 6  # optional

    Returns:
        Recorder: An instance of :class:`Recorder` which may be used as a
            context manager.

    Raises:
        ImportError: If PyYAML is not installed.
        FileNotFoundError: If 'lu.yaml' does not exist.

    Example:

        with record2():
            # target code that will be recorded/replayed
            ...
    """

    if yaml is None:
        raise ImportError("PyYAML is required to use record2(). Install it with: pip install pyyaml")

    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"YAML configuration file not found: {yaml_file}")

    with open(yaml_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        return record(**config)

