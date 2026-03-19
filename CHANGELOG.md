# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows semantic versioning where applicable.

## [Unreleased]

<!-- Add upcoming changes here -->

## [1.0.0] — 2026-03-19

### Added

- End-to-end GenAI packaging pipeline: SKU brief JSON → Amazon Bedrock image generation → Pillow text overlay → S3 output.
- Amazon Nova Canvas (`amazon.nova-canvas-v1:0`) as primary image model with Titan V2 as dev/fallback.
- Claude Sonnet 4.6 prompt enhancement via `AnthropicBedrock` for improved image quality.
- 3 aspect ratios per product: front label (1:1, 1024×1024), back label (9:16, 576×1024), wraparound (16:9, 1024×576).
- Pillow text overlay compositing with brand name, attributes, and regulatory text across all 3 layouts.
- S3 output organized by `{SKU}/{region}/{format}/` with JSON manifests per pipeline run.
- Local image caching (`~/.cache/pai-pipeline/`) with deterministic SHA-256 cache keys.
- 8 Claude Code custom skills as the sole interface: `/run-pipeline`, `/pipeline-status`, `/view-results`, `/deploy`, `/teardown`, `/health-check`, `/run-tests`, `/generate-demo`.
- CloudFormation stack: S3 input + output buckets (SSE-S3, Block Public Access), IAM least-privilege role, Budget alarm.
- 35+ unit tests with pytest; GitHub Actions CI (lint + tests + pip-audit on every push).
- `--dry-run` mode and `--model-tier` selection (dev/iterate/final) for cost-controlled iteration.
- Open-source governance files: README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT.
- Assistant security policy and Copilot instruction files.

### Changed

- Hardened ignore patterns for environment and credential artifacts.
- Hardened assistant command guardrails for destructive and sensitive operations.
