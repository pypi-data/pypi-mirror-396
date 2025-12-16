# eZarr

Easily store any Python object inside [zarr](https://zarr.readthedocs.io/en/latest/) hierarchies.
This package defines proxies for regular Python lists (EZList) and dicts (EZDict), built as wrappers around zarr Arrays and Groups.
It also defines a Protocol for writing and loading any object in zarr hierarchies.

## EZList
An EZlist is a proxy for a Python list built on top of a zarr.Array.
It allows storing mixed arbitrary objects in a 1 dimensional sequence.

### Examples
```python
>>> from ezarr import EZList
>>> from pathlib import Path

# EZList creation from a zarr.Array:
>>> EZList(zarr.array([1, 2, 3]))
EZList[1, 2, 3]

# EZList creation from a list:
>>> data = [1, "some text", Path("some/path.txt")]
>>> ez_list = EZList.from_list(data, store={}, name="data")
                                      #    ~~        ~~~~ a name for the list inside the store
                                      #    |
                                      #    or any zarr StoreLike object to store the list

>>> ez_list
EZList[1, 'some text', PosixPath('some/path.txt')]

# EZLists support general list methods:
>>> ez_list[0]
1

>>> del ez_list[1]
>>> ez_list
EZList[1, PosixPath('some/path.txt')]

>>> ez_list.append(3.14)
>>> ez_list
EZList[1, PosixPath('some/path.txt'), 3.14]

>>> ez_list.insert(0, [1, 2, 3])
>>> ez_list
EZList[[1, 2, 3], 1, PosixPath('/some/path.txt'), 3.14]

# EZList save to zarr store:
>>> ez_list.save("path/to/store", name="saved_list")

# EZList load from zarr store:
>>> EZList.open("path/to/store", name="saved_list")
EZList[[1, 2, 3], 1, PosixPath('/some/path.txt'), 3.14]

# EZList conversion to a regular list:
>>> ez_list.copy()
[[1, 2, 3], 1, PosixPath('some/path.txt'), 3.14]
```

## EZDict
An EZDict is a proxy for a Python dict built on top of a zarr.Group.
It expands zarr.Groups to store and retrieve arbitrary objects.

### Examples
```python
>>> from ezarr import EZDict

# EZdDct creation for a zarr.Group:
>>> EZDict(zarr.open_group({}))
EZDict{}

# EZDict creation for a dict:
>>> data = {"a": 1, "b": [1, 2, 3], "c": {"d": "some text"}}
>>> ez_dict = EZDict.from_dict(data, store={})
                                    #      ~~ or any zarr StoreLike object to store the dict into                                    #      |

# EZDict lazy representation:
>>> ez_dict
EZDict{
        a: 1,
        b: [1 2 3],
        c: {...}                    # <-- note the nested dict was not loaded for the representation
}

# EZDict save to zarr store:
>>> ez_dict.save("path/to/store", name="saved_dict")

# EZDict load from zarr store:
>>> EZDict.open("path/to/store", name="saved_dict")
EZDict{
        a: 1,
        b: [1 2 3],
        c: {...}
}

# EZDict conversion to a regular dict:
>>> ez_dict.copy()
{'a': np.int64(1), 'b': array([1, 2, 3]), 'c': {'d': np.str_('some text')}}

```

## SupportsEZReadWrite
The `SupportsEZReadWrite` protocol, once implemented on an object, allows it to be store in and retrieved from a zarr hierarchy.

```python
@runtime_checkable
class SupportsEZRead(Protocol):
    @classmethod
    def __ez_read__(cls, grp: zarr.Group) -> Self: ...


@runtime_checkable
class SupportsEZWrite(Protocol):
    def __ez_write__(self, grp: zarr.Group) -> None: ...


@runtime_checkable
class SupportsEZReadWrite(SupportsEZRead, SupportsEZWrite, Protocol): ...
```

This protocol has 2 parts:
 - `SupportsEZRead` defines the classmethod `__ez_read__(cls, grp: zarr.Group) -> Self` for reconstructing an object from a zarr.Group.
 - `SupportsEZWrite` defines the method `__ez_write__(self, grp: zarr.Group) -> None` for storing an object in a zarr.Group.

 Once implemented on an object, this protocol allows that object to be automatically saved and loaded in EZLists and EZDicts.
