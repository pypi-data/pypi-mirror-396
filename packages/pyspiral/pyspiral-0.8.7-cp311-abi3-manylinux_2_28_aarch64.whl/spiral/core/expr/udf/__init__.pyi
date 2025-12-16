from collections.abc import Callable

from pyarrow import Array, DataType, Scalar

from .. import Expr

class UDF:
    def __call__(self, args: list[Expr]) -> Expr: ...

def create(
    name: str,
    return_type: Callable[[tuple[DataType, ...]], DataType],
    invoke: Callable[[tuple[Array[Scalar[DataType]], ...]], Array[Scalar[DataType]]],
) -> UDF: ...
