---
name: deploy
description: "Deploy or update the CloudFormation stack (pai-exercise) in us-east-1. Creates S3 buckets, IAM role, and Budget alarm. Requires AWS credentials configured."
argument-hint: "[--env dev|prod]"
disable-model-invocation: true
allowed-tools: Bash, Read
---

Deploy the PAI CloudFormation infrastructure stack.

## Pre-flight Checks

Before deploying, verify:
```bash
aws sts get-caller-identity --profile pai-exercise
aws cloudformation validate-template --template-body file://infra/cloudformation/stack.yaml --profile pai-exercise
```

## Deploy Command

```bash
aws cloudformation deploy \
  --stack-name pai-exercise \
  --template-file infra/cloudformation/stack.yaml \
  --capabilities CAPABILITY_IAM \
  --profile pai-exercise \
  --region us-east-1
```

## Post-Deploy

Show stack outputs (bucket names, role ARN):
```bash
aws cloudformation describe-stacks \
  --stack-name pai-exercise \
  --query 'Stacks[0].Outputs' \
  --profile pai-exercise
```

Save outputs to `phase-01-complete.md` if Phase 1 deployment.

## Expected Outputs

- `InputBucketName` — S3 bucket for brand assets
- `OutputBucketName` — S3 bucket for generated images
- `PipelineRoleArn` — IAM role ARN for pipeline execution
