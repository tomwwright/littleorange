import os
import boto3
import logging
from crhelper import CfnResource
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


class PortfolioShareError(RuntimeError):
  """Portfolio share operation finished with COMPLETED_WITH_ERRORS status"""


def assume_role(accountId, region, role_session_name):
  sts = boto3.client("sts")

  identity = sts.get_caller_identity()
  if identity["Account"] == accountId:
    logger.warning(f"Already in Account '{accountId}', not assuming role...")
    return boto3.Session(region_name=region)

  credentials = sts.assume_role(RoleArn=f"arn:aws:iam::{accountId}:role/OrganizationAccountAccessRole", RoleSessionName=role_session_name)

  logger.info(f"Assumed OrganizationAccountAccessRole in {accountId} for access key: {credentials['Credentials']['AccessKeyId']}")

  assumed = boto3.Session(
      aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
      aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
      aws_session_token=credentials["Credentials"]["SessionToken"],
      region_name=region
  )

  return assumed


def create_session(event):
  account_id = event["ResourceProperties"]["AccountId"]
  region = event["ResourceProperties"]["Region"]

  session = assume_role(account_id, region, "ServiceCatalogOrganizationPortfolioShare")
  return session


def get_share_configuration(event):
  return event["ResourceProperties"]["PortfolioShareConfiguration"]


def handle_portfolio_share_token(service_catalog, token):
  is_pending = True
  response = None
  while is_pending:
    response = service_catalog.describe_portfolio_share_status(
        PortfolioShareToken=token
    )

    logger.info(f"ServiceCatalog DescribePortfolioShareStatus {response}")

    if response["Status"] in ["NOT_STARTED", "IN_PROGRESS"]:
      logger.info(f"Sleeping as Status is {response['Status']}")
      time.sleep(3)
    else:
      is_pending = False

  if "ERROR" in response["Status"]:
    raise PortfolioShareError(response)


@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  session = create_session(event)
  service_catalog = session.client("servicecatalog")

  config = get_share_configuration(event)
  parameters = {
      "OrganizationNode": {
          "Type": "ORGANIZATION" if config["OrganizationNodeId"].startswith("o-") else "ORGANIZATIONAL_UNIT",
          "Value": config["OrganizationNodeId"]
      },
      "PortfolioId": config["PortfolioId"]
  }

  response = service_catalog.create_portfolio_share(**parameters)
  logger.info(f"ServiceCatalog CreatePortfolioShare {response}")
  token = response["PortfolioShareToken"]

  handle_portfolio_share_token(service_catalog, token)

  return token


@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  session = create_session(event)

  service_catalog = session.client("servicecatalog")

  config = get_share_configuration(event)
  parameters = {
      "OrganizationNode": {
          "Type": "ORGANIZATION" if config["OrganizationNodeId"].startswith("o-") else "ORGANIZATIONAL_UNIT",
          "Value": config["OrganizationNodeId"]
      },
      "PortfolioId": config["PortfolioId"],
  }

  response = service_catalog.delete_portfolio_share(**parameters)
  logger.info(f"ServiceCatalog DeletePortfolioShare {response}")
  token = response["PortfolioShareToken"]

  handle_portfolio_share_token(service_catalog, token)

  return token


@helper.update
def update(event, context):
  logger.info("Performing UPDATE via DELETE and CREATE")

  delete(event, context)
  return create(event, context)


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
