import abc

import pyarrow as pa

from spiral import _lib
from spiral.expressions.base import Expr, ExprLike


class UDF(abc.ABC):
    """A User-Defined Function (UDF). This class should be subclassed to define custom UDFs.

    Example:

    ```python
    import spiral
    from spiral.demo import fineweb

    sp = spiral.Spiral()
    fineweb_table = fineweb(sp)

    from spiral import expressions as se
    import pyarrow as pa

    class MyAdd(se.UDF):
        def __init__(self):
            super().__init__("my_add")

        def return_type(self, scope: pa.DataType):
            if not isinstance(scope, pa.StructType):
                raise ValueError("Expected struct type as input")
            return scope.field(0).type

        def invoke(self, scope: pa.Array):
            if not isinstance(scope, pa.StructArray):
                raise ValueError("Expected struct array as input")
            return pa.compute.add(scope.field(0), scope.field(1))

    my_add = MyAdd()

    expr = my_add(fineweb_table.select("first_arg", "second_arg"))
    ```
    """

    def __init__(self, name: str):
        self._udf = _lib.expr.udf.create(name, return_type=self.return_type, invoke=self.invoke)

    def __call__(self, scope: ExprLike) -> Expr:
        """Create an expression that calls this UDF with the given arguments."""
        from spiral import expressions as se

        return Expr(self._udf(se.lift(scope).__expr__))

    @abc.abstractmethod
    def return_type(self, scope: pa.DataType) -> pa.DataType:
        """Must return the return type of the UDF given the input scope type.

        All expressions in Spiral must return nullable (Arrow default) types,
        including nested structs, meaning that all fields in structs must also be nullable,
        and if those fields are structs, their fields must also be nullable, and so on.
        """
        ...

    @abc.abstractmethod
    def invoke(self, scope: pa.Array) -> pa.Array:
        """Must implement the UDF logic given the input scope array."""
        ...
