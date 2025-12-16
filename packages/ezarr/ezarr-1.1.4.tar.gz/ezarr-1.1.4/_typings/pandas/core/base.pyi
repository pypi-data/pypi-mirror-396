from typing import Any, Self, override
from pandas.core.accessor import DirNamesMixin

class PandasObject(DirNamesMixin):
    """
    Baseclass for various pandas objects.
    """

    _cache: dict[str, Any]

    @property
    def _constructor(self) -> Self: ...
    @override
    def __repr__(self) -> str: ...
    def _reset_cache(self, key: str | None = None) -> None: ...
    @override
    def __sizeof__(self) -> int: ...
