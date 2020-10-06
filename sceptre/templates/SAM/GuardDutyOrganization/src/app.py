import os
import boto3
import logging
from crhelper import CfnResource
from distutils import util


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


def assume_role(accountId):
  sts = boto3.client("sts")
  credentials = sts.assume_role(RoleArn=f"arn:aws:iam::{accountId}:role/OrganizationAccountAccessRole", RoleSessionName="GuardDutyOrganization")

  logger.info(f"Assumed OrganizationAccountAccessRole in {accountId} for access key: {credentials['Credentials']['AccessKeyId']}")

  assumed = boto3.Session(
      aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
      aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
      aws_session_token=credentials["Credentials"]["SessionToken"]
  )

  return assumed


def parse_boolean_values(properties):
  if "AutoEnable" in properties:
    properties["AutoEnable"] = bool(util.strtobool(properties["AutoEnable"]))

  if "DataSources" in properties and "S3Logs" in properties["DataSources"] and "AutoEnable" in properties["DataSources"]["S3Logs"]:
    properties["DataSources"]["S3Logs"]["AutoEnable"] = bool(util.strtobool(properties["DataSources"]["S3Logs"]["AutoEnable"]))

  return properties


@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  accountId = event["ResourceProperties"]["AccountId"]
  configuration = event["ResourceProperties"]["OrganizationConfiguration"]
  parse_boolean_values(configuration)

  guardduty = boto3.client("guardduty")
  response = guardduty.enable_organization_admin_account(AdminAccountId=accountId)

  logger.info(f"GuardDuty EnableOrganizationAdminAccount Response: {response}")

  assumed = assume_role(accountId)

  assumedGuardDuty = assumed.client("guardduty")
  response = assumedGuardDuty.list_detectors()

  logger.debug(f"GuardDuty [ASSUMED] ListDetectors Response: {response}")

  configuration["DetectorId"] = response["DetectorIds"][0]
  response = assumedGuardDuty.update_organization_configuration(**configuration)

  logger.info(f"GuardDuty [ASSUMED] UpdateOrganizationConfiguration Response: {response}")

  assumedSsm = assumed.client("ssm")
  response = assumedSsm.put_parameter(
      Name="/LittleOrange/GuardDuty/DetectorId",
      Description="GuardDuty DetectorId configured when account enabled as Organization admin account",
      Value=detectorId,
      Type="String",
      Overwrite=True
  )

  logger.info(f"SSM [ASSUMED] PutParameter Response: {response}")


@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  accountId = event["ResourceProperties"]["AccountId"]
  guardduty = boto3.client('guardduty')
  response = guardduty.disable_organization_admin_account(AdminAccountId=accountId)

  logger.info(f"GuardDuty DisableOrganizationAdminAccount Response: {response}")

  assumed = assume_role(accountId)

  assumedSsm = assumed.client("ssm")
  response = assumedSsm.delete_parameter(
      Name="/LittleOrange/GuardDuty/DetectorId"
  )

  logger.info(f"SSM [ASSUMED] DeleteParameter Response: {response}")


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
