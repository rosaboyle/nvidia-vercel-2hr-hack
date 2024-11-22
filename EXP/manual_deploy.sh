#!/bin/bash
# save as: manual-deploy.sh

# Variables
REGION="us-west-2"
REPO_NAME="nvda-2hr"
SERVICE_NAME="nvda-2hr"
ARCHITECTURE="arm64"  # Explicitly set architecture

# Ensure AWS_APPRUNNER_ECR_ACCESS_ROLE is set
if [ -z "$AWS_APPRUNNER_ECR_ACCESS_ROLE" ]; then
    echo "Error: AWS_APPRUNNER_ECR_ACCESS_ROLE environment variable is not set"
    exit 1
fi

echo "🚀 Starting deployment process..."
echo "⚙️  Architecture: ARM64"

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

echo "📦 Building and pushing Docker image..."

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO

# Build and push image with platform specified
docker build --platform linux/arm64 -t ${REPO_NAME}:latest .
docker tag ${REPO_NAME}:latest ${ECR_REPO}:latest-arm64
docker push ${ECR_REPO}:latest-arm64

echo "🚀 Deploying to App Runner..."

# Deploy to App Runner with ARM64 runtime
aws apprunner create-service \
  --region $REGION \
  --service-name $SERVICE_NAME \
  --source-configuration "{
    \"AuthenticationConfiguration\": {
      \"AccessRoleArn\": \"${AWS_APPRUNNER_ECR_ACCESS_ROLE}\"
    },
    \"AutoDeploymentsEnabled\": true,
    \"ImageRepository\": {
      \"ImageIdentifier\": \"${ECR_REPO}:latest-arm64\",
      \"ImageRepositoryType\": \"ECR\",
      \"ImageConfiguration\": {
        \"Port\": \"8000\",
        \"RuntimeEnvironmentVariables\": {
          \"ARCHITECTURE\": \"arm64\"
        }
      }
    }
  }" \
  --instance-configuration "{
    \"Cpu\": \"1024\",
    \"Memory\": \"2048\",
    \"InstanceRoleArn\": \"$