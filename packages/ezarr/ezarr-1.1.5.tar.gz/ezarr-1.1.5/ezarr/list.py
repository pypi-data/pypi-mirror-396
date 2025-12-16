from __future__ import annotations

from collections.abc import Collection, Iterable, Iterator, MutableSequence
from typing import Any, Self, cast, overload, override
import warnings

import numpy as np
import numpy.typing as npt
from numpy._typing import _SupportsArray as SupportsArray  # pyright: ignore[reportPrivateUsage]
import zarr
from zarr.core.common import AccessModeLiteral
from zarr.errors import BoundsCheckError, UnstableSpecificationWarning
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

from ezarr._repr import repr_element
from ezarr.names import UNKNOWN, Attribute, EZType
from ezarr.object import EZObject
from ezarr.types import DeferredCreationFunc, ListWrapper, PyObject, PyObjectCodec


def deferred_EZList(values: Collection[Any]) -> DeferredCreationFunc:
    def inner(grp: zarr.Group, name: str, overwrite: bool) -> None:
        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            arr = grp.create_array(
                name,
                shape=(len(values),),
                dtype=PyObject(),
                serializer=PyObjectCodec(),
                attributes={Attribute.EZType: EZType.List},
                overwrite=overwrite,
            )
        arr[:] = values  # pyright: ignore[reportArgumentType]

    return inner


