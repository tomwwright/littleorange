import os
import boto3
import logging
from crhelper import CfnResource
from distutils import util


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

COST_USAGE_REPORTS_SERVICE_REGION = "us-east-1"


def parseReportDefinition(event):

  name = event["ResourceProperties"]["ReportName"]
  definition = event["ResourceProperties"]["ReportDefinition"]
  definition["ReportName"] = name

  if "RefreshClosedReports" in definition:
    definition["RefreshClosedReports"] = bool(util.strtobool(definition["RefreshClosedReports"]))

  return name, definition


@helper.create
def create(event, context):

  name, definition = parseReportDefinition(event)
  logger.info(f"Creating report definition '{name}'")

  costusagereports = boto3.client('cur', region_name=COST_USAGE_REPORTS_SERVICE_REGION)
  response = costusagereports.put_report_definition(
      ReportDefinition=definition
  )

  logger.info(f"CUR PutReportDefinition Response: {response}")


@helper.update
def update(event, context):

  name, definition = parseReportDefinition(event)
  logger.info(f"Updating report definition '{name}'")

  costusagereports = boto3.client('cur', region_name=COST_USAGE_REPORTS_SERVICE_REGION)
  response = costusagereports.modify_report_definition(
      ReportName=name,
      ReportDefinition=definition
  )

  logger.info(f"CUR ModifyReportDefinition Response: {response}")


@helper.delete
def delete(event, context):

  name = event['ResourceProperties']['ReportName']
  logger.info(f"Deleting report definition '{name}'")

  costusagereports = boto3.client('cur', region_name=COST_USAGE_REPORTS_SERVICE_REGION)
  response = costusagereports.delete_report_definition(
      ReportName=name
  )

  logger.info(f"CUR DeleteReportDefinition Response: {response}")


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
