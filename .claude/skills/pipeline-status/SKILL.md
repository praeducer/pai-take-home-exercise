---
name: pipeline-status
description: "Show status of recent pipeline runs. Reads local manifest files from outputs/runs/. Read-only — does not call any AWS APIs."
argument-hint: "[--last N]"
allowed-tools: Read, Bash
---

Display recent pipeline run history from local manifest files.

## Steps

1. List files in `outputs/runs/*.json` sorted by timestamp (newest first)
2. Parse each manifest and display a summary table
3. Default: show last 10 runs. `--last N` overrides.

## Output Format

```
Recent Pipeline Runs
──────────────────────────────────────────────────────────────────
 Timestamp            SKU                  Images  Tier    Status
──────────────────────────────────────────────────────────────────
 2026-03-19 12:00:00  trail-mix-original   6       dev     OK
 2026-03-19 11:30:00  granola-bar-latam    6       final   OK
 2026-03-19 11:00:00  test-brief           0       dev     DRY-RUN
──────────────────────────────────────────────────────────────────
```

Show compliance column if manifest contains compliance section (Phase 6+).
