#!/bin/bash
# save as: manual-deploy.sh

# Variables
REGION="us-west-2"
REPO_NAME="nvda-2hr"
SERVICE_NAME="nvda-2hr"

# Ensure AWS_APPRUNNER_ECR_ACCESS_ROLE is set
if [ -z "$AWS_APPRUNNER_ECR_ACCESS_ROLE" ]; then
    echo "Error: AWS_APPRUNNER_ECR_ACCESS_ROLE environment variable is not set"
    exit 1
fi

echo "🚀 Starting deployment process..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

echo "📦 Building and pushing Docker image..."

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO

# Build and push image
docker build -t ${REPO_NAME}:latest .
docker tag ${REPO_NAME}:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest

echo "🚀 Deploying to App Runner..."

# Deploy to App Runner
aws apprunner create-service \
  --region $REGION \
  --service-name $SERVICE_NAME \
  --source-configuration "{
    \"AuthenticationConfiguration\": {
      \"AccessRoleArn\": \"${AWS_APPRUNNER_ECR_ACCESS_ROLE}\"
    },
    \"AutoDeploymentsEnabled\": true,
    \"ImageRepository\": {
      \"ImageIdentifier\": \"${ECR_REPO}:latest\",
      \"ImageRepositoryType\": \"ECR\",
      \"ImageConfiguration\": {
        \"Port\": \"8000\"
      }
    }
  }" \
  --instance-configuration "{
    \"Cpu\": \"1024\",
    \"Memory\": \"2048\"
  }"

echo "⏳ Waiting for deployment to complete..."

# Wait and get URL
aws apprunner wait service-updated --service-name $SERVICE_NAME --region $REGION
URL=$(aws apprunner describe-service --service-name $SERVICE_NAME --region $REGION --query "Service.ServiceUrl" --output text)
echo "✅ Application deployed to https://${URL}"