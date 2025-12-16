# configx/storage/runtime.py

import os

from configx.storage.snapshot import SnapshotStore
from configx.storage.wal import WriteAheadLog


class StorageRuntime:
    """
    Coordinates persistence lifecycle for ConfigX.

    Responsibilities:
    - startup recovery (snapshot + WAL replay)
    - write-ahead logging
    - checkpointing (snapshot + WAL compaction)
    - graceful shutdown
    """

    def __init__(self, snapshot_path: str, wal_path: str):
        self.snapshot_path = snapshot_path
        self.wal_path = wal_path

        self.wal = WriteAheadLog(wal_path)
        self._logging_enabled = True

    # -------------------------------------------------
    # Startup / Recovery
    # -------------------------------------------------

    def start(self, tree):
        """
        Recover system state:
        1. Load snapshot if it exists
        2. Replay WAL
        """
        self._logging_enabled = False

        if os.path.exists(self.snapshot_path):
            SnapshotStore.load(tree, self.snapshot_path)

        self.wal.replay(tree)

        self._logging_enabled = True

    # -------------------------------------------------
    # Mutation Hooks (called by ConfigTree)
    # -------------------------------------------------

    def before_set(self, path: str, value):
        if self._logging_enabled:
            self.wal.log_set(path, value)

    def before_delete(self, path: str):
        if self._logging_enabled:
            self.wal.log_delete(path)

    # -------------------------------------------------
    # Checkpointing
    # -------------------------------------------------

    def checkpoint(self, tree):
        """
        Persist full snapshot and clear WAL.
        """
        SnapshotStore.save(tree, self.snapshot_path)
        self.wal.clear()

    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------

    def shutdown(self, tree):
        """
        Graceful shutdown = checkpoint.
        """
        self.checkpoint(tree)
