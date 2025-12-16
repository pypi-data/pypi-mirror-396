from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dwellir_harvester.collector_base import CollectorFailedError, GenericCollector


class FileIngestCollector(GenericCollector):
    """Ingest JSON from a file and return it as a collector result."""

    NAME = "file-ingest"
    VERSION = "0.0.1"

    @classmethod
    def create(cls, path: Optional[str] = None, paths: Optional[list[str]] = None, *args, **kwargs) -> "FileIngestCollector":
        inst = cls(*args, **kwargs)
        if paths:
            inst._paths = [Path(p) for p in paths]
        elif path is not None:
            inst._paths = [Path(path)]
        else:
            env_path = os.environ.get("FILE_INGEST_PATH")
            inst._paths = [Path(env_path)] if env_path else [Path("/var/lib/dwellir-harvester/ingest.json")]
        return inst

    def collect(self) -> Dict[str, Any]:
        paths = getattr(self, "_paths", [Path("/var/lib/dwellir-harvester/ingest.json")])
        merged: Dict[str, Any] = {}
        for p in paths:
            if not p.exists():
                raise CollectorFailedError(f"file-ingest: file does not exist: {p}")
            try:
                content = p.read_text()
                payload = json.loads(content)
            except Exception as exc:
                raise CollectorFailedError(f"file-ingest: failed to read/parse {p}: {exc}") from exc

            # Store each file's payload under its basename without additional nesting
            merged[p.name] = payload

        result = {
            "meta": {
                "collector_type": getattr(self, "COLLECTOR_TYPE", "generic"),
                "collector_name": self.NAME,
                "collector_version": self.VERSION,
            },
            "data": merged,
        }

        meta = result.setdefault("meta", {})
        meta.setdefault("collector_type", getattr(self, "COLLECTOR_TYPE", "generic"))
        meta.setdefault("collector_name", self.NAME)
        meta.setdefault("collector_version", self.VERSION)
        return result


# Usage:
# 1) Create a JSON file (default path: /var/lib/dwellir-harvester/ingest.json).
# 2) Run via CLI:
#    dwellir-harvester collect file-ingest \
#      --collector-args '{"file-ingest":{"path":"/tmp/ingest.json"}}' \
#      --no-validate
#    Or set env: HARVESTER_COLLECTOR_ARGS='{"file-ingest":{"path":"/tmp/ingest.json"}}'
#    For multiple files: use "paths": ["/tmp/a.json","/tmp/b.json"] to merge data from both.
# 3) Daemon: add file-ingest to --collectors and set HARVESTER_COLLECTOR_ARGS similarly (paths or path).
# 
# Another example: dwellir-harvester collect file-ingest \
#                  --collector-args '{"file-ingest":{"paths":["/tmp/ingest.json","/tmp/ingest2.json"]}}' \
#                   --no-validate
