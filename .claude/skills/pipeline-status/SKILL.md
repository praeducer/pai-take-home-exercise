---
name: pipeline-status
description: "Show status of recent pipeline runs. Reads local manifest files from outputs/runs/. Read-only — does not call any AWS APIs."
argument-hint: "[--last N]"
allowed-tools: Read, Bash
---

Display recent pipeline run history from local manifest files.

## Steps

1. Run this Python snippet to display recent run manifests:

```python
import json, glob
manifests = sorted(glob.glob("outputs/runs/*.json"))
if not manifests:
    print("No pipeline runs found in outputs/runs/")
else:
    print(f"{'Timestamp':<20} {'SKU':<35} {'Images':>6}  {'Status'}")
    print("-" * 75)
    for path in manifests[-10:]:
        data = json.load(open(path))
        status = "DRY-RUN" if data.get("dry_run") else "OK" if not data.get("errors") else f"{len(data['errors'])} errors"
        ts = data.get("timestamp", "")[:19].replace("T", " ")
        print(f"{ts:<20} {data['sku_id']:<35} {data['images_generated']:>6}  {status}")
```

2. Show the last manifest file path for reference.

## Output Format

```
Recent Pipeline Runs
Timestamp            SKU                                 Images  Status
---------------------------------------------------------------------------
2026-03-19 12:00:00  organic-trail-mix-us                     6  OK
2026-03-19 11:30:00  granola-bar-latam                        6  OK
2026-03-19 11:00:00  test-brief                               0  DRY-RUN
```
