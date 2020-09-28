import os
import boto3
import logging
from crhelper import CfnResource
from distutils import util


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


def parse_boolean_values(properties):
  if "AutoEnable" in properties:
    properties["AutoEnable"] = bool(util.strtobool(properties["AutoEnable"]))

  if "DataSources" in properties and "S3Logs" in properties["DataSources"] and "AutoEnable" in properties["DataSources"]["S3Logs"]:
    properties["DataSources"]["S3Logs"]["AutoEnable"] = bool(util.strtobool(properties["DataSources"]["S3Logs"]["AutoEnable"]))

  return properties


@helper.create
@helper.update
def create(event, context):

  configuration = event['ResourceProperties']['OrganizationConfiguration']
  parse_boolean_values(configuration)

  guardduty = boto3.client('guardduty')

  response = guardduty.update_organization_configuration(**configuration)

  logger.info(f"GuardDuty UpdateOrganizationConfiguration Response: {response}")


@helper.delete
def delete(event, context):
  logger.info("Delete is a no-op for GuardDuty Organization Configuration")


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
