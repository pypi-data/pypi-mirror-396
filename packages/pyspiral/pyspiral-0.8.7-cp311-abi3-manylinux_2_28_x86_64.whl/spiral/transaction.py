import logging
from pathlib import Path

from spiral.core.client import Shard
from spiral.core.table import Transaction as CoreTransaction
from spiral.core.table.spec import Operation
from spiral.expressions.base import ExprLike
from spiral.scan import Scan

logger = logging.getLogger(__name__)


class Transaction:
    """Spiral table transaction.

    While transaction can be used to atomically write data to the table,
    it is important that the primary key columns are unique within the transaction.
    """

    def __init__(self, core: CoreTransaction):
        self._core = core

    @property
    def status(self) -> str:
        """The status of the transaction."""
        return self._core.status

    def is_empty(self) -> bool:
        """Check if the transaction has no operations."""
        return self._core.is_empty()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._core.commit()
        else:
            self._core.abort()

    def write(self, expr: ExprLike, push_down_nulls: bool = False):
        """Write an item to the table inside a single transaction.

        :param push_down_nulls: Whether to push down nullable structs down its children. E.g. `[{"a": 1}, null]` would
        become `[{"a": 1}, {"a": null}]`. SpiralDB doesn't allow struct-level nullability, so use this option if your
        data contains nullable structs.

        :param expr: The expression to write. Must evaluate to a struct array.
        """
        from spiral import expressions as se

        record_batches = se.evaluate(expr)
        if push_down_nulls:
            self._core.write_push_down(record_batches)
        else:
            self._core.write(record_batches)

    def writeback(
        self,
        scan: Scan,
        *,
        shards: list[Shard] | None = None,
    ):
        """Write back the results of a scan to the table.

        :param scan: The scan to write back.
            The scan does NOT need to be over the same table as transaction,
            but it does need to have the same key schema.
        :param shards: The shards to read from. If not provided, all shards are read.
        """
        self._core.writeback(scan.core, shards=shards)

    def drop_columns(self, column_paths: list[str]):
        """
        Drops the specified columns from the table.

        :param column_paths: Fully qualified column names. (e.g., "column_name" or "nested.field").
            All columns must exist, if a column doesn't exist the function will return an error.
        """
        self._core.drop_columns(column_paths)

    def compact_key_space(self):
        """Compact the key space of the table."""
        self._core.compact_key_space()

    def take(self) -> list[Operation]:
        """Take the operations from the transaction

        Transaction can no longer be committed or aborted after calling this method.
        ."""
        return self._core.take()

    def include(self, ops: list[Operation]):
        """Include the given operations in the transaction.

        Checks for conflicts between the included operations and any existing operations.
        """
        self._core.include(ops)

    def commit(self, *, txn_dump: str | None = None, compact: bool = False):
        """Commit the transaction."""
        if txn_dump is not None:
            try:
                # Create parent directories if they don't exist
                dump_path = Path(txn_dump)
                dump_path.parent.mkdir(parents=True, exist_ok=True)

                # Write operations to a JSONL file
                with open(dump_path, "w") as f:
                    for op in self._core.ops():
                        f.write(op.to_json() + "\n")

                logger.info(f"Transaction dumped to {txn_dump}")
            except Exception as e:
                logger.error(f"Failed to dump transaction to {txn_dump}: {e}")

        self._core.commit(compact=compact)

    @staticmethod
    def load_dumps(*txn_dump: str) -> list[Operation]:
        """Load a transaction from a dump file."""
        import json

        dumps = list(txn_dump)
        ops: list[Operation] = []

        for dump in dumps:
            with open(dump) as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Each line may contain multiple JSON objects concatenated together
                # This is due to a bug in the dump writing code.
                # Use JSONDecoder to parse them one by one
                decoder = json.JSONDecoder()
                idx = 0
                while idx < len(line):
                    try:
                        obj, end_idx = decoder.raw_decode(line, idx)
                        ops.append(Operation.from_json(json.dumps(obj)))
                        idx = end_idx
                        # Skip whitespace between JSON objects
                        while idx < len(line) and line[idx].isspace():
                            idx += 1
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Failed to parse JSON at position {idx} in line: {line}") from e

        return ops

    def abort(self):
        """Abort the transaction."""
        self._core.abort()
