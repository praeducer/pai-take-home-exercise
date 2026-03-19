# PAI Packaging Automation PoC

Public proof-of-concept for automated product packaging asset generation using AWS services and GenAI models.

## Project Status

This repository is in active development for a take-home exercise. The implementation roadmap and phase plans are in `.claude/plans/`.

## Goals

- Accept SKU briefs and generate packaging assets for multiple formats.
- Use AWS-native services and CloudFormation-managed infrastructure.
- Store outputs in structured S3 paths by SKU, region, and format.

## Tech Stack

- Python 3.12
- AWS (S3, CloudFormation, Bedrock, IAM)
- Claude Code and GitHub Copilot-assisted development workflows

## Repository Structure

- `src/` application code
- `infra/cloudformation/` infrastructure templates
- `tests/` automated tests
- `docs/` setup and security documentation
- `inputs/` exercise and profile reference inputs

## Security and Responsible Use

- Security configuration overview: `docs/security-configuration.md`
- AWS setup and least-privilege guidance: `docs/aws-setup.md`
- Assistant policies: `AGENTS.md` and `.github/copilot-instructions.md`

## Quick Start

1. Follow `docs/aws-setup.md`.
2. Configure local non-secret defaults in `.env` (see `.env.example`).
3. Use AWS profile `pai-exercise` in `us-east-1`.

## Open Source Standards

- License: see `LICENSE`
- Contributing guide: see `CONTRIBUTING.md`
- Security policy: see `SECURITY.md`
- Code of conduct: see `CODE_OF_CONDUCT.md`

## Roadmap

Current and future scope is tracked in `BACKLOG.md` and phase plans under `.claude/plans/`.
