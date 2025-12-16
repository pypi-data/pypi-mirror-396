import hashlib
import importlib
from typing import Iterable


def import_string(dotted_path: str, reload: bool = False):
    # Lifted from Django, to avoid a dependency if using Varanus outside Django.
    module_path, class_name = dotted_path.rsplit(".", 1)
    try:
        mod = importlib.import_module(module_path)
        if reload:
            mod = importlib.reload(mod)
        return getattr(mod, class_name)
    except AttributeError as err:
        raise ImportError(f"`{module_path}` does not define `{class_name}`") from err


def make_fingerprint(parts: Iterable) -> str:
    return hashlib.sha256(
        ":".join(str(p).strip().lower() for p in parts if p).encode("utf-8")
    ).hexdigest()


def safe_repr(obj, max_length: int = 1024) -> str:
    r = repr(obj)
    if len(r) > max_length:
        r = r[: max_length - 1] + "…"
    return r
