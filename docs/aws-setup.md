# AWS Setup — PAI Take-Home Exercise

Complete AWS console and CLI setup for the `pai-exercise` IAM user. Execute the steps below
in order. All CLI steps run in Git Bash.

---

## Step 1 — Create IAM User in AWS Console

1. Sign in to **AWS Console** → account `<ACCOUNT_ID>` → **IAM** → **Users** → **Create user**
2. **User name:** `pai-exercise`
3. **Provide user access to the AWS Management Console:** leave unchecked (programmatic only)
4. Click **Next**
5. **Set permissions:** choose **Attach policies directly**
6. Click **Create policy** (opens new tab) → **JSON** tab → paste the full policy below → **Next**
7. **Policy name:** `pai-exercise-policy` → **Create policy**
8. Back on the user creation tab, refresh and attach `pai-exercise-policy`
9. Click **Next** → **Create user**

---

## Step 2 — Create Access Key

1. Click the `pai-exercise` user → **Security credentials** tab
2. **Access keys** section → **Create access key**
3. **Use case:** Command Line Interface (CLI)
4. Acknowledge the recommendation → **Next**
5. **Description tag:** `pai-exercise-cli` (optional)
6. **Create access key**
7. **Save both values** — the Secret Access Key is shown only once:
   - Access Key ID: `AKIA...`
   - Secret Access Key: `...`

---

## Step 3 — Configure AWS CLI Profile

```bash
aws configure set aws_access_key_id YOUR_ACCESS_KEY_ID --profile pai-exercise
aws configure set aws_secret_access_key YOUR_SECRET_ACCESS_KEY --profile pai-exercise
aws configure set region us-east-1 --profile pai-exercise
aws configure set output json --profile pai-exercise
```

Verify:

```bash
aws sts get-caller-identity --profile pai-exercise
# Expected output:
# {
#     "UserId": "AIDA...",
#     "Account": "<ACCOUNT_ID>",
#     "Arn": "arn:aws:iam::<ACCOUNT_ID>:user/pai-exercise"
# }
```

---

## Step 4 — Verify Bedrock Model Access

Bedrock models auto-enable on first invocation. No console enablement page is needed.

- **Amazon models** (Nova Canvas, Titan V2): auto-enable on first `InvokeModel` call — no
  action required.
- **Anthropic Claude Sonnet 4.6**: has an AWS Marketplace product ID. The IAM policy below
  includes `aws-marketplace:Subscribe` so auto-enablement fires on first invocation.
  First-time use in a new account may trigger a one-time use case form from Anthropic
  in the AWS console before the first Claude invocation succeeds.

Confirm models are visible in the catalog:

```bash
aws bedrock list-foundation-models --profile pai-exercise --region us-east-1 --query "modelSummaries[?contains(modelId,'nova-canvas') || contains(modelId,'titan-image') || contains(modelId,'claude-sonnet-4-6')].modelId"
```

Expected output (all three present):

```json
[
    "amazon.nova-canvas-v1:0",
    "amazon.titan-image-generator-v2:0",
    "anthropic.claude-sonnet-4-6"
]
```

---

## Full IAM Policy — `pai-exercise-policy`

Paste this exactly into the JSON tab in Step 1 above.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvokeModels",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-canvas-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-image-generator-v2:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6"
      ]
    },
    {
      "Sid": "BedrockListModels",
      "Effect": "Allow",
      "Action": "bedrock:ListFoundationModels",
      "Resource": "*"
    },
    {
      "Sid": "S3PipelineBucketActions",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": [
        "arn:aws:s3:::pai-assets-input-*",
        "arn:aws:s3:::pai-packaging-output-*"
      ]
    },
    {
      "Sid": "S3PipelineObjectActions",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::pai-assets-input-*/*",
        "arn:aws:s3:::pai-packaging-output-*/*"
      ]
    },
    {
      "Sid": "CloudFormation",
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResources",
        "cloudformation:GetTemplate",
        "cloudformation:ListStackResources",
        "cloudformation:ValidateTemplate",
        "cloudformation:CreateChangeSet",
        "cloudformation:DescribeChangeSet",
        "cloudformation:ExecuteChangeSet",
        "cloudformation:DeleteChangeSet"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMForCloudFormation",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRole",
        "iam:GetRolePolicy",
        "iam:PassRole",
        "iam:TagRole",
        "iam:UntagRole",
        "iam:CreateInstanceProfile",
        "iam:DeleteInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:RemoveRoleFromInstanceProfile",
        "iam:GetInstanceProfile"
      ],
      "Resource": [
        "arn:aws:iam::<ACCOUNT_ID>:role/pai-exercise-*",
        "arn:aws:iam::<ACCOUNT_ID>:instance-profile/pai-exercise-*"
      ]
    },
    {
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketVersioning",
        "s3:GetBucketVersioning",
        "s3:GetBucketLocation",
        "s3:PutEncryptionConfiguration",
        "s3:GetEncryptionConfiguration",
        "s3:PutLifecycleConfiguration",
        "s3:GetLifecycleConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::pai-assets-input-*",
        "arn:aws:s3:::pai-packaging-output-*"
      ]
    },
    {
      "Sid": "BudgetsForAlarm",
      "Effect": "Allow",
      "Action": [
        "budgets:ModifyBudget",
        "budgets:ViewBudget"
      ],
      "Resource": "*"
    },
    {
      "Sid": "MarketplaceForAnthropicAutoEnablement",
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:Subscribe",
        "aws-marketplace:Unsubscribe",
        "aws-marketplace:ViewSubscriptions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyDestructive",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion",
        "iam:CreateUser",
        "iam:DeleteUser",
        "iam:CreateAccessKey",
        "iam:DeleteAccessKey",
        "bedrock:CreateModelCustomizationJob",
        "bedrock:DeleteFoundationModelAgreement",
        "organizations:*",
        "account:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## CloudFormation Connection Test

Before deploying, verify that your profile can call the CloudFormation service in `us-east-1`:

```bash
aws cloudformation list-stacks --max-items 1 --profile pai-exercise --region us-east-1
```

If this returns stack metadata (or an empty result without auth errors), the service connection is working.

---

## CloudFormation Deploy Command

Use `CAPABILITY_NAMED_IAM` (not just `CAPABILITY_IAM`) because the stack defines a role with
a custom name (`PaiPipelineRole`):

```bash
aws cloudformation deploy --stack-name pai-exercise --template-file infra/cloudformation/stack.yaml --capabilities CAPABILITY_NAMED_IAM --profile pai-exercise --region us-east-1
```
