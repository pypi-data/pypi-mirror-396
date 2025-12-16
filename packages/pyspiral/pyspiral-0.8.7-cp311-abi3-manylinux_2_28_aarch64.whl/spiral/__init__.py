"""Python client for Spiral"""

import importlib
import os
import warnings

# This is here to make sure we load the native extension first
from spiral import _lib

# Eagerly import the Spiral library
assert _lib, "Spiral library"


from spiral.client import Spiral  # noqa: E402
from spiral.core.client import Shard, ShuffleConfig  # noqa: E402
from spiral.dataloader import SpiralDataLoader, World  # noqa: E402
from spiral.enrichment import Enrichment  # noqa: E402
from spiral.iceberg import Iceberg  # noqa: E402
from spiral.key_space_index import KeySpaceIndex  # noqa: E402
from spiral.project import Project  # noqa: E402
from spiral.scan import Scan  # noqa: E402
from spiral.snapshot import Snapshot  # noqa: E402
from spiral.table import Table  # noqa: E402
from spiral.text_index import TextIndex  # noqa: E402
from spiral.transaction import Transaction  # noqa: E402

__all__ = [
    "Spiral",
    "Project",
    "Table",
    "Snapshot",
    "Transaction",
    "Enrichment",
    "Scan",
    "Shard",
    "ShuffleConfig",
    "TextIndex",
    "KeySpaceIndex",
    "SpiralDataLoader",
    "World",
    "Iceberg",
]

__version__ = importlib.metadata.version("pyspiral")


def _warn_msg():
    warnings.warn(
        "Spiral does not support forking, and it may cause undefined behavior. \
            Please use `spawn` or `forkserver` multiprocessing."
    )


if hasattr(os, "register_at_fork"):
    os.register_at_fork(before=_warn_msg)
