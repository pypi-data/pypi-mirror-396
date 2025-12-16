from typing import final, override

class DirNamesMixin:
    _accessors: set[str] = set()
    _hidden_attrs: frozenset[str] = frozenset()

    @final
    def _dir_deletions(self) -> set[str]: ...
    def _dir_additions(self) -> set[str]: ...
    @override
    def __dir__(self) -> list[str]: ...
