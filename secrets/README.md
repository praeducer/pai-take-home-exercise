# secrets/

Local secrets and credentials for the `pai-exercise` AWS profile.

**Never commit files from this directory.** All contents except `.gitignore` and this `README.md` are gitignored.

## Contents

| File | Purpose |
|------|---------|
| `pai-exercise_credentials.csv` | IAM access key CSV downloaded from AWS console |

## AWS Setup

Copy credentials from the CSV into `~/.aws/credentials`:

```ini
[pai-exercise]
aws_access_key_id = <from csv>
aws_secret_access_key = <from csv>
```

Then verify:
```bash
aws sts get-caller-identity --profile pai-exercise
```
