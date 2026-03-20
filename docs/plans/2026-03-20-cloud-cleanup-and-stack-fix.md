# Cloud Cleanup, Stack Fix & Documentation Fact-Check Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the CloudFormation `UPDATE_ROLLBACK_COMPLETE` state permanently, delete orphaned S3 prototype data, fact-check all cloud cost/model claims in documentation, and re-run the full pipeline to produce fresh verified outputs.

**Architecture:** Four sequential phases — (A) fix and redeploy infrastructure, (B) clean up S3, (C) fact-check and update docs, (D) re-run pipeline and verify deliverables. Phases A and B must complete before C and D can verify clean state.

**Tech Stack:** AWS CloudFormation YAML, AWS CLI, GitHub Actions, Python, cfn-lint, `aws s3api`

---

## Context for the Implementing Agent

### Repository state (2026-03-20)
- Working directory: `C:/dev/pai-take-home-exercise`
- AWS profile: `pai-exercise`, region `us-east-1`
- Stack name: `pai-exercise`
- Stack status: `UPDATE_ROLLBACK_COMPLETE` (every deploy rolls back — root cause confirmed below)
- Output bucket: `pai-exercise-paipackagingoutputbucket-l4u1ootx9lac`
- Input bucket: `pai-exercise-paiassetsinputbucket-vssunkaugllr`

### Root cause of ROLLBACK (confirmed from stack events)
```
Resource: PaiBudgetAlarm
Status: UPDATE_FAILED
Reason: "A budget or resource with the same name but a different internalId
         already exists." (Budgets API 400)
```
AWS Budgets doesn't support updating a budget once its internal ID drifts from CF's record. Fix: add `DeletionPolicy: Retain` + `UpdateReplacePolicy: Retain` to `PaiBudgetAlarm`. CF will then skip the resource on all future updates.

