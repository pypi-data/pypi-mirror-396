from __future__ import annotations

import re
import warnings
from collections.abc import Callable, Generator, Hashable, Iterable, Mapping, MutableMapping, Sequence
from typing import Any, Literal, NoReturn, Self, cast, overload, override

import numpy as np
import numpy.typing as npt
import pandas as pd
import pandas._typing as pdt
import zarr
import zarr.abc.store
import zarr.storage
from pandas.core.generic import NDFrame
from pandas.core.internals.array_manager import BaseArrayManager  # pyright: ignore[reportMissingImports, reportUnknownVariableType]
from zarr.codecs import VLenUTF8Codec
from zarr.core.common import AccessModeLiteral
from zarr.core.dtype import VariableLengthUTF8
from zarr.errors import UnstableSpecificationWarning
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

import ezarr
from ezarr.dataframe.manager import EZArrayManager
from ezarr.types import SupportsEZReadWrite


def _get_arrays(
    store: zarr.Group,
    arrays: Iterable[tuple[Hashable, Any]],
    dtypes: Mapping[Hashable, str | np.dtype | type[str | complex | bool | object]],
) -> Generator[zarr.Array, None, None]:
    for name, arr in arrays:
        array = np.asarray(arr)

        if name in dtypes:
            array = array.astype(dtypes[name])

        if array.dtype == object:
            if array.size:
                array = array.astype(type(array.flat[0]))  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

            if array.dtype == object:
                raise TypeError(
                    f'Failed interpreting the "Object" data type to a non ambiguous data type for array {array}'
                )

        if np.issubdtype(array.dtype, np.str_):  # pyright: ignore[reportUnknownArgumentType]
            z_arr = store.create_array(
                str(name), shape=array.shape, dtype=VariableLengthUTF8(), serializer=VLenUTF8Codec()
            )
            z_arr[:] = array
            yield z_arr

        else:
            yield store.create_array(str(name), data=array)


