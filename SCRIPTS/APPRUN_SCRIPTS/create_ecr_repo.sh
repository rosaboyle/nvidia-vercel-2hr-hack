#!/bin/bash
# save as: setup-aws.sh

# Variables
REGION="us-west-2"
REPO_NAME="nvda-2hr"

echo "Creating ECR repository..."
aws ecr create-repository \
    --repository-name $REPO_NAME \
    --region $REGION \
    --image-scanning-configuration scanOnPush=true

echo "Creating IAM role for App Runner..."
TRUST_POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "build.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
)

ROLE_NAME="AppRunnerECRAccessRole-nvda2hr"

# Create the IAM role
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document "$TRUST_POLICY"

# Attach necessary policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess

# Get and output the role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "✅ ECR repository created: $REPO_NAME"
echo "✅ IAM role ARN: $ROLE_ARN"
echo "⚠️  Save this role ARN as a GitHub secret named AWS_APPRUNNER_ECR_ACCESS_ROLE"