### Real template issues (verified against live AWS state)
1. `PaiBudgetAlarm` — no retain policies → UPDATE_FAILED on every deploy
2. `PaiAssetsInputBucket` lifecycle rule — `NoncurrentVersionExpirationInDays: 90` with NO `VersioningConfiguration` → no-op rule (noncurrent versions can't exist without versioning)
3. `PaiPackagingOutputBucket` — no `DeletionPolicy` → `delete-stack` would attempt to delete the bucket (fails if non-empty, or destroys data if empty)
4. `deploy.yml` — missing `--no-fail-on-empty-changeset` → deploy job fails on any push that doesn't change CF resources

### The `!` intrinsic function tags (`!Sub`, `!Ref`, `!GetAtt`)
These are **NOT runtime errors**. They are standard CloudFormation YAML shorthand intrinsic functions. All 4 stack resources are `CREATE_COMPLETE`. The "unresolved tag" warnings come from generic YAML linters (VS Code YAML extension) that don't understand CF-specific tags. Fix: add `.cfnlintrc.yaml` (CF-aware linter config) to suppress false positives.

### S3 orphaned prefixes to delete (confirmed from `aws s3 ls --recursive`)
These are prototype SKUs from early development — not part of the final `alpine-harvest-trail-mix` demo:
- `organic-trail-mix-us/` — 7 objects
- `granola-bar-latam/` — 7 objects
- `natural-energy-apac/` — 6 objects
- `plant-protein-bar-eu/` — 7 objects
- `alpine-harvest-trail-mix/apac/front_label/matcha-green-tea.png` — old APAC flavor (3 objects total across formats)
- Old noncurrent versions of all deleted objects (bucket has versioning enabled)

### IAM policy state (verified)
Current deployed policy has `anthropic.claude-sonnet-4-6` (no version suffix) which is the correct Bedrock model ID (confirmed by `list-foundation-models`). Opus (`anthropic.claude-opus-4-6-v1`) is **not** in the policy — correct, since pipeline no longer uses it.

---

## Phase A — Fix CloudFormation Template and Redeploy

### Task 1: Fix `stack.yaml`

**Files:**
- Modify: `infra/cloudformation/stack.yaml`

This is a pure infrastructure change — no tests to write. Verify by deploying and checking stack status.

**Step 1: Read the current template**

```bash
cat infra/cloudformation/stack.yaml
```

Confirm you see: `PaiBudgetAlarm`, `PaiAssetsInputBucket`, `PaiPackagingOutputBucket`, `PaiPipelineRole`.

**Step 2: Apply all four fixes to `infra/cloudformation/stack.yaml`**

Replace the entire file content with the following corrected template:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: >
  PAI Packaging Automation PoC — S3 buckets, IAM role, Budget alarm.
  Intrinsic function shorthand (!Sub, !Ref, !GetAtt) is standard CloudFormation
  YAML syntax, not a linting error. Use cfn-lint (not generic yamllint) to validate.

Parameters:
  BudgetEmail:
    Type: String
    Default: "paul@modular.earth"
    Description: "Email address for budget alarm notifications"

Resources:

  # ---------- S3: Input Assets Bucket ----------
  PaiAssetsInputBucket:
    Type: AWS::S3::Bucket
    # Retain bucket if stack is deleted — prevents accidental loss of uploaded assets
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        IgnorePublicAcls: true
        BlockPublicPolicy: true
        RestrictPublicBuckets: true
      # No versioning on input bucket — lifecycle rule omitted (no-op without versioning)

  # ---------- S3: Output Packaging Images Bucket ----------
  PaiPackagingOutputBucket:
    Type: AWS::S3::Bucket
    # Retain bucket if stack is deleted — generated images must survive infrastructure teardown
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        IgnorePublicAcls: true
        BlockPublicPolicy: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: ExpireNoncurrentVersions
            Status: Enabled
            NoncurrentVersionExpirationInDays: 90

  # ---------- IAM: Pipeline Execution Role ----------
  PaiPipelineRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: pai-pipeline-role
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
          # Allow assumption by IAM users/roles in the same account (local dev)
          - Effect: Allow
            Principal:
              AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
            Action: sts:AssumeRole
      Policies:
        - PolicyName: pai-pipeline-policy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              # S3 read on input bucket
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                  - s3:HeadObject
                Resource:
                  - !GetAtt PaiAssetsInputBucket.Arn
                  - !Sub "${PaiAssetsInputBucket.Arn}/*"
              # S3 read/write on output bucket
              - Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !GetAtt PaiPackagingOutputBucket.Arn
                  - !Sub "${PaiPackagingOutputBucket.Arn}/*"
              # Bedrock model invocations
              # Model IDs verified 2026-03-20 via bedrock:ListFoundationModels
              # anthropic.claude-sonnet-4-6 has no version suffix (unlike claude-opus-4-6-v1)
              - Effect: Allow
                Action: bedrock:InvokeModel
                Resource:
                  - arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-canvas-v1:0
                  - arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-image-generator-v2:0
                  - arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6
              # Explicit denies — defense in depth, cannot be overridden by Allow
              - Effect: Deny
                Action:
                  - s3:DeleteObject
                  - s3:DeleteBucket
                  - s3:PutBucketPolicy
                  - iam:*
                Resource: "*"

  # ---------- Budget: $25/month cost alarm ----------
  PaiBudgetAlarm:
    Type: AWS::Budgets::Budget
    # DeletionPolicy: Retain — AWS Budgets does not support idempotent CF updates.
    # A budget with the same name but a different internal CF tracking ID causes
    # UPDATE_FAILED (Budgets API 400). Retain prevents CF from attempting updates
    # or deletion, eliminating the UPDATE_ROLLBACK_COMPLETE cycle.
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      Budget:
        BudgetName: pai-exercise-budget
        BudgetType: COST
        TimeUnit: MONTHLY
        BudgetLimit:
          Amount: 25
          Unit: USD
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 80
            ThresholdType: PERCENTAGE
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref BudgetEmail
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 100
            ThresholdType: PERCENTAGE
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref BudgetEmail

Outputs:
  InputBucketName:
    Description: "S3 bucket for input assets"
    Value: !Ref PaiAssetsInputBucket
    Export:
      Name: !Sub "${AWS::StackName}-InputBucketName"

  OutputBucketName:
    Description: "S3 bucket for generated packaging images"
    Value: !Ref PaiPackagingOutputBucket
    Export:
      Name: !Sub "${AWS::StackName}-OutputBucketName"

  PipelineRoleArn:
    Description: "IAM role ARN for pipeline execution"
    Value: !GetAtt PaiPipelineRole.Arn
    Export:
      Name: !Sub "${AWS::StackName}-PipelineRoleArn"
```

**Step 3: Validate the template locally**

```bash
aws cloudformation validate-template \
  --template-body file://infra/cloudformation/stack.yaml \
  --profile pai-exercise \
  --region us-east-1
```

Expected: JSON response with `Parameters` and `Description` fields — no error output.

If `cfn-lint` is available:
```bash
cfn-lint infra/cloudformation/stack.yaml
```
Expected: zero errors, zero warnings.

**Step 4: Commit the template fix**

```bash
git add infra/cloudformation/stack.yaml
git commit -m "fix(infra): budget DeletionPolicy Retain — resolves UPDATE_ROLLBACK_COMPLETE

Root cause: AWS Budgets rejects CF updates when the budget's internal tracking
ID drifts from CF's record. DeletionPolicy+UpdateReplacePolicy Retain prevents
CF from attempting updates, ending the rollback cycle.

Additional fixes:
- PaiAssetsInputBucket: removed NoncurrentVersionExpiration lifecycle rule
  (no-op without versioning; versioning not enabled on input bucket)
- PaiPackagingOutputBucket: added DeletionPolicy Retain (protects generated images)
- PaiAssetsInputBucket: added DeletionPolicy Retain (protects uploaded assets)
- Added descriptive comments explaining !Sub/!Ref/!GetAtt tag behavior
- Verified IAM Bedrock ARNs against live bedrock:ListFoundationModels output"
```

---

### Task 2: Fix the Deploy Workflow

**Files:**
- Modify: `.github/workflows/deploy.yml`

**Step 1: Read the current deploy workflow**

```bash
cat .github/workflows/deploy.yml
```

**Step 2: Add `--no-fail-on-empty-changeset`**

Find the `aws cloudformation deploy` command and add the flag. The deploy step should become:

```yaml
      - name: Deploy CloudFormation stack
        run: |
          aws cloudformation deploy \
            --stack-name pai-exercise \
            --template-file infra/cloudformation/stack.yaml \
            --capabilities CAPABILITY_NAMED_IAM \
            --region us-east-1 \
            --no-fail-on-empty-changeset
```

**Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "fix(ci): add --no-fail-on-empty-changeset to cloudformation deploy

Without this flag, the deploy job exits non-zero on pushes that do not
change CF resources (e.g., Python-only commits). This caused false deploy
failures on every non-infrastructure commit."
```

---

### Task 3: Add cfn-lint Config

**Files:**
- Create: `.cfnlintrc.yaml`

**Step 1: Create `.cfnlintrc.yaml` at the repo root**

```yaml
# .cfnlintrc.yaml — CloudFormation linter configuration
# cfn-lint understands all CF intrinsic function shorthand (!Sub, !Ref, !GetAtt, etc.)
# and validates them correctly. Generic YAML linters (yamllint, VS Code YAML extension)
# do not understand these CF-specific YAML tags and emit false "unresolved tag" warnings.
# Use cfn-lint, not generic YAML linters, to validate CloudFormation templates.
templates:
  - infra/cloudformation/stack.yaml
regions:
  - us-east-1
include_checks:
  - W
```

**Step 2: Commit**

```bash
git add .cfnlintrc.yaml
git commit -m "chore: add .cfnlintrc.yaml — CF-aware linter config

Suppresses false 'unresolved tag' warnings from generic YAML linters
for !Sub, !Ref, !GetAtt intrinsic functions. cfn-lint is the authoritative
validator for CloudFormation templates."
```

---

### Task 4: Push and Wait for CI + Deploy to Go Green

**Step 1: Push all commits**

```bash
git push origin main
```

**Step 2: Watch the CI run**

```bash
gh run list --repo praeducer/pai-take-home-exercise --workflow ci.yml --limit 1 \
  --json databaseId --jq '.[0].databaseId'
# Use the ID to watch:
gh run watch <CI_RUN_ID> --repo praeducer/pai-take-home-exercise --exit-status
```

Expected: all CI steps green (lint, test 42 passed, pip-audit).

**Step 3: Watch the Deploy run**

```bash
gh run list --repo praeducer/pai-take-home-exercise --workflow deploy.yml --limit 1 \
  --json databaseId --jq '.[0].databaseId'
gh run watch <DEPLOY_RUN_ID> --repo praeducer/pai-take-home-exercise --exit-status
```

Expected: deploy job exits 0 (either applies changeset or "No changes to deploy" without failing).

**Step 4: Verify stack is out of ROLLBACK state**

```bash
aws cloudformation describe-stacks \
  --stack-name pai-exercise \
  --profile pai-exercise \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus' \
  --output text
```

Expected: `UPDATE_COMPLETE` (not `UPDATE_ROLLBACK_COMPLETE`).

If still `UPDATE_ROLLBACK_COMPLETE`: the changeset may not have included enough resource changes to trigger the budget update. In that case run a manual deploy:

```bash
aws cloudformation deploy \
  --stack-name pai-exercise \
  --template-file infra/cloudformation/stack.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --profile pai-exercise \
  --region us-east-1 \
  --no-fail-on-empty-changeset
```

Then re-check status.

---

## Phase B — S3 Cleanup

### Task 5: Delete Orphaned Prototype SKU Objects

**Step 1: Confirm objects exist before deleting**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1 \
  | grep -E "^(.*organic-trail-mix|.*granola-bar-latam|.*natural-energy-apac|.*plant-protein-bar-eu)"
```

Expected: 27 objects across the 4 prototype prefixes.

**Step 2: Delete all current-version objects under the 4 prototype prefixes**

```bash
for prefix in organic-trail-mix-us granola-bar-latam natural-energy-apac plant-protein-bar-eu; do
  echo "=== Deleting prefix: $prefix ==="
  aws s3 rm s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/$prefix/ \
    --recursive \
    --profile pai-exercise \
    --region us-east-1
done
```

Expected: `delete:` lines for each object, no errors.

**Step 3: Delete noncurrent versions and delete markers for those prefixes**

The output bucket has versioning enabled. `aws s3 rm` only deletes current versions (it creates delete markers). Use `s3api` to purge all versions:

```bash
for prefix in organic-trail-mix-us granola-bar-latam natural-energy-apac plant-protein-bar-eu; do
  echo "=== Purging versions for: $prefix ==="
  # Get all version IDs and delete markers
  aws s3api list-object-versions \
    --bucket pai-exercise-paipackagingoutputbucket-l4u1ootx9lac \
    --prefix "$prefix/" \
    --profile pai-exercise \
    --output json \
  | python -c "
import json, sys
data = json.load(sys.stdin)
objects = []
for v in data.get('Versions', []):
    objects.append({'Key': v['Key'], 'VersionId': v['VersionId']})
for m in data.get('DeleteMarkers', []):
    objects.append({'Key': m['Key'], 'VersionId': m['VersionId']})
if objects:
    print(json.dumps({'Objects': objects, 'Quiet': True}))
" | while read -r payload; do
    aws s3api delete-objects \
      --bucket pai-exercise-paipackagingoutputbucket-l4u1ootx9lac \
      --delete "$payload" \
      --profile pai-exercise \
      --region us-east-1
  done
done
```

Expected: JSON `{"Deleted": [...]}` for each prefix with all versions deleted.

**Step 4: Verify prototype prefixes are gone**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1 \
  | grep -E "organic-trail-mix|granola-bar-latam|natural-energy-apac|plant-protein-bar-eu"
```

Expected: zero output (empty).

---

### Task 6: Delete Old Matcha Green Tea APAC Files

**Step 1: Confirm matcha files exist**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise \
  | grep matcha-green-tea
```

Expected: 3 lines (front_label, back_label, wraparound).

**Step 2: Delete current-version matcha objects**

```bash
aws s3 rm s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/alpine-harvest-trail-mix/ \
  --recursive \
  --exclude "*" \
  --include "*matcha-green-tea*" \
  --profile pai-exercise \
  --region us-east-1
```

Expected: 3 `delete:` lines.

**Step 3: Purge matcha noncurrent versions**

```bash
aws s3api list-object-versions \
  --bucket pai-exercise-paipackagingoutputbucket-l4u1ootx9lac \
  --profile pai-exercise \
  --output json \
| python -c "
import json, sys
data = json.load(sys.stdin)
objects = []
for v in data.get('Versions', []):
    if 'matcha-green-tea' in v['Key']:
        objects.append({'Key': v['Key'], 'VersionId': v['VersionId']})
for m in data.get('DeleteMarkers', []):
    if 'matcha-green-tea' in m['Key']:
        objects.append({'Key': m['Key'], 'VersionId': m['VersionId']})
if objects:
    print(json.dumps({'Objects': objects, 'Quiet': True}))
    print(f'# Deleting {len(objects)} version(s)', file=sys.stderr)
else:
    print('# No versions found', file=sys.stderr)
" | grep -v "^#" | while read -r payload; do
  [ -z "$payload" ] && continue
  aws s3api delete-objects \
    --bucket pai-exercise-paipackagingoutputbucket-l4u1ootx9lac \
    --delete "$payload" \
    --profile pai-exercise \
    --region us-east-1
done
```

**Step 4: Verify final S3 state — only alpine-harvest-trail-mix remains**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1
```

Expected: only `alpine-harvest-trail-mix/` prefix, no matcha files, all 4 regions with correct products:
- `us-west/`: original + dark-chocolate (6 images + 1 manifest)
- `latam/`: original + tropical-edition (6 images + 1 manifest)
- `apac/`: original + mango-coconut (6 images + 1 manifest)
- `eu/`: original + dark-berry (6 images + 1 manifest)

**Step 5: Count remaining objects**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1 | wc -l
```

Expected: 28 objects (4 regions × 7 objects each = 24 images + 4 manifests).

---

## Phase C — Fact-Check Documentation

### Task 7: Verify Bedrock Pricing and Update Cost Claims

**Step 1: Fetch current Nova Canvas pricing from AWS**

```bash
# Check the AWS pricing page for Nova Canvas
# Authoritative source: https://aws.amazon.com/bedrock/pricing/
# Fetch and check
```

Use WebFetch to pull `https://aws.amazon.com/bedrock/pricing/` and extract:
- Nova Canvas standard quality price per image (1024×1024)
- Nova Canvas premium quality price per image
- Amazon Titan Image Generator V2 price per image
- Claude Sonnet 4.6 input/output token prices on Bedrock

**Step 2: Verify actual pipeline call costs**

The pipeline makes these AI calls per full 4-region demo run (24 images):
- Brand profile: 4 calls (one per brief) to `claude-sonnet-4-6` via tool_use, max_tokens=300
  - Estimate input tokens: ~450-600 tokens per call
  - Estimate output tokens: ~250-300 tokens per call
- Prompt enhancement: 24 calls to `claude-sonnet-4-6`, max_tokens=400
  - Estimate input tokens: ~300-400 tokens per call
  - Estimate output tokens: ~300-400 tokens per call
- Image generation: 24 calls to `nova-canvas-v1:0` at premium quality

Calculate actual expected total and compare to claims in:
- `docs/solution-architecture.md` Section 10 (PoC Cost Breakdown table)
- `README.md` (mentions "$0.20 for 24 high-quality packaging variants")
- `docs/uat-walkthrough.md` Section 3.4 model cost table

**Step 3: Update any incorrect cost figures**

If the real cost materially differs from documented costs (>20% off):
- Update `docs/solution-architecture.md` Section 10 cost breakdown table
- Update `README.md` executive summary cost claim
- Update `docs/uat-walkthrough.md` Section 3.4 model table

If costs are within ~20%, add a note that costs are approximate and leave as-is.

**Step 4: Verify model IDs in documentation match live AWS**

Confirmed from `list-foundation-models` on 2026-03-20:
- `amazon.nova-canvas-v1:0` ✓
- `amazon.titan-image-generator-v2:0` ✓
- `anthropic.claude-sonnet-4-6` ✓ (no `-v1` suffix)
- `anthropic.claude-opus-4-6-v1` ✓ (has `-v1` suffix — Opus IS different)

Check these strings appear correctly in:
```bash
grep -rn "claude-opus\|claude-sonnet\|nova-canvas\|titan-image" \
  docs/ README.md --include="*.md"
```

Fix any occurrences of `claude-opus-4-6` (missing `-v1` suffix) in documentation.

**Step 5: Fact-check UAT walkthrough checklist items**

Run each verification command from the walkthrough and confirm expected outputs:

```bash
# 1. Unit tests
pytest tests/ -q -m "not integration" --tb=short
# Expected: 42 passed, 3 skipped

# 2. Schema validation
python -c "
import json, jsonschema, glob
schema = json.load(open('src/schemas/sku_brief_schema.json'))
for path in glob.glob('inputs/demo_briefs/*.json') + ['inputs/sample_sku_brief.json']:
    jsonschema.validate(json.load(open(path)), schema)
    print(f'valid: {path}')
"
# Expected: 5 valid lines

# 3. Dry-run pipeline
python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json --dry-run
# Expected: 6 skipped lines, exits clean

# 4. Demo images exist
find outputs/demo -name "*.png" | sort
# Expected: 6 images including apac/mango-coconut.png (NOT matcha-green-tea.png)
```

**Step 6: Update UAT walkthrough with any corrections found**

If any checklist items are wrong (wrong counts, wrong filenames, stale URLs), update `docs/uat-walkthrough.md`.

**Step 7: Commit documentation updates**

```bash
git add docs/solution-architecture.md docs/uat-walkthrough.md README.md
git commit -m "docs: fact-check cloud costs, model IDs, and UAT checklist

- Verified Bedrock pricing against aws.amazon.com/bedrock/pricing/ (2026-03-20)
- Confirmed model IDs match live bedrock:ListFoundationModels output
- Updated cost estimates to match verified pricing
- UAT checklist verified against live environment"
```

---

## Phase D — Re-Run Pipeline and Share Deliverables

### Task 8: Run Full Demo Pipeline

**Step 1: Verify AWS connectivity before running**

```bash
aws sts get-caller-identity --profile pai-exercise
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --profile pai-exercise --region us-east-1 | head -5
```

Expected: account ID returned, S3 bucket accessible.

**Step 2: Set the output bucket environment variable**

```bash
export PAI_OUTPUT_BUCKET=pai-exercise-paipackagingoutputbucket-l4u1ootx9lac
```

**Step 3: Run all 4 demo briefs at final tier**

```bash
for brief in trail-mix-us trail-mix-latam trail-mix-apac trail-mix-eu; do
  echo "=== Running $brief ==="
  python -m src.pipeline.run_pipeline \
    inputs/demo_briefs/${brief}.json \
    --model-tier final \
    --profile pai-exercise
  echo "=== Done $brief ==="
done
```

Expected for each brief:
- 6 lines showing image generation (2 products × 3 formats)
- `Pipeline complete: 6 images`
- Duration ~25-35 seconds per brief

**Step 4: Verify S3 object count after run**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1 | grep "\.png" | wc -l
```

Expected: ≥24 PNG files.

**Step 5: Verify manifest files**

```bash
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1 | grep "\.json"
```

Expected: at least 4 manifest files (one per region).

**Step 6: Check pipeline outputs locally**

```bash
find outputs/results -name "*.png" | wc -l
find outputs/results -name "*.png" | sort
```

Expected: 24 PNG files organized by region/format/product.

**Step 7: Commit fresh pipeline outputs**

```bash
git add outputs/results/ outputs/runs/
git commit -m "chore: fresh pipeline outputs — 24 images post cloud cleanup

Generated with Nova Canvas premium (final tier) after:
- Stack fixed to UPDATE_COMPLETE (budget DeletionPolicy Retain)
- S3 cleaned: deleted 4 prototype SKU prefixes + matcha-green-tea APAC variant
- All 4 regions: us-west, latam, apac (mango-coconut), eu"
```

---

### Task 9: Final Verification and Deliverables Summary

**Step 1: Confirm stack status is clean**

```bash
aws cloudformation describe-stacks \
  --stack-name pai-exercise \
  --profile pai-exercise \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus' \
  --output text
```

Expected: `UPDATE_COMPLETE` (not `UPDATE_ROLLBACK_COMPLETE`).

**Step 2: Confirm CI is green**

```bash
gh run list --repo praeducer/pai-take-home-exercise \
  --workflow ci.yml --limit 1 \
  --json conclusion,url --jq '.[0]'
```

Expected: `"conclusion": "success"`.

**Step 3: Run full regression**

```bash
ruff check src/ tests/
pytest tests/ -q -m "not integration"
python -m src.pipeline.run_pipeline inputs/sample_sku_brief.json --dry-run
```

Expected:
- ruff: zero output
- pytest: 42 passed, 3 skipped
- dry-run: 6 skipped lines, exits clean

**Step 4: Push all commits and tag v1.2.1**

```bash
git push origin main
git tag -a v1.2.1 -m "v1.2.1: cloud cleanup — fixed CF ROLLBACK, S3 prototype data deleted, costs verified"
git push origin v1.2.1
```

**Step 5: Print final deliverables summary**

```bash
echo "=== GITHUB ==="
echo "Repo:       https://github.com/praeducer/pai-take-home-exercise"
echo "CI badge:   https://github.com/praeducer/pai-take-home-exercise/actions/workflows/ci.yml"
echo "v1.2.1 tag: https://github.com/praeducer/pai-take-home-exercise/releases/tag/v1.2.1"
echo ""
echo "=== AWS RESOURCES ==="
aws cloudformation describe-stacks \
  --stack-name pai-exercise \
  --profile pai-exercise \
  --region us-east-1 \
  --query 'Stacks[0].{Status:StackStatus,LastUpdated:LastUpdatedTime}' \
  --output table
echo ""
echo "=== S3 FINAL STATE ==="
aws s3 ls s3://pai-exercise-paipackagingoutputbucket-l4u1ootx9lac/ \
  --recursive --profile pai-exercise --region us-east-1 \
  | grep "\.png" | wc -l
echo "PNG files in S3 (expected: ≥24)"
echo ""
echo "=== LOCAL OUTPUTS ==="
find outputs/results -name "*.png" | wc -l
echo "PNG files locally (expected: 24)"
```

---

## Pass Criteria

All of the following must be true after Task 9:

| Check | Expected |
|-------|---------|
| `aws cloudformation describe-stacks` | `UPDATE_COMPLETE` (not ROLLBACK) |
| `aws cloudformation deploy` (re-run) | Exits 0 (no changeset or clean deploy) |
| S3 prototype prefixes | Zero objects in `organic-trail-mix-us/`, `granola-bar-latam/`, `natural-energy-apac/`, `plant-protein-bar-eu/` |
| S3 matcha-green-tea | Zero objects matching `*matcha-green-tea*` |
| S3 PNG count | ≥24 in `alpine-harvest-trail-mix/` |
| `ruff check src/ tests/` | Exit 0, zero output |
| `pytest -m "not integration"` | 42 passed, 3 skipped |
| `aws cloudformation validate-template` | No errors |
| CI latest run | `"conclusion": "success"` |
| v1.2.1 tag | Exists on GitHub |
| SA doc + UAT walkthrough | Cost figures verified against real pricing |