class EZDataFrame(pd.DataFrame, SupportsEZReadWrite):  # EZObject[pd.DataFrame],
    """
    Proxy for pandas DataFrames for storing data in zarr stores.
    """

    _internal_names: list[str] = ["_data_store"] + pd.DataFrame._internal_names  # pyright: ignore[reportAttributeAccessIssue]
    _internal_names_set: set[str] = {"_data_store"} | pd.DataFrame._internal_names_set  # pyright: ignore[reportAttributeAccessIssue]

    _data_store: zarr.Group

    @property
    def _constructor(self) -> Callable[..., EZDataFrame]:
        def inner(df: Any) -> EZDataFrame:
            if not isinstance(df, EZDataFrame):
                raise ValueError("EZDataFrame constructor not properly called")

            return df

        return inner

    def _constructor_from_mgr(self, mgr: BaseArrayManager, axes: list[pd.Index]) -> pd.DataFrame:
        if not isinstance(mgr, EZArrayManager):
            df: pd.DataFrame = pd.DataFrame._from_mgr(mgr, axes=axes)  # pyright: ignore[reportAttributeAccessIssue]

        else:
            df = EZDataFrame._from_mgr(mgr, axes=axes)  # pyright: ignore[reportAttributeAccessIssue]

        if isinstance(self, pd.DataFrame):
            # This would also work `if self._constructor is DataFrame`, but
            #  this check is slightly faster, benefiting the most-common case.
            return df

        elif type(self).__name__ == "GeoDataFrame":
            # Shim until geopandas can override their _constructor_from_mgr
            #  bc they have different behavior for Managers than for DataFrames
            return self._constructor(mgr)

        # We assume that the subclass __init__ knows how to handle a
        #  pd.DataFrame object.
        return self._constructor(df)

    def _constructor_sliced_from_mgr(self, mgr: BaseArrayManager, axes: list[pd.Index[Any]]) -> pd.Series[Any]:
        ser: pd.Series = pd.Series._from_mgr(mgr, axes)  # pyright: ignore[reportAttributeAccessIssue]
        ser._name = None  # caller is responsible for setting real name

        if isinstance(self, pd.DataFrame):
            return ser

        return self._constructor_sliced(ser)

    def __init__(
        self,
        data: pd.DataFrame
        | MutableMapping[Hashable, npt.NDArray[Any] | Sequence[Any]]
        | ezarr.EZDict[Any]
        | npt.NDArray[Any]
        | zarr.Array
        | tuple[EZArrayManager, zarr.Group]
        | None = None,
        index: zarr.Array | pd.Index | None = None,
        columns: zarr.Array | pd.Index | None = None,
        dtypes: Mapping[Hashable, str | np.dtype | type[str | complex | bool | object]] | None = None,
    ):
        match data:
            case ezarr.EZDict():
                assert index is None, (
                    "Cannot provide the `index` parameter when also providing the `data` parameter as EZDict."
                )
                assert columns is None, (
                    "Cannot provide the `columns` parameter when also providing the `data` parameter as EZDict."
                )

                _index: pd.Index = pd.Index(data["index"].copy())
                _columns: pd.Index = pd.Index(data["arrays"].keys())
                arrays: list[zarr.Array] = [arr for arr in data["arrays"].values()]

                store = data.group
                mgr = EZArrayManager(arrays, [_index, _columns], group=store)

            case pd.DataFrame():
                _index = data.index if index is None else pd.Index(np.array(index))
                _columns = data.columns if columns is None else pd.Index(np.array(columns))

                store = zarr.create_group({})
                with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                    arrays = list(_get_arrays(store, data.to_dict(orient="series").items(), dtypes or {}))

                mgr = EZArrayManager(arrays, [_index, _columns], group=store)

            case np.ndarray() | zarr.Array():
                _index = pd.RangeIndex(start=0, stop=data.shape[0]) if index is None else pd.Index(np.array(index))
                _columns = (
                    pd.RangeIndex(start=0, stop=data.shape[1]) if columns is None else pd.Index(np.array(columns))
                )

                store = zarr.create_group({})
                with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                    arrays = list(_get_arrays(store, zip(_columns, np.transpose(np.asarray(data))), dtypes or {}))

                mgr = EZArrayManager(arrays, [_index, _columns], group=store)

            case MutableMapping():
                assert columns is None, (
                    "Cannot provide the `columns` parameter when also providing the `data` parameter as dict."
                )

                _columns = pd.Index(data.keys())

                store = zarr.create_group({})
                arrays = list(_get_arrays(store, data.items(), dtypes or {}))

                _index = pd.RangeIndex(start=0, stop=arrays[0].shape[0]) if index is None else pd.Index(np.array(index))

                mgr = EZArrayManager(arrays, [_index, _columns], group=store)

            case None:
                _index = pd.RangeIndex(0) if index is None else pd.Index(np.array(index))
                _columns = pd.RangeIndex(0) if columns is None else pd.Index(np.array(columns))
                arrays = []

                store = zarr.create_group({})
                mgr = EZArrayManager(arrays, [_index, _columns], group=store)

            case (EZArrayManager() as mgr, zarr.Group() as store):
                pass

            case _:  # pyright: ignore[reportUnnecessaryComparison]
                raise TypeError(f"Invalid type '{type(data)}' for 'data' argument.")  # pyright: ignore[reportUnreachable]

        object.__setattr__(self, "_data_store", store)
        NDFrame.__init__(self, mgr)  # pyright: ignore[reportCallIssue]

    @override
    def __finalize__(self, other: EZDataFrame, method: str | None = None, **kwargs: Any) -> pd.DataFrame:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().__finalize__(other, method, **kwargs)

        if method == "copy":
            return other

        return self

    @staticmethod
    def _get_mode(store: zarr.abc.store.Store) -> str:
        match store:
            case zarr.storage.FsspecStore():
                return "FSSpec"
            case zarr.storage.GpuMemoryStore():
                return "GPU"
            case zarr.storage.LocalStore():
                return "Local"
            case zarr.storage.LoggingStore(store=inner_store):  # pyright: ignore[reportUnknownVariableType]
                return f"Logging:{EZDataFrame._get_mode(inner_store)}"  # pyright: ignore[reportUnknownArgumentType]
            case zarr.storage.MemoryStore():
                return "RAM"
            case zarr.storage.ObjectStore():
                return "Object"
            case zarr.storage.WrapperStore(store=inner_store):  # pyright: ignore[reportUnknownVariableType]
                return f"Wrapper:{EZDataFrame._get_mode(inner_store)}"  # pyright: ignore[reportUnknownArgumentType]
            case zarr.storage.ZipStore():
                return "Zip"
            case _:
                return type(store).__name__

    @override
    def __repr__(self) -> str:
        if self.empty:
            return f"""\
Empty {type(self).__name__}
Columns: {self.columns.tolist()}
Index: {self.index.tolist()}
[{self._get_mode(self._data_store.store)}]"""

        repr_ = repr(self.iloc[:5].copy())
        re.sub(r"\n\n\[.*\]$", "", repr_)
        return (
            repr_
            + ("\n..." if self.shape[1] > 5 else "")
            + f"\n[{self._get_mode(self._data_store.store)}]\n[{len(self.index)} rows x {len(self.columns)} columns]"
        )

    @override
    def __ez_write__(self, values: ezarr.EZDict[Any]) -> None:
        if values.group.store == self._data_store.store:
            return

        _index = self.index.values
        if _index.dtype == object:
            _index = _index.astype(str)

        values["index"] = _index
        values["arrays"] = {str(k): v.values for k, v in self.to_dict(orient="series").items()}
        values["arrays"].attrs["columns_order"] = self.columns.to_list()

    @classmethod
    @override
    def __ez_read__(cls, values: ezarr.EZDict[Any]) -> Self:
        arrays = values["arrays"]
        columns_order = values["arrays"].attrs["columns_order"]
        columns_order_str = np.array(columns_order).astype(str)

        mgr = EZArrayManager(
            [
                arr
                for (_, arr) in sorted(
                    arrays.group.arrays(), key=lambda name_arr: np.where(columns_order_str == name_arr[0])[0][0]
                )
            ],
            [pd.Index(values["index"][:]), pd.Index(columns_order)],
            group=values.group,
        )

        return cls((mgr, values.group))

    @property
    def data(self) -> ezarr.EZDict[Any]:
        return ezarr.EZDict(self._data_store)

    @classmethod
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
        path = f"{path.rstrip('/')}/{name}" if path else name
        return cls.__ez_read__(ezarr.EZDict(zarr.open_group(store, mode=mode, path=path)))

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
        path = f"{path.rstrip('/')}/{name}" if path else name

        if not overwrite:
            mode = "w-"

        self.__ez_write__(ezarr.EZDict(zarr.open_group(store, mode=mode, path=path)))

    @overload
    def sort_values(
        self,
        by: str | Sequence[str],
        *,
        axis: pdt.Axis = ...,
        ascending: bool | list[bool] | tuple[bool, ...] = ...,
        inplace: Literal[False] = ...,
        kind: pdt.SortKind = ...,
        na_position: pdt.NaPosition = ...,
        ignore_index: bool = ...,
        key: pdt.ValueKeyFunc = ...,
    ) -> pd.DataFrame: ...

    @overload
    def sort_values(
        self,
        by: str | Sequence[str],
        *,
        axis: pdt.Axis = ...,
        ascending: bool | list[bool] | tuple[bool, ...] = ...,
        inplace: Literal[True],
        kind: pdt.SortKind = ...,
        na_position: pdt.NaPosition = ...,
        ignore_index: bool = ...,
        key: pdt.ValueKeyFunc = ...,
    ) -> NoReturn: ...

    @override
    def sort_values(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        by: str | Sequence[str],
        *,
        axis: pdt.Axis = 0,
        ascending: bool | list[bool] | tuple[bool, ...] = True,
        inplace: bool = False,
        kind: pdt.SortKind = "quicksort",
        na_position: pdt.NaPosition = "last",
        ignore_index: bool = False,
        key: pdt.ValueKeyFunc | None = None,
    ) -> pd.DataFrame:
        """
        Sort by the values along either axis.

        Parameters
        ----------
        by : str or list of str
            Name or list of names to sort by.

            - if `axis` is 0 or `'index'` then `by` may contain index
              levels and/or column labels.
            - if `axis` is 1 or `'columns'` then `by` may contain column
              levels and/or index labels.
        axis : "{0 or 'index', 1 or 'columns'}", default 0
             Axis to be sorted.
        ascending : bool or list of bool, default True
             Sort ascending vs. descending. Specify list for multiple sort
             orders.  If this is a list of bools, must match the length of
             the by.
        inplace : bool, default False
             If True, perform operation in-place.
        kind : {'quicksort', 'mergesort', 'heapsort', 'stable'}, default 'quicksort'
             Choice of sorting algorithm. See also :func:`numpy.sort` for more
             information. `mergesort` and `stable` are the only stable algorithms. For
             DataFrames, this option is only applied when sorting on a single
             column or label.
        na_position : {'first', 'last'}, default 'last'
             Puts NaNs at the beginning if `first`; `last` puts NaNs at the
             end.
        ignore_index : bool, default False
             If True, the resulting axis will be labeled 0, 1, …, n - 1.
        key : callable, optional
            Apply the key function to the values
            before sorting. This is similar to the `key` argument in the
            builtin :meth:`sorted` function, with the notable difference that
            this `key` function should be *vectorized*. It should expect a
            ``Series`` and return a Series with the same shape as the input.
            It will be applied to each column in `by` independently.

        Returns
        -------
        DataFrame or None
            DataFrame with sorted values or None if ``inplace=True``.

        See Also
        --------
        DataFrame.sort_index : Sort a DataFrame by the index.
        Series.sort_values : Similar method for a Series.

        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'col1': ['A', 'A', 'B', np.nan, 'D', 'C'],
        ...     'col2': [2, 1, 9, 8, 7, 4],
        ...     'col3': [0, 1, 9, 4, 2, 3],
        ...     'col4': ['a', 'B', 'c', 'D', 'e', 'F']
        ... })
        >>> df
          col1  col2  col3 col4
        0    A     2     0    a
        1    A     1     1    B
        2    B     9     9    c
        3  NaN     8     4    D
        4    D     7     2    e
        5    C     4     3    F

        Sort by col1

        >>> df.sort_values(by=['col1'])
          col1  col2  col3 col4
        0    A     2     0    a
        1    A     1     1    B
        2    B     9     9    c
        5    C     4     3    F
        4    D     7     2    e
        3  NaN     8     4    D

        Sort by multiple columns

        >>> df.sort_values(by=['col1', 'col2'])
          col1  col2  col3 col4
        1    A     1     1    B
        0    A     2     0    a
        2    B     9     9    c
        5    C     4     3    F
        4    D     7     2    e
        3  NaN     8     4    D

        Sort Descending

        >>> df.sort_values(by='col1', ascending=False)
          col1  col2  col3 col4
        4    D     7     2    e
        5    C     4     3    F
        2    B     9     9    c
        0    A     2     0    a
        1    A     1     1    B
        3  NaN     8     4    D

        Putting NAs first

        >>> df.sort_values(by='col1', ascending=False, na_position='first')
          col1  col2  col3 col4
        3  NaN     8     4    D
        4    D     7     2    e
        5    C     4     3    F
        2    B     9     9    c
        0    A     2     0    a
        1    A     1     1    B

        Sorting with a key function

        >>> df.sort_values(by='col4', key=lambda col: col.str.lower())
           col1  col2  col3 col4
        0    A     2     0    a
        1    A     1     1    B
        2    B     9     9    c
        3  NaN     8     4    D
        4    D     7     2    e
        5    C     4     3    F

        Natural sort with the key argument,
        using the `natsort <https://github.com/SethMMorton/natsort>` package.

        >>> df = pd.DataFrame({
        ...    "time": ['0hr', '128hr', '72hr', '48hr', '96hr'],
        ...    "value": [10, 20, 30, 40, 50]
        ... })
        >>> df
            time  value
        0    0hr     10
        1  128hr     20
        2   72hr     30
        3   48hr     40
        4   96hr     50
        >>> from natsort import index_natsorted
        >>> df.sort_values(
        ...     by="time",
        ...     key=lambda x: np.argsort(index_natsorted(df["time"]))
        ... )
            time  value
        0    0hr     10
        3   48hr     40
        2   72hr     30
        4   96hr     50
        1  128hr     20
        """
        if inplace:
            raise NotImplementedError

        df = cast(pd.DataFrame, self.copy())
        df.sort_values(
            by,
            axis=axis,
            ascending=ascending,
            inplace=True,
            kind=kind,
            na_position=na_position,
            ignore_index=ignore_index,
            key=key,
        )
        return df
