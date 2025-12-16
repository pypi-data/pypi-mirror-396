from typing import Any, Callable, override

import numpy as np
from pandas._typing import ArrayLike, FloatFormatType

class _GenericArrayFormatter:
    def __init__(
        self,
        values: ArrayLike,
        digits: int = 7,
        formatter: Callable[..., Any] | None = None,
        na_rep: str = "NaN",
        space: str | int = 12,
        float_format: FloatFormatType | None = None,
        justify: str = "right",
        decimal: str = ".",
        quoting: int | None = None,
        fixed_width: bool = True,
        leading_space: bool | None = True,
        fallback_formatter: Callable[..., Any] | None = None,
    ) -> None: ...
    def get_result(self) -> list[str]: ...
    def _format_strings(self) -> list[str]: ...

class FloatArrayFormatter(_GenericArrayFormatter):
    def __init__(
        self,
        values: ArrayLike,
        digits: int = 7,
        formatter: Callable[..., Any] | None = None,
        na_rep: str = "NaN",
        space: str | int = 12,
        float_format: FloatFormatType | None = None,
        justify: str = "right",
        decimal: str = ".",
        quoting: int | None = None,
        fixed_width: bool = True,
        leading_space: bool | None = True,
        fallback_formatter: Callable[..., Any] | None = None,
    ) -> None: ...
    def _value_formatter(
        self, float_format: FloatFormatType | None = None, threshold: float | None = None
    ) -> Callable[..., Any]: ...
    def get_result_as_array(self) -> np.ndarray: ...
    @override
    def _format_strings(self) -> list[str]: ...
