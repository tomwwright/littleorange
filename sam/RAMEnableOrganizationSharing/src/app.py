import os
import boto3
import logging
from crhelper import CfnResource
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  ram = boto3.client("ram")

  response = ram.enable_sharing_with_aws_organization()
  logger.info(f"RAM EnableSharingWithAWSOrganization {response}")


@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  # Delete is no-op as there is no action to disable sharing


@helper.update
def update(event, context):
  logger.info("Performing UPDATE")

  # Update is no-op as there is no action to disable sharing


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