class EZList[T](EZObject[list[T]], MutableSequence[T]):
    """
    List-like object built on top of a zarr.Array for storing arbitrary Python objects.

    Args:
        array: a zarr.Array with PyObject() dtype

    Example:
        >>> EZList(zarr.array([1, 2, 3]))
        EZList[1, 2, 3]
    """

    def __init__(self, array: zarr.Array):
        assert array.ndim == 1
        self._array: zarr.Array = array

        self._iter_index: int = 0

    @classmethod
    def from_list(
        cls,
        lst: Collection[T],
        *,
        name: str,
        store: StoreLike | None = None,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> Self:
        """
        Create an EZList from a list-like object.

        Args:
            lst: list-like collection of values to store in an EZList.
            name: name for the EZList, to use inside the store.
            store: Store, path to a directory or name of a zip file.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store where the EZList will be saved.
            overwrite: overwrite object if a group with name `name` already exists ? (default: False)

        Example:
            >>> from pathlib import Path
            >>> data = [1, "some text", Path("/some/path.txt")]
            >>> ez_list = EZList.from_list(data, name="data")
            >>> ez_list
            EZList[1, 'some text', PosixPath('/some/path.txt')]

            >>> ez_list = EZList.from_list([1, [2, 3]], name="data")
            >>> ez_list
            EZList[1, array([2, 3])]
        """
        if store is None:
            store = {}

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            arr = zarr.open_group(store, mode=mode, path=path).create_array(
                name,
                shape=(len(lst),),
                dtype=PyObject(),
                serializer=PyObjectCodec(),
                attributes={Attribute.EZType: EZType.List},
                overwrite=overwrite,
            )
        arr[:] = np.asarray([ListWrapper(e) if isinstance(e, list | SupportsArray) else e for e in lst])  # pyright: ignore[reportUnknownArgumentType]

        return cls(arr)

    def __array__(self, dtype: np.dtype | None = None, copy: bool | None = None) -> npt.NDAarray:
        return self._array[:]

    @override
    def __repr__(self) -> str:
        if len(self) > 6:
            return f"{type(self).__name__}[{repr_element(self[0])}, {repr_element(self[1])}, {repr_element(self[2])}, ..., {repr_element(self[-3])}, {repr_element(self[-2])}, {repr_element(self[-1])}]"

        return f"{type(self).__name__}[{', '.join(repr_element(e) for e in self)}]"

    @override
    def __len__(self) -> int:
        return self._array.shape[0]

    @overload
    def __getitem__(self, item: int) -> T: ...
    @overload
    def __getitem__(self, item: slice[int] | slice[int, int] | slice[int, int, int]) -> Self: ...
    @override
    def __getitem__(self, item: int | slice[int, int, int]) -> T | Self:
        if isinstance(item, slice):
            return type(self)(self._array[item])  # pyright: ignore[reportArgumentType]

        try:
            return cast(T, self._array.get_basic_selection(item)[()])  # pyright: ignore[reportIndexIssue, reportArgumentType, reportCallIssue]

        except BoundsCheckError:
            raise IndexError(
                f"EZList index {item} is out of range [{self._array.shape[0]} ... {self._array.shape[0] - 1}]."
            )

    @overload
    def __setitem__(self, key: int, value: T) -> None: ...
    @overload
    def __setitem__(self, key: slice[int] | slice[int, int] | slice[int, int, int], value: Iterable[T]) -> None: ...
    @override
    def __setitem__(self, key: int | slice[int, int, int], value: T | Iterable[T]) -> None:
        try:
            self._array[key] = np.array(value)

        except BoundsCheckError:
            raise IndexError(
                f"EZList index {key} is out of range [{self._array.shape[0]} ... {self._array.shape[0] - 1}]."
            )

    @override
    def __delitem__(self, key: int | slice[int, int, int]) -> None:
        if isinstance(key, slice):
            raise NotImplementedError

        if key < 0:
            key = len(self) + key

        self._array[key:-1] = self._array[key + 1 :]

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            self._array.resize(self._array.shape[0] - 1)

    @override
    def __iter__(self) -> Iterator[T]:
        self._iter_index = 0
        return self

    def __next__(self) -> T:
        if self._iter_index >= self._array.shape[0]:
            raise StopIteration

        obj = cast(T, self._array.get_basic_selection(self._iter_index)[()])  # pyright: ignore[reportIndexIssue, reportArgumentType, reportCallIssue]
        self._iter_index += 1

        return obj

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, list | SupportsArray):
            return False

        return np.array_equal(self._array[()], other)  # pyright: ignore[reportUnknownArgumentType]

    @classmethod
    @override
    def open(
        cls, store: StoreLike | None = None, *, name: str, mode: AccessModeLiteral = "a", path: str | None = None
    ) -> Self:
        """
        Open this EZList from a store.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZList, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store to open.

        Example:
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")
            >>> ez_list.save("/tmp/list", overwrite=True)
            >>> EZList.open("/tmp/list", name="data")
            EZList[1, 'some text', PosixPath('/some/path.txt')]
        """
        path = f"{path.rstrip('/')}/{name}" if path else name
        arr = zarr.open_array(store, mode=mode, path=path)

        arr_type = cast(str, arr.attrs.get(Attribute.EZType, UNKNOWN))
        if arr_type != EZType.List:
            raise ValueError(f"Cannot read EZList from Array marked with type '{arr_type}', should be 'list'.")

        return cls(arr)

    @override
    def save(
        self,
        store: StoreLike,
        *,
        name: str | None = None,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save this EZList to a local file system.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZList, to use inside the store. (default: same as name used during EZLits creation)
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store where the EZList will be saved.
            overwrite: overwrite EZList if a group with name `name` already exists ? (default: False)

        Example:
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")
            >>> ez_list.save("/tmp/list", overwrite=True)
            >>> Path("/tmp/list").exists()
            True
        """
        if name is None:
            name = self._array.name

        path = f"{path.rstrip('/')}/{name}" if path else name

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            arr = zarr.create_array(
                store=store,
                name=path,
                shape=(self._array.shape[0],),
                dtype=PyObject(),
                serializer=PyObjectCodec(),
                attributes={Attribute.EZType: EZType.List},
                overwrite=overwrite,
            )
        arr[()] = self._array[()]

    @override
    def copy(self) -> list[T]:
        """
        Convert this EZList into a Python list, loading all the data into memory.

        Example:
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")
            >>> ez_list.copy()
            [1, 'some text', PosixPath('/some/path.txt')]
        """
        return self._array[:].tolist()  # pyright: ignore[reportUnknownVariableType, reportAttributeAccessIssue]

    @classmethod
    def defer(cls, values: Collection[Any]) -> DeferredCreationFunc:
        r"""
        Create an EZList from a list-like object, but defer its storage.
        This function returns a function that can be called to finalize the EZList creation and storage,
        with parameters:
            grp: (zarr.Group) a group in which to store the EZList
            name: (str) name for the EZList, to use inside the store.
            overwrite: (bool) overwrite object if a group with name `name` already exists ? (default: False)

        This is usually used as a convenience function to create an EZList in an existing EZDict.

        Args:
            values: list-like collection of values to store in an EZList.

        Example:
            >>> from ezarr import EZDict
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")

            >>> d = EZDict(zarr.open_group({}))
            >>> d["list"] = EZList.defer([1, 2, 3])
            >>> repr(d)
            'EZDict{\n\tlist: EZList[1, 2, 3]\n}'
        """
        return deferred_EZList(values)

    @override
    def append(self, value: T) -> None:
        """
        Append a value to the end of an EZList.

        Args:
            value: value to be appended.

        Example:
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")

            >>> ez_list.append(3.14)
            >>> ez_list
            EZList[1, 'some text', PosixPath('/some/path.txt'), 3.14]

            >>> ez_list.append([1, 2, 3])
            >>> ez_list
            EZList[1, 'some text', PosixPath('/some/path.txt'), 3.14, array([1, 2, 3])]
        """
        if isinstance(value, list | SupportsArray):
            value = ListWrapper(value)  # pyright: ignore[reportAssignmentType, reportUnknownArgumentType]

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            self._array.append(np.asarray([value]))

    @override
    def extend(self, values: Iterable[T]) -> None:
        """
        Append multiple values to the end of an EZList.

        Args:
            values: values to be appended.

        Example:
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")

            >>> ez_list.extend([3.14, 2.71, [-1, -2]])
            >>> ez_list
            EZList[1, 'some text', PosixPath('/some/path.txt'), 3.14, 2.71, array([-1, -2])]
        """
        values_np = np.asarray([ListWrapper(v) if isinstance(v, list | SupportsArray) else v for v in values])  # pyright: ignore[, reportUnknownArgumentType]

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            self._array.append(values_np)

    @override
    def insert(self, index: int, value: T) -> None:
        """
        Insert a value in an EZList before `index`.

        Args:
            value: value to be inserted.

        Example:
            >>> from pathlib import Path
            >>> ez_list = EZList.from_list([1, "some text", Path("/some/path.txt")], name="data")

            >>> ez_list.insert(1, [1, 2, 3])
            >>> ez_list
            EZList[1, array([1, 2, 3]), 'some text', PosixPath('/some/path.txt')]
        """
        if index < 0:
            index = len(self) + index

        if isinstance(value, list | SupportsArray):
            value = ListWrapper(value)  # pyright: ignore[reportAssignmentType, reportUnknownArgumentType]

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            self._array.resize(self._array.shape[0] + 1)
        self._array[index + 1 :] = self._array[index:-1]

        self._array[index] = value  # pyright: ignore[reportArgumentType]
