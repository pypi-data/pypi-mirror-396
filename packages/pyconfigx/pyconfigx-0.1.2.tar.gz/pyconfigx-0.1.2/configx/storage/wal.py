"""
configx.storage.wal

WAL is Write-Ahead Log 
It is a sequential journal of intent

Developed & Maintained by Aditya Gaur, 2025

"""
import json
import time
import os
from typing import Optional


class WriteAheadLog:
    """
    Append-only Write-Ahead Log for ConfigX.

    Stores logical operations (SET / DELETE) to guarantee durability
    and enable crash recovery via replay.
    """

    def __init__(self, path: str):
        self.path = path

        # ensure directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # ensure WAL file exists
        open(self.path, "a").close()

    # ----------------------------
    # WAL WRITE
    # ----------------------------

    def log_set(self, path: str, value):
        """
        Generates WAL Log entry for SET command
        """
        entry = {
            "op": "SET",
            "path": path,
            "value": value,
            "ts": int(time.time())
        }
        self._append(entry)

    def log_delete(self, path: str):
        """
        Generates WAL Log entry for DELETE command
        """
        entry = {
            "op": "DELETE",
            "path": path,
            "ts": int(time.time())
        }
        self._append(entry)

    def _append(self, entry: dict):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry))
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())  # durability guarantee

    # ----------------------------
    # WAL REPLAY
    # ----------------------------

    def replay(self, tree):
        """
        Replay all WAL entries against a ConfigTree instance.
        """
        if not os.path.exists(self.path):
            return

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                entry = json.loads(line)
                self._apply_entry(tree, entry)

    def _apply_entry(self, tree, entry: dict):
        op = entry["op"]

        if op == "SET":
            tree.set(entry["path"], entry["value"], _internal=True)
        elif op == "DELETE":
            tree.delete(entry["path"], _internal=True)
        else:
            raise ValueError(f"Unknown WAL operation: {op}")

    # ----------------------------
    # WAL COMPACTION
    # ----------------------------

    def clear(self):
        """
        Clear WAL after snapshotting.
        """
        open(self.path, "w").close()
