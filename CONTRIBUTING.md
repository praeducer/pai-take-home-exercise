# Contributing

Thanks for your interest in contributing.

## Before You Start

- Read `README.md` and `docs/security-configuration.md`.
- Follow security policies in `AGENTS.md` and `.github/copilot-instructions.md`.
- Do not commit secrets, credentials, or local environment files.

## Development Workflow

1. Fork the repository and create a feature branch.
2. Keep changes focused and include tests where applicable.
3. Run linting and tests locally before opening a PR.
4. Open a pull request with a clear summary and rationale.

## Commit and PR Guidelines

- Use clear, descriptive commit messages.
- Document behavior changes and any operational impact.
- Include security considerations for AWS/IAM/Bedrock changes.

## Security Requirements

- Never include AWS access keys, `.env`, or contents from `secrets/`.
- Use redacted outputs in examples and discussions.
- Prefer least-privilege changes and explain why permissions are required.

## Scope and Priorities

- Refer to `BACKLOG.md` for out-of-scope and future items.
- Keep PoC constraints in mind when proposing large architecture changes.
