#!/bin/bash

# AWS Configuration Variables
AWS_REGION="us-west-2"
ECR_REPOSITORY="767398153015.dkr.ecr.us-west-2.amazonaws.com/nvda-2hr"
IMAGE_TAG="d3fc9db20861f5e5663249470a99fc95d837d7f4"
CLUSTER_NAME="fastapi-cluster"
SERVICE_NAME="nvda2"

echo "Starting deployment process..."

# Get current service info to extract task definition
CURRENT_TASK_DEFINITION=$(aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --query 'services[0].taskDefinition' \
    --output text)

echo "Current task definition: $CURRENT_TASK_DEFINITION"

# Get task definition family
TASK_FAMILY=$(aws ecs describe-task-definition \
    --task-definition $CURRENT_TASK_DEFINITION \
    --query 'taskDefinition.family' \
    --output text)

echo "Task family: $TASK_FAMILY"

# Register new task definition
aws ecs register-task-definition \
    --family $TASK_FAMILY \
    --cli-input-json "$(aws ecs describe-task-definition \
        --task-definition $CURRENT_TASK_DEFINITION \
        --query 'taskDefinition | {
            containerDefinitions: containerDefinitions,
            family: family,
            taskRoleArn: taskRoleArn,
            executionRoleArn: executionRoleArn,
            networkMode: networkMode,
            volumes: volumes,
            placementConstraints: placementConstraints,
            requiresCompatibilities: requiresCompatibilities,
            cpu: cpu,
            memory: memory
        }' \
        --output json)" > /dev/null

# Get the new task definition revision
NEW_TASK_DEFINITION="${TASK_FAMILY}:$(aws ecs describe-task-definition \
    --task-definition $TASK_FAMILY \
    --query 'taskDefinition.revision' \
    --output text)"

echo "New task definition: $NEW_TASK_DEFINITION"

# Update the service
echo "Updating ECS service..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --task-definition $NEW_TASK_DEFINITION \
    --force-new-deployment

echo "Deployment initiated. Waiting for service to stabilize..."

# Wait for deployment to complete
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME

echo "Deployment completed successfully!"

# Verify the deployment
NEW_RUNNING_COUNT=$(aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --query 'services[0].runningCount' \
    --output text)

echo "Current running tasks: $NEW_RUNNING_COUNT"