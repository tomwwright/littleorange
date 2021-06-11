import boto3
import logging
from crhelper import CfnResource
from distutils import util


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

SES_REGION = "us-east-1"

@helper.create
def create(event, context):

  domain = event["ResourceProperties"]["DomainName"]
  ses = boto3.client('ses', region_name=SES_REGION)

  response = ses.verify_domain_dkim(
    Domain=domain
  )
  logger.info(f"SES VerifyDomainDkim Response: {response}")

  helper.Data = response

@helper.delete
def delete(event, context):

  domain = event["ResourceProperties"]["DomainName"]
  ses = boto3.client('ses', region_name=SES_REGION)

  response = ses.delete_identity(
    Identity=domain
  )
  logger.info(f"SES DeleteIdentity Response: {response}")


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
