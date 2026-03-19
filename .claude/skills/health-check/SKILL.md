---
name: health-check
description: "Verify AWS resources, Bedrock model access, and Python environment are correctly configured. Read-only diagnostic tool."
argument-hint: ""
allowed-tools: Bash, Read
---

Run a full health check of the PAI pipeline environment.

## Checks to Run

```bash
echo "=== AWS Identity ==="
aws sts get-caller-identity --profile pai-exercise

echo "=== CloudFormation Stack ==="
aws cloudformation describe-stacks --stack-name pai-exercise \
  --query 'Stacks[0].StackStatus' --profile pai-exercise 2>/dev/null || echo "Stack not deployed"

echo "=== S3 Buckets ==="
aws s3 ls --profile pai-exercise | grep pai

echo "=== Bedrock Model Access ==="
aws bedrock list-foundation-models --region us-east-1 --profile pai-exercise \
  --query 'modelSummaries[?contains(modelId, `nova-canvas`) || contains(modelId, `titan-image`) || contains(modelId, `claude-sonnet`)].{id:modelId,access:modelLifecycleStatus}' \
  --output table 2>/dev/null || echo "Bedrock check failed"

echo "=== Python Environment ==="
python --version
python -c "import boto3, PIL, anthropic, jsonschema; print('deps OK')" 2>/dev/null || echo "deps NOT OK — run: pip install -r requirements.txt"

echo "=== uv (MCP transport) ==="
uv --version 2>/dev/null || echo "uv not installed — run: pip install uv"
```

## Expected Healthy Output

- AWS identity: account `<ACCOUNT_ID>`
- Stack: `CREATE_COMPLETE` or `UPDATE_COMPLETE`
- Bedrock: 3 models listed with access enabled
- Python: `3.12.x`, deps OK
- uv: version string
