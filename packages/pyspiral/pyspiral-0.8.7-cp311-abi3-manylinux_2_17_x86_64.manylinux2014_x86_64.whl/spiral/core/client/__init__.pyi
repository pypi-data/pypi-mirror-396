from enum import Enum
from typing import Any

import pyarrow as pa
from spiral.api.types import DatasetName, IndexName, ProjectId, RootUri, TableId, TableName
from spiral.core.authn import Authn
from spiral.core.config import ClientSettings
from spiral.core.table import ColumnGroupState, KeyRange, KeySpaceState, Scan, ScanState, Snapshot, Table, Transaction
from spiral.core.table.spec import ColumnGroup, Schema
from spiral.expressions import Expr

class Spiral:
    """A client for Spiral database"""
    def __init__(
        self,
        config: ClientSettings | None = None,
        overrides: dict[str, str] | None = None,
    ):
        """Initialize the Spiral client.

        Args:
            config: Client configuration, defaults to the global config.
            overrides: Configuration overrides using dot notation,
                see the [Client Configuration](/python-client) page for a full list.
        """
        ...

    def authn(self) -> Authn:
        """Get the current authentication context."""
        ...

    def scan(
        self,
        projection: Expr,
        filter: Expr | None = None,
        asof: int | None = None,
        key_columns: KeyColumns | None = None,
    ) -> Scan:
        """Construct a table scan."""
        ...

    def load_scan(self, plan_state: ScanState) -> Scan:
        """Load a scan from a serialized scan state."""
        ...

    def transaction(self, table: Table, *, partition_max_bytes: int | None = None) -> Transaction:
        """Being a table transaction."""
        ...

    def search(
        self,
        top_k: int,
        rank_by: Expr,
        *,
        filters: Expr | None = None,
        freshness_window_s: int | None = None,
    ) -> pa.RecordBatchReader:
        """Search an index.

        Searching an index returns a stream of record batches that match table's key schema + float score column.
        """
        ...

    def table(self, table_id: str) -> Table:
        """Get a table."""
        ...

    def create_table(
        self,
        project_id: ProjectId,
        dataset: DatasetName,
        table: TableName,
        key_schema: Schema,
        *,
        root_uri: RootUri | None = None,
        exist_ok: bool = False,
    ) -> Table:
        """Create a new table in the specified project."""
        ...

    def move_table(
        self,
        table_id: TableId,
        new_dataset: DatasetName,
    ):
        """Move a table to a dataset in the same project."""
        ...

    def rename_table(
        self,
        table_id: TableId,
        new_table: TableName,
    ):
        """Rename a table."""
        ...

    def drop_table(self, table_id: TableId):
        """Drop a table."""
        ...

    def text_index(self, index_id: str) -> TextIndex:
        """Get a text index."""
        ...

    def create_text_index(
        self,
        project_id: ProjectId,
        name: IndexName,
        projection: Expr,
        filter: Expr | None = None,
        *,
        root_uri: RootUri | None = None,
        exist_ok: bool = False,
    ) -> TextIndex:
        """Create a new index in the specified project."""
        ...

    def key_space_index(self, index_id: str) -> KeySpaceIndex:
        """Get a key space index."""
        ...

    def create_key_space_index(
        self,
        project_id: ProjectId,
        name: IndexName,
        granularity: int,
        projection: Expr,
        filter: Expr | None = None,
        *,
        root_uri: RootUri | None = None,
        exist_ok: bool = False,
    ) -> KeySpaceIndex:
        """Create a new key space index in the specified project."""
        ...

    def compute_shards(
        self,
        max_batch_size: int,
        projection: Expr,
        filter: Expr | None = None,
        asof: int | None = None,
        stream: bool = False,
    ) -> list[Shard]:
        """Constructs shards for a given projection (and filter).

        Useful for distributing work.
        """
        ...

    def internal(self, *, format: str | None = None) -> Internal:
        """Internal client APIs. It can change without notice."""
        ...

    def config(self) -> ClientSettings:
        """Client-side configuration."""
        ...

class KeyColumns(Enum):
    IfProjected = 0
    Included = 1
    Only = 2

class TextIndex:
    id: str

class KeySpaceIndex:
    id: str
    table_id: str
    granularity: int
    projection: Expr
    filter: Expr
    asof: int

class Shard:
    """A shard representing a partition of data.

    Attributes:
        key_range: The key range for this shard.
        cardinality: The number of rows in this shard, if known.
    """

    key_range: KeyRange
    cardinality: int | None

    def __init__(self, key_range: KeyRange, cardinality: int | None): ...
    def __getnewargs__(self) -> tuple[KeyRange, int | None]: ...

class ShuffleConfig:
    """Configuration for within-shard sample shuffling.

    This controls how samples are shuffled within a buffer, separate from
    which shards to read (which is specified as a parameter to the scan).

    Attributes:
        buffer_size: Size of the buffer pool for shuffling samples.
        seed: Random seed for reproducibility. If None, uses OS randomness.
    """

    buffer_size: int
    seed: int | None

    def __init__(
        self,
        buffer_size: int,
        *,
        seed: int | None = None,
    ): ...

class Internal:
    def flush_wal(self, table: Table) -> None:
        """
        Flush the write-ahead log of the table.
        """
        ...
    def update_text_index(self, index: TextIndex, snapshot: Snapshot) -> None:
        """
        Index table changes up to the given snapshot.
        """
        ...
    def update_key_space_index(self, index: KeySpaceIndex, snapshot: Snapshot) -> None:
        """
        Index table changes up to the given snapshot.
        """
        ...
    def key_space_state(self, snapshot: Snapshot) -> KeySpaceState:
        """
        The key space state for the table.
        """
        ...
    def column_group_state(
        self, snapshot: Snapshot, key_space_state: KeySpaceState, column_group: ColumnGroup
    ) -> ColumnGroupState:
        """
        The state the column group of the table.
        """
        ...
    def column_groups_states(self, snapshot: Snapshot, key_space_state: KeySpaceState) -> list[ColumnGroupState]:
        """
        The state of each column group of the table.
        """
        ...
    def key_space_index_shards(self, index: KeySpaceIndex) -> list[Shard]:
        """
        Compute the scan shards from a key space index.
        """
        ...
    def prepare_shard(
        self,
        output_path: str,
        scan: Scan,
        shard: Shard,
        row_block_size: int = 8192,
    ) -> None:
        """
        Prepare a shard locally. Used for `SpiralStream` integration with `streaming` which requires on-disk shards.
        """
        ...
    def metrics(self) -> dict[str, Any]: ...

def flush_telemetry() -> None:
    """Flush telemetry data to the configured exporter."""
    ...
