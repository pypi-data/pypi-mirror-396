from __future__ import annotations

from numbers import Number
import pickle
from collections.abc import Collection, Mapping
from typing import Any, cast
import warnings

import numpy as np
import zarr
import zarr.api.asynchronous
from zarr.errors import UnstableSpecificationWarning, ZarrUserWarning

import ezarr
from ezarr.dict import DictParameters
from ezarr.names import UNKNOWN, Attribute, EZType
from ezarr.types import DeferredCreationFunc, PyObject, PyObjectCodec, SupportsEZRead, SupportsEZWrite


def read_object(grp: zarr.Group, *, name: str, path: str = "") -> Any:
    path = f"{path.lstrip('/')}/{name}" if path else name

    with warnings.catch_warnings(action="ignore", category=ZarrUserWarning):
        data = grp[path]

    ez_type = cast(str, data.attrs.get(Attribute.EZType, UNKNOWN))

    if isinstance(data, zarr.Group):
        if ez_type != EZType.Object:
            return ezarr.EZDict[Any](data)

        ez_class = cast(zarr.Array | None, data.get(Attribute.EZClass))
        if ez_class is None:
            raise ValueError("Cannot read object with unknown class.")

        assert isinstance(ez_class, zarr.Array)
        data_class = pickle.loads(ez_class[()])  # pyright: ignore[reportArgumentType]

        if not issubclass(data_class, SupportsEZRead):
            raise ValueError(f"Can't read {data_class} since it does not implement the '__ez_read__' method.")

        return data_class.__ez_read__(ezarr.EZDict(data))

    if data.ndim == 0:
        return data[()]

    if ez_type == EZType.List:
        return ezarr.EZList[Any](data)

    return data


def write_object[T](
    grp: zarr.Group | ezarr.EZDict[Any],
    *,
    obj: Any,
    name: str,
    path: str = "",
    overwrite: bool = False,
    parameters: DictParameters | None = None,
) -> None:
    """
    Save any object in a zarr.Group

    Args:
        grp: a zarr.Group.
        obj: a Python object to be saved.
        name: name for the object, to use inside the Group.
        path: [optional] path within the Group where the object will be saved.
        overwrite: overwrite if a group with name `name` already exists ? (default: False)
        parameters: optional parameters passed during array creation.
    """
    grp = grp.group if isinstance(grp, ezarr.EZDict) else grp

    if path:
        grp = grp.require_group(path, overwrite=overwrite)

    match obj:
        case SupportsEZWrite():
            subgroup = grp.create_group(name, overwrite=overwrite)
            obj.__ez_write__(ezarr.EZDict(subgroup))
            subgroup.attrs[Attribute.EZType] = EZType.Object

            klass = pickle.dumps(getattr(obj, Attribute.EZClass, type(obj)), protocol=pickle.HIGHEST_PROTOCOL)

            subgroup.create_array(Attribute.EZClass, data=np.void(klass), overwrite=True)  # pyright: ignore[reportArgumentType]

        case DeferredCreationFunc():
            obj(grp, name, overwrite)

        case Mapping():
            subgroup = grp.create_group(name, overwrite=overwrite)
            write_objects(subgroup, "", parameters=parameters, **obj)

        case zarr.Array() | np.ndarray():
            full_name = f"{grp.path.rstrip('/')}/{name}" if grp.path else f"{name}"
            grp._sync(zarr.api.asynchronous.from_array(grp.store, name=full_name, data=obj))  # pyright: ignore[reportPrivateUsage]

        case Collection() | Number():
            with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                grp.create_array(name, data=np.array(obj), overwrite=overwrite, **(parameters or {}))

        case _:
            with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
                arr = grp.create_array(
                    name, shape=(), dtype=PyObject(), serializer=PyObjectCodec(), overwrite=overwrite
                )
            arr[()] = obj


def write_objects[T](
    grp: zarr.Group | ezarr.EZDict[Any], path: str = "", parameters: DictParameters | None = None, **kwargs: Any
) -> None:
    for name, value in kwargs.items():
        write_object(grp, obj=value, name=name, path=path, parameters=parameters)
