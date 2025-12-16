"""
ConfigX Testing Suite - test_runtime_persistence.py

End-to-end tests for ConfigX persistence layer:
- Snapshot
- WAL (Write-Ahead Log)
- StorageRuntime coordination

These tests validate durability, crash recovery, and correctness guarantees.
Developed & Maintained by Aditya Gaur, 2025
"""

import os
import shutil
import tempfile
import pytest

from configx.core.tree import ConfigTree
from configx.storage.runtime import StorageRuntime
from configx.core.errors import ConfigNodeStructureError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

@pytest.fixture()
def temp_storage():
    """
    Creates a temporary directory for snapshot + WAL files.
    Automatically cleaned up after test.
    """
    tmpdir = tempfile.mkdtemp()
    snapshot = os.path.join(tmpdir, "state.snapshot")
    wal = os.path.join(tmpdir, "state.wal")

    yield snapshot, wal

    shutil.rmtree(tmpdir)


# -----------------------------------------------------------------------------
# 1. WAL-only recovery (no snapshot)
# -----------------------------------------------------------------------------

def test_recovery_from_wal_only(temp_storage):
    snapshot, wal = temp_storage

    runtime = StorageRuntime(snapshot, wal)
    tree = ConfigTree(runtime=runtime)
    runtime.start(tree)

    tree.set("app.ui.theme", "dark")
    tree.set("app.ui.fontSize", 14)

    # simulate crash: new tree + runtime
    runtime2 = StorageRuntime(snapshot, wal)
    tree2 = ConfigTree(runtime=runtime2)
    runtime2.start(tree2)

    assert tree2.get("app.ui.theme") == "dark"
    assert tree2.get("app.ui.fontSize") == 14


# -----------------------------------------------------------------------------
# 2. Snapshot + WAL recovery
# -----------------------------------------------------------------------------

def test_snapshot_plus_wal_recovery(temp_storage):
    snapshot, wal = temp_storage

    runtime = StorageRuntime(snapshot, wal)
    tree = ConfigTree(runtime=runtime)
    runtime.start(tree)

    tree.set("a", 1)
    tree.set("b", 2)

    runtime.checkpoint(tree)  # snapshot + WAL clear

    tree.set("c", 3)

    # simulate crash
    runtime2 = StorageRuntime(snapshot, wal)
    tree2 = ConfigTree(runtime=runtime2)
    runtime2.start(tree2)

    assert tree2.get("a") == 1
    assert tree2.get("b") == 2
    assert tree2.get("c") == 3


# -----------------------------------------------------------------------------
# 3. Failed SET must NOT touch WAL
# -----------------------------------------------------------------------------

def test_failed_set_not_logged(temp_storage):
    snapshot, wal = temp_storage

    runtime = StorageRuntime(snapshot, wal)
    tree = ConfigTree(runtime=runtime)
    runtime.start(tree)

    tree.set("app.ui.theme", "dark")

    with pytest.raises(ConfigNodeStructureError):
        # invalid: app.ui is now interior
        tree.set("app.ui", "red")

    # WAL should only contain ONE entry
    with open(wal, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 1


# -----------------------------------------------------------------------------
# 4. Replay must NOT re-log operations
# -----------------------------------------------------------------------------

def test_replay_does_not_duplicate_wal(temp_storage):
    snapshot, wal = temp_storage

    runtime = StorageRuntime(snapshot, wal)
    tree = ConfigTree(runtime=runtime)
    runtime.start(tree)

    tree.set("x", 10)
    tree.set("y", 20)

    with open(wal, "r", encoding="utf-8") as f:
        wal_size_before = len(f.readlines())

    # restart
    runtime2 = StorageRuntime(snapshot, wal)
    tree2 = ConfigTree(runtime=runtime2)
    runtime2.start(tree2)

    with open(wal, "r", encoding="utf-8") as f:
        wal_size_after = len(f.readlines())

    assert wal_size_before == wal_size_after


# -----------------------------------------------------------------------------
# 5. Shutdown triggers snapshot + WAL clear
# -----------------------------------------------------------------------------

def test_shutdown_checkpoints_and_clears_wal(temp_storage):
    snapshot, wal = temp_storage

    runtime = StorageRuntime(snapshot, wal)
    tree = ConfigTree(runtime=runtime)
    runtime.start(tree)

    tree.set("p", 100)
    tree.set("q", 200)

    runtime.shutdown(tree)

    # WAL should be empty
    with open(wal, "r", encoding="utf-8") as f:
        assert f.read().strip() == ""

    # Snapshot should restore state
    runtime2 = StorageRuntime(snapshot, wal)
    tree2 = ConfigTree(runtime=runtime2)
    runtime2.start(tree2)

    assert tree2.get("p") == 100
    assert tree2.get("q") == 200
