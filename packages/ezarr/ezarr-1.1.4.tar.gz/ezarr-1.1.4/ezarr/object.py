from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from zarr.core.common import AccessModeLiteral
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]


class EZObject[PythonType](ABC):
    @classmethod
    @abstractmethod
    def open(
        cls, store: StoreLike | None = None, *, name: str, mode: AccessModeLiteral = "a", path: str | None = None
    ) -> Self:
        """
        Open this object from a store.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the object, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store to open.
        """

    @abstractmethod
    def save(
        self,
        store: StoreLike,
        *,
        name: str,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save this object to a local file system.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the object, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store where the object will be saved.
            overwrite: overwrite object if a group with name `name` already exists ? (default: False)
        """

    @abstractmethod
    def copy(self) -> PythonType:
        """
        Convert this object into its Python equivalent, loading all the data into memory.
        """
        pass
