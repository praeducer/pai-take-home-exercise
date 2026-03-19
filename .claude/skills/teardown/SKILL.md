---
name: teardown
description: "Destroy the CloudFormation stack and all AWS resources. IRREVERSIBLE — S3 buckets and all generated images will be deleted. Requires explicit confirmation."
argument-hint: "[--confirm]"
disable-model-invocation: true
allowed-tools: Bash, Read
---

DESTRUCTIVE: Tears down the CloudFormation stack and all associated AWS resources.

## Safety Check

This skill WILL NOT proceed without `--confirm` in the arguments:

```
/teardown --confirm
```

Without `--confirm`: Print a warning and exit without doing anything.

## Warning to Display

```
WARNING: This will permanently delete:
  - CloudFormation stack: pai-exercise
  - S3 input bucket (and all contents)
  - S3 output bucket (and ALL generated images)
  - IAM role
  - Budget alarm

This action CANNOT be undone. All generated images will be lost.

To confirm, run: /teardown --confirm
```

## Teardown Sequence (only with --confirm)

1. Empty S3 buckets first (CloudFormation cannot delete non-empty buckets):
```bash
# Get bucket names from stack outputs
INPUT_BUCKET=$(aws cloudformation describe-stacks --stack-name pai-exercise --query 'Stacks[0].Outputs[?OutputKey==`InputBucketName`].OutputValue' --output text --profile pai-exercise)
OUTPUT_BUCKET=$(aws cloudformation describe-stacks --stack-name pai-exercise --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' --output text --profile pai-exercise)

aws s3 rm s3://$INPUT_BUCKET --recursive --profile pai-exercise
aws s3 rm s3://$OUTPUT_BUCKET --recursive --profile pai-exercise
```

2. Delete stack:
```bash
aws cloudformation delete-stack --stack-name pai-exercise --profile pai-exercise --region us-east-1
aws cloudformation wait stack-delete-complete --stack-name pai-exercise --profile pai-exercise
```

3. Confirm: `aws cloudformation describe-stacks --stack-name pai-exercise` should return `ValidationError: Stack with id pai-exercise does not exist`
