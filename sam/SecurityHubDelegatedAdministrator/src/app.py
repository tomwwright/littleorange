import boto3
import logging
from crhelper import CfnResource

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

def assume_role(accountId):
  sts = boto3.client("sts")
  credentials = sts.assume_role(RoleArn=f"arn:aws:iam::{accountId}:role/OrganizationAccountAccessRole", RoleSessionName="SecurityHubDelegatedAdministrator")

  logger.info(f"Assumed OrganizationAccountAccessRole in {accountId} for access key: {credentials['Credentials']['AccessKeyId']}")

  assumed = boto3.Session(
      aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
      aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
      aws_session_token=credentials["Credentials"]["SessionToken"]
  )

  return assumed

def list_organization_accounts():
  organizations = boto3.client("organizations")
  account_ids = [account["Id"] for page in organizations.get_paginator("list_accounts").paginate() for account in page["Accounts"]]
  return account_ids

@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  accountId = event["ResourceProperties"]["AccountId"]
  region = event["ResourceProperties"]["Region"]
  
  securityhub = boto3.client("securityhub", region_name=region)
  response = securityhub.enable_organization_admin_account(AdminAccountId=accountId)
  logger.info(f"SecurityHub EnableOrganizationAdminAccount Response: {response}")

  assumed = assume_role(accountId)
  assumed_securityhub = assumed.client("securityhub", region_name=region)

  response = assumed_securityhub.update_organization_configuration(AutoEnable=True)
  logger.info(f"SecurityHub UpdateOrganizationConfiguration Response: {response}")

  account_ids = list_organization_accounts()
  response = assumed_securityhub.create_members(AccountDetails=[
    {
      "AccountId": id
    }
    for id in account_ids
  ])
  logger.info(f"SecurityHub CreateMembers Response: {response}")



@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  accountId = event["ResourceProperties"]["AccountId"]
  region = event["ResourceProperties"]["Region"]

  securityhub = boto3.client("securityhub", region_name=region)
  try:
    response = securityhub.disable_organization_admin_account(AdminAccountId=accountId)
    logger.info(f"SecurityHub DisableOrganizationAdminAccount Response: {response}")
  except securityhub.exceptions.ResourceNotFoundException:
    logger.info(f"Caught ResourceNotFoundException, continuing...")

def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
