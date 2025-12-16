import pandas as pd
import pandas.io.formats.format as fmt
import zarr


_base_repr = pd.Series.__repr__


def _repr_series(series: pd.Series) -> str:
    if isinstance(series.values, zarr.Array):
        params = fmt.get_series_repr_params()  # pyright: ignore[reportAttributeAccessIssue, reportUnknownVariableType]
        return series.copy().to_string(**params)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]

    return _base_repr(series)


pd.Series.__repr__ = _repr_series  # pyright: ignore[reportAttributeAccessIssue]
