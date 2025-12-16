from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `expandai.resources` module.

    This is used so that we can lazily import `expandai.resources` only when
    needed *and* so that users can just import `expandai` and reference `expandai.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("expandai.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
