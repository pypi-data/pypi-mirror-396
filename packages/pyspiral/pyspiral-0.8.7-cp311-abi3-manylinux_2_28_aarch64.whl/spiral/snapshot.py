from typing import TYPE_CHECKING

from spiral.core.table import Snapshot as CoreSnapshot
from spiral.core.table.spec import Schema
from spiral.types_ import Timestamp

if TYPE_CHECKING:
    import duckdb
    import polars as pl
    import pyarrow.dataset as ds
    import torch.utils.data as torchdata  # noqa

    from spiral.table import Table


class Snapshot:
    """Spiral table snapshot.

    A snapshot represents a point-in-time view of a table.
    """

    def __init__(self, table: "Table", core: CoreSnapshot):
        self.core = core
        self._table = table

    @property
    def asof(self) -> Timestamp:
        """Returns the asof timestamp of the snapshot."""
        return self.core.asof

    def schema(self) -> Schema:
        """Returns the schema of the snapshot."""
        return self.core.table.get_schema(asof=self.asof)

    @property
    def table(self) -> "Table":
        """Returns the table associated with the snapshot."""
        return self._table

    def to_arrow_dataset(self) -> "ds.Dataset":
        """Returns a PyArrow Dataset representing the table."""
        from spiral.dataset import Dataset

        return Dataset(self)

    def to_polars_lazy_frame(self) -> "pl.LazyFrame":
        """Returns a Polars LazyFrame for the Spiral table."""
        import polars as pl

        return pl.scan_pyarrow_dataset(self.to_arrow_dataset())

    def to_duckdb_relation(self) -> "duckdb.DuckDBPyRelation":
        """Returns a DuckDB relation for the Spiral table."""
        import duckdb

        # this in theory should work with only sending `self.to_dataset()`,
        # but duckdb (as of 1.4.2) then calls `.scanner()` itself on the
        # dataset object and assumes it is a PyArrow TableScanner, then casts
        # it and tries to access its C++ fields, resulting in a segfault.
        # We directly pass the reader that duckdb just uses the python api of.
        return duckdb.from_arrow(self.to_arrow_dataset().scanner().to_reader())
