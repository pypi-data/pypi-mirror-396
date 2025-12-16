from spiral import _lib
from spiral.expressions.base import Expr, ExprLike


def get(expr: ExprLike, abort_on_error: bool = False) -> Expr:
    """Read data from the local filesystem by the file:// URL.

    Args:
        expr: URLs of the data that needs to be read.
        abort_on_error: Should the expression abort on errors or just collect them.
    """
    from spiral import expressions as se

    expr = se.lift(expr)

    # This just works :)
    return Expr(_lib.expr.s3.get(expr.__expr__, abort_on_error))
