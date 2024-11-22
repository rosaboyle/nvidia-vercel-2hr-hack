# deploy_handler.py
import boto3
import os
import json
import time
import logging
from typing import Any, Dict

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def wait_for_service_stability(ecs_client: Any, cluster: str, service: str) -> bool:
    """
    Wait for ECS service to become stable after deployment

    Args:
        ecs_client: Boto3 ECS client
        cluster: Name of the ECS cluster
        service: Name of the ECS service

    Returns:
        bool: True if service stabilized, False otherwise
    """
    logger.info(f"Waiting for service {service} to become stable")
    waiter = ecs_client.get_waiter("services_stable")
    try:
        waiter_config: Dict[str, int] = {"Delay": 15, "MaxAttempts": 40}
        waiter.wait(cluster=cluster, services=[service], WaiterConfig=waiter_config)
        return True
    except Exception as e:
        logger.error(f"Error waiting for service stability: {str(e)}")
        return False


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing ECR push events and triggering ECS deployments

    Args:
        event: AWS Lambda event object containing ECR push details
        context: AWS Lambda context object

    Returns:
        Dict[str, Any]: Response object with status code and deployment results

    Raises:
        Exception: If deployment fails or service fails to stabilize
    """
    logger.info("Received event: " + json.dumps(event))

    # Extract image details from the ECR push event
    repository: str = event["detail"]["repository-name"]
    registry: str = event["detail"]["repository-name"]
    image_tag: str = event["detail"].get("image-tag", "latest")

    # Get the region from Lambda environment
    region = context.invoked_function_arn.split(":")[3]

    # Initialize ECS client
    ecs: Any = boto3.client("ecs", region_name=region)
    cluster_name: str = os.environ["ECS_CLUSTER"]
    service_name: str = os.environ["ECS_SERVICE"]

    try:
        # Get current service details
        service_desc: Dict[str, Any] = ecs.describe_services(
            cluster=cluster_name, services=[service_name]
        )["services"][0]

        logger.info(f"Triggering deployment for service {service_name}")

        # Force new deployment
        response: Dict[str, Any] = ecs.update_service(
            cluster=cluster_name, service=service_name, forceNewDeployment=True
        )

        # Wait for service to become stable
        if wait_for_service_stability(ecs, cluster_name, service_name):
            logger.info("Service deployment completed successfully")

            deployment_result: Dict[str, str] = {
                "message": "Deployment completed successfully",
                "service": service_name,
                "cluster": cluster_name,
            }

            return {"statusCode": 200, "body": json.dumps(deployment_result)}
        else:
            raise Exception("Service failed to stabilize within the expected timeframe")

    except Exception as e:
        error_message: str = f"Error during deployment: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)
