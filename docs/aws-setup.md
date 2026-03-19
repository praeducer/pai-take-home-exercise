# AWS Setup — PAI Take-Home Exercise

Complete AWS console and CLI setup for the `pai-exercise` IAM user. Execute the steps below
in order. All CLI steps run in Git Bash.

For a high-level security and assistant-governance overview, see `docs/security-configuration.md`.

---

## Step 1 — Create IAM User in AWS Console

1. Sign in to **AWS Console** → account `730007904340` → **IAM** → **Users** → **Create user**
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
#     "Account": "730007904340",
#     "Arn": "arn:aws:iam::730007904340:user/pai-exercise"
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
        "arn:aws:iam::730007904340:role/pai-exercise-*",
        "arn:aws:iam::730007904340:instance-profile/pai-exercise-*"
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

## Policy Statement Reference

| Statement | What It Covers | Why |
|-----------|---------------|-----|
| `BedrockInvokeModels` | `InvokeModel` + `InvokeModelWithResponseStream` on all 3 model ARNs | `anthropic[bedrock]` uses streaming by default; both actions required |
| `BedrockListModels` | List all foundation models | G-001 verification, `/health-check` skill |
| `S3PipelineBucketActions` | `ListBucket` on input and output bucket ARNs | Bucket-level action — must target bucket ARN not object ARN |
| `S3PipelineObjectActions` | `GetObject` + `PutObject` on objects in both buckets | Object-level actions — must target `bucket/*` ARN |
| `CloudFormation` | All stack + changeset operations | `Resource: "*"` required: `DescribeChangeSet`/`ExecuteChangeSet` target changeset ARNs (different format from stack ARNs); `ValidateTemplate` never supports resource-level scoping |
| `IAMForCloudFormation` | Create/manage `PaiPipelineRole` and instance profile | `CAPABILITY_NAMED_IAM` required when stack defines a named IAM role |
| `S3BucketManagement` | Create/configure S3 buckets with Block Public Access + versioning + lifecycle | CloudFormation creates these bucket resources |
| `BudgetsForAlarm` | Create and view the `$25` monthly budget alarm | `CreateBudget` and `DeleteBudget` are not real IAM actions — create/update both use `ModifyBudget` |
| `MarketplaceForAnthropicAutoEnablement` | Subscribe to Anthropic's Marketplace product | Required for Claude Sonnet 4.6 first-invocation auto-enablement |
| `DenyDestructive` | Explicit deny: object deletion, new user/key creation, model training, org actions | Blast-radius limit |

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

---

## GitHub Actions Secrets (Phase 4)

When GitHub Actions CI/CD is set up in Phase 4, add these secrets to the repo:

1. **GitHub → praeducer/pai-take-home-exercise → Settings → Secrets and variables → Actions**
2. Add:
   - `AWS_ACCESS_KEY_ID` — same key as Step 2
   - `AWS_SECRET_ACCESS_KEY` — same secret as Step 2

These are used by `deploy.yml` to run `aws cloudformation deploy` from GitHub Actions.

### Test GitHub Actions AWS Credentials

After adding the secrets, verify they work before relying on CI/CD deploys:

1. Open **GitHub → praeducer/pai-take-home-exercise → Actions**.
2. Select the deploy workflow (`deploy.yml`).
3. Click **Run workflow** on the `main` branch (or the branch configured in the workflow).
4. In the workflow logs, confirm the AWS auth step succeeds and run identity output shows:
  - Account: `730007904340`
  - ARN: `arn:aws:iam::730007904340:user/pai-exercise`
5. If the run fails with credential errors, re-check `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` values in repository secrets.

---

## Environment Variables for Local Development

Use a repo-root `.env` file (standard dotenv location used by most tooling). This file is gitignored in this repo.

1. Create `.env` in the project root with:

```bash
AWS_PROFILE=pai-exercise
AWS_REGION=us-east-1
```

2. Keep secrets out of `.env` (do not put access keys there). Store credentials in the default AWS location:

```text
~/.aws/credentials
~/.aws/config
```

3. Verify the profile and region are usable:

```bash
aws sts get-caller-identity --profile pai-exercise --region us-east-1
```

The `AnthropicBedrock` client requires `aws_region` set explicitly — it does not read
`~/.aws/config` automatically:

```python
from anthropic import AnthropicBedrock
client = AnthropicBedrock(aws_region="us-east-1")
```
