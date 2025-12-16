from __future__ import annotations

from contextlib import AbstractContextManager, contextmanager
import itertools as it
import warnings
from collections.abc import ItemsView, Iterator, Mapping, MutableMapping
from typing import Any, Literal, NotRequired, Self, TypedDict, cast, override

import numpy as np
import numpy.typing as npt
import zarr
from numpy._typing import _SupportsArray as SupportsArray  # pyright: ignore[reportPrivateUsage]
from zarr.core.array import DEFAULT_FILL_VALUE, CompressorsLike, FiltersLike, SerializerLike, ShardsLike
from zarr.core.array_spec import ArrayConfigLike
from zarr.core.attributes import Attributes
from zarr.core.chunk_key_encodings import ChunkKeyEncodingLike
from zarr.core.common import JSON, AccessModeLiteral, DimensionNames, MemoryOrder, ShapeLike
from zarr.core.dtype import ZDTypeLike
from zarr.errors import UnstableSpecificationWarning
from zarr.storage import StoreLike  # pyright: ignore[reportUnknownVariableType]

import ezarr
from ezarr import io
from ezarr._repr import repr_element
from ezarr.object import EZObject

type DictData[T] = Mapping[str, int | float | np.integer | np.floating | list[Any] | npt.ArrayLike | DictData[T]]
type GroupItems = ItemsView[str, zarr.Group | zarr.Array]


class DictParameters(TypedDict):
    compressors: NotRequired[CompressorsLike]


@contextmanager
def ParametersManager(ez_dict: EZDict[Any], parameters: DictParameters):
    original_parameters = ez_dict.get_parameters()
    ez_dict.set_parameters(parameters)
    try:
        yield

    finally:
        ez_dict.set_parameters(original_parameters)


