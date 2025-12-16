import datetime
from typing import TypeAlias, Union

import pyarrow as pa

from spiral import _lib

NativeExpr: TypeAlias = _lib.expr.Expr


class Expr:
    """Base class for Spiral expressions. All expressions support comparison and basic arithmetic operations."""

    def __init__(self, native: NativeExpr) -> None:
        if not isinstance(native, NativeExpr):
            raise TypeError(f"Expected a native expression, got {type(native)}")
        self._native = native

    @property
    def __expr__(self) -> NativeExpr:
        return self._native

    def __str__(self):
        return str(self.__expr__)

    def __repr__(self):
        return repr(self.__expr__)

    def __getitem__(self, item: str | int | list[str]) -> "Expr":
        """
        Get an item from a struct or list.

        Args:
            item: The key or index to get.
                If item is a string, it is assumed to be a field in a struct. Dot-separated string is supported
                to access nested fields.
                If item is a list of strings, it is assumed to be a list of fields in a struct.
                If item is an integer, it is assumed to be an index in a list.
        """
        from spiral import expressions as se

        expr = self

        if isinstance(item, int):
            # Assume list and get an element.
            expr = se.list_.element_at(expr, item)
        elif isinstance(item, str):
            if item == "*":
                # Select all fields when "*" is used in getitem.
                # getitem("*") is not a valid expression, so we translate it to select(all).
                expr = se.select(expr, names=[item])
            else:
                # Walk into the struct.
                for part in item.split("."):
                    expr = se.getitem(expr, part)
        elif isinstance(item, list) and all(isinstance(i, str) for i in item):
            expr = expr.select(*item)
        else:
            raise TypeError(f"Invalid item type: {type(item)}")

        return expr

    def __eq__(self, other: "ExprLike") -> "Expr":
        return self._binary("eq", other)

    def __ne__(self, other: "ExprLike") -> "Expr":
        return self._binary("neq", other)

    def __lt__(self, other: "ExprLike") -> "Expr":
        return self._binary("lt", other)

    def __le__(self, other: "ExprLike") -> "Expr":
        return self._binary("lte", other)

    def __gt__(self, other: "ExprLike") -> "Expr":
        return self._binary("gt", other)

    def __ge__(self, other: "ExprLike") -> "Expr":
        return self._binary("gte", other)

    def __and__(self, other: "ExprLike") -> "Expr":
        return self._binary("and", other)

    def __or__(self, other: "ExprLike") -> "Expr":
        return self._binary("or", other)

    def __xor__(self, other: "ExprLike") -> "Expr":
        raise NotImplementedError

    def __add__(self, other: "ExprLike") -> "Expr":
        return self._binary("add", other)

    def __sub__(self, other: "ExprLike") -> "Expr":
        return self._binary("sub", other)

    def __mul__(self, other: "ExprLike") -> "Expr":
        return self._binary("mul", other)

    def __truediv__(self, other: "ExprLike") -> "Expr":
        return self._binary("div", other)

    def __mod__(self, other: "ExprLike") -> "Expr":
        return self._binary("mod", other)

    def __neg__(self):
        return Expr(_lib.expr.unary("neg", self.__expr__))

    def in_(self, other: "ExprLike") -> "Expr":
        from spiral import expressions as se

        other = se.lift(other)
        return Expr(_lib.expr.list.contains(other.__expr__, self.__expr__))

    def contains(self, other: "ExprLike") -> "Expr":
        from spiral import expressions as se

        return se.lift(other).in_(self)

    def cast(self, dtype: pa.DataType) -> "Expr":
        """Cast the expression result to a different data type."""
        return Expr(_lib.expr.cast(self.__expr__, dtype))

    def select(self, *paths: str, exclude: list[str] = None) -> "Expr":
        """Select fields from a struct-like expression.

        Args:
            *paths: Field names to select. If a path contains a dot, it is assumed to be a nested struct field.
            exclude: List of field names to exclude from result.
        """
        from spiral import expressions as se

        if paths:
            if exclude:
                raise ValueError("Cannot specify both selection and exclusion.")

            # If any of the paths contain nested fields, then we re-pack nested select statements.
            if any("." in p for p in paths):
                fields = {}
                for p in paths:
                    if p == "*":
                        # This is handled later.
                        continue

                    if "." not in p:
                        fields[p] = self[p]
                        continue

                    parent, child = p.split(".", 1)
                    node = self[parent].select(child)
                    if parent in fields:
                        fields[parent] = se.merge(fields[parent], node)
                    else:
                        fields[parent] = node

                packed = se.pack(fields)
                if "*" in paths:
                    packed = se.merge(self.select("*"), packed)

                return packed

            return se.select(self, names=list(paths))

        if exclude:
            if any("." in p for p in exclude):
                raise ValueError("Exclusion of nested fields is not supported yet.")
            return se.select(self, exclude=exclude)

        return self

    def _binary(self, op: str, rhs: "ExprLike") -> "Expr":
        """Create a comparison expression."""
        from spiral import expressions as se

        rhs = se.lift(rhs)
        return Expr(_lib.expr.binary(op, self.__expr__, rhs.__expr__))


ScalarLike: TypeAlias = bool | int | float | str | list["ScalarLike"] | datetime.datetime | None
ArrowLike: TypeAlias = Union[
    pa.RecordBatch,
    "pa.Array[pa.Scalar[pa.DataType]]",
    "pa.ChunkedArray[pa.Scalar[pa.DataType]]",
    "pa.Scalar[pa.DataType]",
    pa.Table,
]
ExprLike: TypeAlias = Expr | dict[str, "ExprLike"] | list["ExprLike"] | ArrowLike | ScalarLike
