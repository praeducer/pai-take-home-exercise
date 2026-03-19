# Agent Security Policy

This repository contains AWS automation code. Follow least privilege and secret-handling controls at all times.

## Scope

These rules apply to coding assistants and autonomous agents working in this repository, including GitHub Copilot agents, OpenAI Codex-backed agents, and Claude Code agents.

## Secret Handling

- Never print, echo, or log secret values.
- Never read credential files unless explicitly requested by the user for a specific troubleshooting task.
- Treat these locations as sensitive:
  - `secrets/`
  - `.env`
  - `~/.aws/credentials`
  - `~/.aws/config`
- Do not copy values from sensitive files into markdown, code comments, commit messages, issues, or PR descriptions.

## Environment Standard

- Use repo-root `.env` for non-secret defaults only.
- Keep AWS credentials in the default AWS CLI locations (`~/.aws/credentials`, `~/.aws/config`).
- Commit only `.env.example` with placeholder or non-secret values.

## Command Safety

- Block destructive AWS operations unless the user explicitly confirms intent.
- Block secret read/exfiltration commands unless the user explicitly confirms intent.
- Prefer read-only diagnostics before write actions.

## Git Safety

- Never commit files from `secrets/`.
- Never commit `.env` or any environment file containing secrets.
- If a potential secret is detected in tracked files, stop and ask the user before proceeding.

## Output Redaction

When sharing command output, redact any sensitive values. Keep only minimal identifiers needed for verification (for example, account ID and IAM ARN).
