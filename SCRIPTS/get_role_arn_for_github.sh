#!/bin/bash
# save as: create-github-role.sh

# Variables
GITHUB_ORG="rosaboyle"  # Replace with your GitHub username/org
GITHUB_REPO="nvidia-vercel-2hr-hack"  # Replace with your repo name
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)

# Create trust policy
cat << EOF > trust-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:*"
                },
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
EOF

# Create inline policy for ECR and App Runner permissions
cat << EOF > permissions-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
                "ecr:GetLifecyclePolicy",
                "ecr:GetLifecyclePolicyPreview",
                "ecr:ListTagsForResource",
                "ecr:DescribeImageScanFindings",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "arn:aws:ecr:us-west-2:${AWS_ACCOUNT_ID}:repository/nvda-2hr"
        },
        {
            "Effect": "Allow",
            "Action": "ecr:GetAuthorizationToken",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "apprunner:CreateService",
                "apprunner:UpdateService",
                "apprunner:DeleteService",
                "apprunner:ListServices",
                "apprunner:DescribeService",
                "apprunner:PauseService",
                "apprunner:ResumeService",
                "apprunner:ListOperations",
                "apprunner:TagResource"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the role
ROLE_NAME="github-actions-nvda2hr"
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://trust-policy.json

# Attach the inline policy
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name "ECRAppRunnerAccess" \
  --policy-document file://permissions-policy.json

# Get the role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

echo "✅ Successfully created role"
echo "🔑 Role ARN: $ROLE_ARN"
echo "👉 Add this Role ARN as AWS_ROLE_ARN secret in your GitHub repository"

# Cleanup
rm trust-policy.json permissions-policy.json