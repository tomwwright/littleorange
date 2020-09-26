import os
import boto3
import logging
from crhelper import CfnResource


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


@helper.create
@helper.update
def create(event, context):

    name = event['ResourceProperties']['TrailName']
    logger.info(f"Enabling IsOrganizationTrail on '{name}'")

    cloudtrail = boto3.client('cloudtrail')
    response = cloudtrail.update_trail(
        Name=name,
        IsOrganizationTrail=True
    )

    logger.info(f"CloudTrail UpdateTrail Response: {response}")


@helper.delete
def delete(event, context):

    name = event['ResourceProperties']['TrailName']
    logger.info(f"Disabling IsOrganizationTrail on '{name}'")

    cloudtrail = boto3.client('cloudtrail')
    response = cloudtrail.update_trail(
        Name=name,
        IsOrganizationTrail=False
    )

    logger.info(f"CloudTrail UpdateTrail Response: {response}")


def handler(event, context):
    logger.info(f"Received event: {event}")
    helper(event, context)
