from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Literal, Protocol, Self, cast, final, override, runtime_checkable

import numpy as np
import numpy.typing as npt
import zarr
from numcodecs.pickles import Pickle  # pyright: ignore[reportMissingTypeStubs]
from numpy._typing import _SupportsArray as SupportsArray  # pyright: ignore[reportPrivateUsage]
from zarr.abc.codec import ArrayBytesCodec
from zarr.core.array_spec import ArraySpec
from zarr.core.buffer import Buffer, NDBuffer
from zarr.core.common import JSON, parse_named_configuration
from zarr.core.dtype import VariableLengthBytes, data_type_registry
from zarr.core.dtype.common import DTypeConfig_V2
from zarr.registry import register_codec

import ezarr


@dataclass
class ListWrapper:
    lst: list[Any] | SupportsArray[Any]


@runtime_checkable
class SupportsEZRead(Protocol):
    @classmethod
    def __ez_read__(cls, values: ezarr.EZDict[Any]) -> Self: ...


@runtime_checkable
class SupportsEZWrite(Protocol):
    def __ez_write__(self, values: ezarr.EZDict[Any]) -> None: ...


@runtime_checkable
class SupportsEZReadWrite(SupportsEZRead, SupportsEZWrite, Protocol): ...


@runtime_checkable
class DeferredCreationFunc(Protocol):
    def __call__(self, grp: zarr.Group, name: str, overwrite: bool) -> None: ...


class PyObjectJSON_V2(DTypeConfig_V2[Literal["|O"], Literal["vlen-bytes"]]):
    """
    A wrapper around the JSON representation of the ``PyObject`` data type in Zarr V2.

    The ``name`` field of this class contains the value that would appear under the
    ``dtype`` field in Zarr V2 array metadata. The ``object_codec_id`` field is always ``py-object``

    References
    ----------
    The structure of the ``name`` field is defined in the Zarr V2
    `specification document <https://github.com/zarr-developers/zarr-specs/blob/main/docs/v2/v2.0.rst#data-type-encoding>`__.

    Examples
    --------
    .. code-block:: python

        {
            "name": "|O",
            "object_codec_id": "py-object"
        }
    """


@final
@dataclass(frozen=True, kw_only=True)
class PyObject(VariableLengthBytes):
    """
    A Zarr data type for arrays containing bytes representations of arbitrary Python objects.

    Wraps the NumPy "object" data type. Scalars for this data type are instances of ``bytes``.

    Attributes
    ----------
    dtype_cls: ClassVar[type[np.dtypes.ObjectDType]] = np.dtypes.ObjectDType
        The NumPy data type wrapped by this ZDType.
    _zarr_v3_name: ClassVar[Literal["python_object"]] = "python_object"
        The name of this data type in Zarr V3.
    object_codec_id: ClassVar[Literal["py-object"]] = "py-object"
        The object codec ID for this data type.

    Notes
    -----
    Because this data type uses the NumPy "object" data type, it does not guarantee a compact memory
    representation of array data. Therefore a "vlen-bytes" codec is needed to ensure that the array
    data can be persisted to storage.
    """

    dtype_cls = np.dtypes.ObjectDType
    _zarr_v3_name: ClassVar[Literal["python_object"]] = "python_object"  # pyright: ignore[reportIncompatibleVariableOverride]
    object_codec_id: ClassVar[Literal["py-object"]] = "py-object"  # pyright: ignore[reportIncompatibleVariableOverride]


_pickle = Pickle()


@dataclass(frozen=True)
class PyObjectCodec(ArrayBytesCodec):
    @override
    @classmethod
    def from_dict(cls, data: dict[str, JSON]) -> Self:
        _, configuration_parsed = parse_named_configuration(data, "py-object", require_configuration=False)
        configuration_parsed = configuration_parsed or {}
        return cls(**configuration_parsed)

    @override
    def to_dict(self) -> dict[str, JSON]:
        return {"name": "py-object", "configuration": {}}

    @override
    def evolve_from_array_spec(self, array_spec: ArraySpec) -> Self:
        return self

    @override
    async def _decode_single(self, chunk_data: Buffer, chunk_spec: ArraySpec) -> NDBuffer:
        assert isinstance(chunk_data, Buffer)

        raw_bytes = chunk_data.as_array_like()
        decoded = cast(npt.NDArray[np.object_], _pickle.decode(raw_bytes))
        assert decoded.dtype == np.object_

        decoded.shape = chunk_spec.shape
        return chunk_spec.prototype.nd_buffer.from_numpy_array(decoded)

    @override
    async def _encode_single(self, chunk_data: NDBuffer, chunk_spec: ArraySpec) -> Buffer | None:
        assert isinstance(chunk_data, NDBuffer)
        return chunk_spec.prototype.buffer.from_bytes(_pickle.encode(self.flatten(chunk_data.as_ndarray_like())))

    flatten = np.vectorize(  # pyright: ignore[reportUnannotatedClassAttribute]
        lambda v: v[()].lst  # pyright: ignore[reportAttributeAccessIssue, reportUnknownArgumentType, reportUnknownLambdaType]
        if isinstance(v, np.ndarray) and isinstance(v[()], ListWrapper)
        else v.lst
        if isinstance(v, ListWrapper)
        else v,
        otypes=[np.object_],
    )

    @override
    def compute_encoded_size(self, input_byte_length: int, chunk_spec: ArraySpec) -> int:
        # what is input_byte_length for an object dtype?
        raise NotImplementedError("compute_encoded_size is not implemented for VLen codecs")


register_codec("python_object", PyObjectCodec)
data_type_registry.register("python_object", PyObject)
