from spiral import _lib
from spiral.expressions.base import Expr, ExprLike


def expensive(expr: ExprLike) -> Expr:
    """Minimise the chance of evaluation the expression over the old version of data,
    applying it as late as possible."""
    from spiral import expressions as se

    expr = se.lift(expr)

    return Expr(_lib.expr.pushdown.expensive(expr.__expr__))
