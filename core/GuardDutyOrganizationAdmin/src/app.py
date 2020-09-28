import os
import boto3
import logging
from crhelper import CfnResource


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  accountId = event["ResourceProperties"]["AccountId"]
  guardduty = boto3.client('guardduty')
  response = guardduty.enable_organization_admin_account(AdminAccountId=accountId)

  logger.info(f"GuardDuty EnableOrganizationAdminAccount Response: {response}")


@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  accountId = event["ResourceProperties"]["AccountId"]
  guardduty = boto3.client('guardduty')
  response = guardduty.disable_organization_admin_account(AdminAccountId=accountId)

  logger.info(f"GuardDuty DisableOrganizationAdminAccount Response: {response}")


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
