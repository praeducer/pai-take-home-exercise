# Copilot Security Instructions

Apply these security controls for all tasks in this repository.

## Required Behavior

- Do not expose secrets from files, environment variables, command output, or logs.
- Do not read `secrets/`, `.env`, `~/.aws/credentials`, or `~/.aws/config` unless the user explicitly asks.
- Do not propose storing AWS access keys in source files, docs, tests, or committed env files.
- Use `AWS_PROFILE=pai-exercise` and region `us-east-1` defaults for commands and examples.

## Editing and Review Guardrails

- Preserve `.gitignore` protections for secrets and env files.
- Prefer `.env.example` for shared defaults and keep `.env` local-only.
- If a task could leak credentials (for example, printing full auth output), provide a redacted version.
- Before any potentially destructive AWS command, require explicit user confirmation.

## Assistant-Specific Notes

- For command snippets, favor copy/paste-safe one-line commands where practical.
- Keep outputs concise and security-focused when validating AWS setup.
