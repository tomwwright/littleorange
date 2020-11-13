import os
import boto3
import logging
import urllib.request
from crhelper import CfnResource
from distutils import util


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


def assume_role(accountId, region):
  sts = boto3.client("sts")

  identity = sts.get_caller_identity()
  if identity["Account"] == accountId:
    logger.warning(f"Already in Account '{accountId}', not assuming role...")
    return boto3.Session(region_name=region)

  credentials = sts.assume_role(RoleArn=f"arn:aws:iam::{accountId}:role/OrganizationAccountAccessRole", RoleSessionName="IAMSAMLProvider")

  logger.info(f"Assumed OrganizationAccountAccessRole in {accountId} for access key: {credentials['Credentials']['AccessKeyId']}")

  assumed = boto3.Session(
      aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
      aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
      aws_session_token=credentials["Credentials"]["SessionToken"],
      region_name=region
  )

  return assumed


def construct_saml_provider_arn(event):
  saml_provider_metadata_url = event["ResourceProperties"]["SamlProvider"]["MetadataUrl"]
  saml_provider_name = event["ResourceProperties"]["SamlProvider"]["Name"]
  account_id = event["ResourceProperties"]["AccountId"]

  saml_provider_arn = f"arn:aws:iam::{account_id}:saml-provider/{saml_provider_name}"
  return saml_provider_arn


def create_session(event):
  account_id = event["ResourceProperties"]["AccountId"]
  region = event["ResourceProperties"]["Region"]

  session = assume_role(account_id, region)
  return session


def fetch_metadata(metadata_url):
  metadata_response = urllib.request.urlopen(metadata_url)
  metadata = metadata_response.read().decode(metadata_response.headers.get_content_charset())
  return metadata


@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  session = create_session(event)

  saml_provider_metadata_url = event["ResourceProperties"]["SamlProvider"]["MetadataUrl"]
  saml_provider_name = event["ResourceProperties"]["SamlProvider"]["Name"]
  metadata = fetch_metadata(saml_provider_metadata_url)

  iam = session.client("iam")
  response = iam.create_saml_provider(
      SAMLMetadataDocument=metadata,
      Name=saml_provider_name
  )
  logger.debug(f"IAM [ASSUMED] CreateSAMLProvider Response: {response}")

  saml_provider_arn = construct_saml_provider_arn(event)
  return saml_provider_arn


@helper.update
def update(event, context):
  logger.info("Performing UPDATE")

  session = create_session(event)
  saml_provider_arn = construct_saml_provider_arn(event)

  saml_provider_metadata_url = event["ResourceProperties"]["SamlProvider"]["MetadataUrl"]
  metadata = fetch_metadata(saml_provider_metadata_url)

  iam = session.client("iam")
  response = iam.update_saml_provider(
      SAMLMetadataDocument=metadata,
      SAMLProviderArn=saml_provider_arn
  )
  logger.debug(f"IAM [ASSUMED] UpdateSAMLProvider Response: {response}")

  return saml_provider_arn


@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  session = create_session(event)
  saml_provider_arn = construct_saml_provider_arn(event)

  iam = session.client("iam")

  try:
    response = iam.delete_saml_provider(
        SAMLProviderArn=saml_provider_arn
    )
    logger.debug(f"IAM [ASSUMED] DeleteSAMLProvider Response: {response}")
  except iam.exceptions.NoSuchEntityException as e:
    logger.warn(f"Received NoSuchEntityException for DeleteSAMLProvider, continuing...")


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
