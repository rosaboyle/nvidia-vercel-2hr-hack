# main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

# EventBridge rule to detect ECR image pushes
resource "aws_cloudwatch_event_rule" "ecr_image_push" {
  name        = "nvda-2hr-ecr-push-rule"
  description = "Capture ECR Image Push for nvda-2hr repository"

  event_pattern = jsonencode({
    source      = ["aws.ecr"]
    detail-type = ["ECR Image Action"]
    detail = {
      action-type = ["PUSH"]
      result      = ["SUCCESS"]
      repository-name = ["nvda-2hr"]
    }
  })
}

# IAM role for EventBridge
resource "aws_iam_role" "eventbridge_role" {
  name = "nvda-2hr-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda function for deployment
resource "aws_lambda_function" "deploy_handler" {
  filename         = "deploy_handler.zip"
  function_name    = "nvda-2hr-deploy-handler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "deploy_handler.handler"
  runtime         = "python3.11"
  timeout         = 300  # 5 minutes timeout
  memory_size     = 256

  environment {
    variables = {
      ECS_CLUSTER  = "nvda-2hr"
      ECS_SERVICE  = "nvda-2hr"
    }
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "nvda-2hr-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda permission policy
resource "aws_iam_role_policy" "lambda_policy" {
  name = "nvda-2hr-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:ListTasks",
          "ecs:DescribeTasks",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Connect EventBridge to Lambda
resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.ecr_image_push.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.deploy_handler.arn
}

# Allow EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.deploy_handler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ecr_image_push.arn
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/nvda-2hr-deploy-handler"
  retention_in_days = 14
}