class EZDict[T](EZObject[dict[str, T]], MutableMapping[str, T]):
    """
    Dict-like object wrapping a zarr.Group for storing arbitrary Python objects

    Args:
        group: a zarr.Group

    Example:
        >>> EZDict(zarr.open_group({}))
        EZDict{}
    """

    __match_args__: tuple[str] = ("_group",)

    def __init__(self, group: zarr.Group) -> None:
        self._group: zarr.Group = group

        self._parameters: DictParameters = DictParameters()

    @classmethod
    def from_dict(
        cls,
        dct: Mapping[str, Any],
        *,
        name: str = "",
        store: StoreLike | None = None,
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> Self:
        r"""
        Create an EZDict from a regular in-memory Python dictionary.

        Args:
            dct: dictionary with arbitrary data to store.
            name: name for the EZDict, to use inside the store.
            store: Store or path to directory in file system or nam of zip file.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: Group path within store.
            overwrite: overwrite object if a group with name `name` already exists ? (default: False)

        Example:
            >>> data = {"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}}
            >>> ez_dict = EZDict.from_dict(data)
            >>> repr(ez_dict)
            'EZDict{\n\ta: 1,\n\tb: [1 2 3],\n\tc: {...}\n}'
        """
        if store is None:
            store = {}

        grp = zarr.open_group(store, mode=mode, path=path)

        if name:
            grp = grp.create_group(name, overwrite=overwrite)

        to_visit: list[tuple[Any, str, str]] = [(dct[k], k, "") for k in dct.keys()]

        while len(to_visit):
            value, name_, path_ = to_visit.pop()

            if isinstance(value, Mapping):
                to_visit.extend([(value[k], k, f"{path_}/{name_}" if path_ else name_) for k in value.keys()])  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]

            elif isinstance(value, list | SupportsArray):
                grp.require_group(path_).create_array(name_, data=np.asarray(value), overwrite=overwrite)  # pyright: ignore[reportUnknownArgumentType]

            else:
                io.write_object(grp, obj=value, name=name_, path=path_, overwrite=overwrite)

        return cls(grp)

    @staticmethod
    def _repr(grp: zarr.Group) -> str:
        if not len(grp):
            return "{}"

        if len(grp) > 100:
            return (
                "{\n\t"
                + ",\n\t".join(
                    [
                        f"{name}: {repr_element(io.read_object(grp, name=name), prefix=f'\t{" " * len(name)}  ')}"
                        for name in it.islice(sorted(grp.keys()), 0, 10)
                    ]
                )
                + ",\n\t...,\n\t"
                + ",\n\t".join(
                    [
                        f"{name}: {repr_element(io.read_object(grp, name=name), prefix=f'\t{" " * len(name)}  ')}"
                        for name in it.islice(sorted(grp.keys()), len(grp) - 10, None)
                    ]
                )
                + "}"
            )

        return (
            "{\n\t"
            + ",\n\t".join(
                [
                    f"{name}: {repr_element(io.read_object(grp, name=name), prefix=f'\t{" " * len(name)}  ')}"
                    for name in sorted(grp.keys())
                ]
            )
            + "\n}"
        )

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}{self._repr(self._group)}"

    @override
    def __len__(self) -> int:
        return len(self._group)

    @override
    def __getitem__(self, key: str, /) -> T:
        return io.read_object(self._group, name=key)

    def __matmul__(self, key: str) -> EZDict[T] | zarr.Array:
        """Get raw Group/Array objects from this EZDict"""
        res = self._group[key]

        if isinstance(res, zarr.Group):
            return EZDict(res)

        return res

    @override
    def __setitem__(self, key: str, value: T, /) -> None:
        if key in self:
            try:
                # try to compare values, might fail when comparing arrays with different shapes
                if self[key] == value:
                    return

            except ValueError:
                pass

        with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
            io.write_object(self._group, obj=value, name=key, overwrite=True)

    @override
    def __delitem__(self, key: str, /) -> None:
        del self._group[key]

    @override
    def __iter__(self) -> Iterator[str]:
        yield from sorted(self._group.keys())

    def __deepcopy__(self, _memo: dict[Any, Any]) -> dict[str, Any]:
        return self.copy()

    def __ior__(self, other: object) -> EZDict[T]:
        if not isinstance(other, Mapping):
            raise NotImplementedError

        other = cast(Mapping[str, T], other)
        for name, value in other.items():
            if isinstance(value, Mapping):
                grp = self._group.require_group(name)
                EZDict(grp).__ior__(value)  # pyright: ignore[reportUnknownArgumentType]

            else:
                with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                    self[name] = value

        return self

    @property
    def attrs(self) -> Attributes:
        return self._group.attrs

    @property
    def group(self) -> zarr.Group:
        return self._group

    def get_parameters(self) -> DictParameters:
        return self._parameters

    def set_parameters(self, params: DictParameters) -> None:
        self._parameters = params

    def parameters(self, compressors: CompressorsLike = None) -> AbstractContextManager[None]:
        return ParametersManager(self, DictParameters(compressors=compressors))

    def create_array(
        self,
        name: str,
        *,
        shape: ShapeLike | None = None,
        dtype: ZDTypeLike | None = None,
        data: np.ndarray[Any, np.dtype[Any]] | None = None,
        chunks: tuple[int, ...] | Literal["auto"] = "auto",
        shards: ShardsLike | None = None,
        filters: FiltersLike = "auto",
        compressors: CompressorsLike = "auto",
        serializer: SerializerLike = "auto",
        fill_value: Any | None = DEFAULT_FILL_VALUE,
        order: MemoryOrder | None = None,
        attributes: dict[str, JSON] | None = None,
        chunk_key_encoding: ChunkKeyEncodingLike | None = None,
        dimension_names: DimensionNames = None,
        storage_options: dict[str, Any] | None = None,
        overwrite: bool = False,
        config: ArrayConfigLike | None = None,
        write_data: bool = True,
    ) -> zarr.Array:
        """Direct array creation interface.

        Args:
            name : str
                The name of the array relative to the group. If ``path`` is ``None``, the array will be located
                at the root of the store.
            shape : ShapeLike, optional
                Shape of the array. Must be ``None`` if ``data`` is provided.
            dtype : npt.DTypeLike | None
                Data type of the array. Must be ``None`` if ``data`` is provided.
            data : Array-like data to use for initializing the array. If this parameter is provided, the
                ``shape`` and ``dtype`` parameters must be ``None``.
            chunks : tuple[int, ...], optional
                Chunk shape of the array.
                If not specified, default are guessed based on the shape and dtype.
            shards : tuple[int, ...], optional
                Shard shape of the array. The default value of ``None`` results in no sharding at all.
            filters : Iterable[Codec] | Literal["auto"], optional
                Iterable of filters to apply to each chunk of the array, in order, before serializing that
                chunk to bytes.

                For Zarr format 3, a "filter" is a codec that takes an array and returns an array,
                and these values must be instances of :class:`zarr.abc.codec.ArrayArrayCodec`, or a
                dict representations of :class:`zarr.abc.codec.ArrayArrayCodec`.

                For Zarr format 2, a "filter" can be any numcodecs codec; you should ensure that the
                the order if your filters is consistent with the behavior of each filter.

                The default value of ``"auto"`` instructs Zarr to use a default used based on the data
                type of the array and the Zarr format specified. For all data types in Zarr V3, and most
                data types in Zarr V2, the default filters are empty. The only cases where default filters
                are not empty is when the Zarr format is 2, and the data type is a variable-length data type like
                :class:`zarr.dtype.VariableLengthUTF8` or :class:`zarr.dtype.VariableLengthUTF8`. In these cases,
                the default filters contains a single element which is a codec specific to that particular data type.

                To create an array with no filters, provide an empty iterable or the value ``None``.
            compressors : Iterable[Codec], optional
                List of compressors to apply to the array. Compressors are applied in order, and after any
                filters are applied (if any are specified) and the data is serialized into bytes.

                For Zarr format 3, a "compressor" is a codec that takes a bytestream, and
                returns another bytestream. Multiple compressors my be provided for Zarr format 3.
                If no ``compressors`` are provided, a default set of compressors will be used.
                These defaults can be changed by modifying the value of ``array.v3_default_compressors``
                in :mod:`zarr.core.config`.
                Use ``None`` to omit default compressors.

                For Zarr format 2, a "compressor" can be any numcodecs codec. Only a single compressor may
                be provided for Zarr format 2.
                If no ``compressor`` is provided, a default compressor will be used.
                in :mod:`zarr.core.config`.
                Use ``None`` to omit the default compressor.
            serializer : dict[str, JSON] | ArrayBytesCodec, optional
                Array-to-bytes codec to use for encoding the array data.
                Zarr format 3 only. Zarr format 2 arrays use implicit array-to-bytes conversion.
                If no ``serializer`` is provided, a default serializer will be used.
                These defaults can be changed by modifying the value of ``array.v3_default_serializer``
                in :mod:`zarr.core.config`.
            fill_value : Any, optional
                Fill value for the array.
            order : {"C", "F"}, optional
                The memory of the array (default is "C").
                For Zarr format 2, this parameter sets the memory order of the array.
                For Zarr format 3, this parameter is deprecated, because memory order
                is a runtime parameter for Zarr format 3 arrays. The recommended way to specify the memory
                order for Zarr format 3 arrays is via the ``config`` parameter, e.g. ``{'config': 'C'}``.
                If no ``order`` is provided, a default order will be used.
                This default can be changed by modifying the value of ``array.order`` in :mod:`zarr.core.config`.
            attributes : dict, optional
                Attributes for the array.
            chunk_key_encoding : ChunkKeyEncoding, optional
                A specification of how the chunk keys are represented in storage.
                For Zarr format 3, the default is ``{"name": "default", "separator": "/"}}``.
                For Zarr format 2, the default is ``{"name": "v2", "separator": "."}}``.
            dimension_names : Iterable[str], optional
                The names of the dimensions (default is None).
                Zarr format 3 only. Zarr format 2 arrays should not use this parameter.
            storage_options : dict, optional
                If using an fsspec URL to create the store, these will be passed to the backend implementation.
                Ignored otherwise.
            overwrite : bool, default False
                Whether to overwrite an array with the same name in the store, if one exists.
            config : ArrayConfig or ArrayConfigLike, optional
                Runtime configuration for the array.
            write_data : bool
                If a pre-existing array-like object was provided to this function via the ``data`` parameter
                then ``write_data`` determines whether the values in that array-like object should be
                written to the Zarr array created by this function. If ``write_data`` is ``False``, then the
                array will be left empty.
        """
        return self._group.create_array(
            name,
            shape=shape,
            dtype=dtype,
            data=data,
            chunks=chunks,
            shards=shards,
            filters=filters,
            compressors=compressors,
            serializer=serializer,
            fill_value=fill_value,
            order=order,
            attributes=attributes,
            chunk_key_encoding=chunk_key_encoding,
            dimension_names=dimension_names,
            storage_options=storage_options,
            overwrite=overwrite,
            config=config,
            write_data=write_data,
        )

    @classmethod
    @override
    def open(
        cls, store: StoreLike | None = None, *, name: str = "", mode: AccessModeLiteral = "a", path: str | None = None
    ) -> Self:
        r"""
        Open this EZDict from a store.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZDict, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store to open.

        Example:
            >>> ez_dict = EZDict.from_dict({"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}})
            >>> ez_dict.save("/tmp/dict", overwrite=True)
            >>> repr(ez_dict.open("/tmp/dict"))
            'EZDict{\n\ta: 1,\n\tb: [1 2 3]\n}'
        """
        path = f"{path.rstrip('/')}/{name}" if path else name
        return cls(zarr.open_group(store, mode=mode, path=path))

    @override
    def save(
        self,
        store: StoreLike,
        *,
        name: str = "",
        mode: AccessModeLiteral = "a",
        path: str | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save this EZDict to a local file system.

        Args:
            store: Store, path to a directory or name of a zip file.
            name: name for the EZDict, to use inside the store.
            mode: Persistence mode: 'r' means read only (must exist); 'r+' means
                read/write (must exist); 'a' means read/write (create if doesn't
                exist); 'w' means create (overwrite if exists); 'w-' means create
                (fail if exists).
            path: path within the store where the EZDict will be saved.
            overwrite: overwrite EZDict if a group with name `name` already exists ? (default: False)

        Example:
            >>> from pathlib import Path
            >>> ez_dict = EZDict.from_dict({"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}})
            >>> ez_dict.save("/tmp/dict", overwrite=True)
            >>> Path("/tmp/dict").exists()
            True
        """
        path = f"{path.rstrip('/')}/{name}/" if path else f"{name}/"

        for _, array in self._group.arrays():
            assert isinstance(array, zarr.Array)
            zarr.create_array(store, name=path + array.path, data=array, overwrite=overwrite)  # pyright: ignore[reportArgumentType]

    @staticmethod
    def _copy_nested(dct: dict[str, Any], value: EZDict[Any]) -> dict[str, Any]:
        for k, v in value.items():
            if isinstance(v, EZDict):
                sub = dct.setdefault(k, {})
                EZDict._copy_nested(sub, v)  # pyright: ignore[reportUnknownArgumentType]

            elif isinstance(v, ezarr.EZList):
                dct[k] = v.copy()

            elif isinstance(v, zarr.Array):
                dct[k] = np.array(v)

            else:
                dct[k] = v

        return dct

    @override
    def copy(self) -> dict[str, T]:
        """
        Convert this EZDict into a Python dict, loading all the data into memory.

        Example:
            >>> ez_dict = EZDict.from_dict({"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}})
            >>> ez_dict.copy()
            {'a': np.int64(1), 'b': array([1, 2, 3]), 'c': {'d': np.str_('some text')}}
        """
        return EZDict._copy_nested({}, self)
