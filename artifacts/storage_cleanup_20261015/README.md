# Verified storage cleanup

The user authorized removal of obsolete or duplicate artifact storage on 2026-10-15.
Eight closed Phase 3C evaluation workspace databases were losslessly compressed.
Each gzip stream was read back and its SHA-256 checked against the original before
the uncompressed copy was removed. The manifest preserves both locations, sizes
and the original hash. Scientific receipts, RDF, source documents, correction
negatives, current application/test databases and Phase 1 workspaces were retained.

Freed artifact space: **947,515,404 bytes (903.62 MiB)**. The compressed archives
remain local generated state, excluded from Git like the original databases.

Only the legacy historical report/reconstruction scripts that reopen these cold
workspaces need restoration. Normal application ingestion and the current test
suite do not use these paths. To restore a selected database without overwriting:

```python
import gzip
import hashlib
import json
import shutil
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path("artifacts/storage_cleanup_20261015/manifest.jsonl").read_text().splitlines()
]
row = rows[0]  # Select the required original path in the manifest.
with gzip.open(row["archive"], "rb") as source, open(row["original"], "xb") as target:
    shutil.copyfileobj(source, target)
with open(row["original"], "rb") as source:
    assert hashlib.file_digest(source, "sha256").hexdigest() == row["sha256_original_and_restored"]
```

Original scientific database bytes remain recoverable exactly. Preservation
checks must recognize these explicit archived locations rather than claim their
old uncompressed paths still exist.
