import os
import boto3
import logging
from crhelper import CfnResource
from distutils import util


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)


def assumeRole(accountId):
  """
  Assumes OrganizationAccountAccessRole in the target account. If current account is already
  the target account assuming role is skipped
  """

  sts = boto3.client("sts")

  identity = sts.get_caller_identity()
  if identity["Account"] == accountId:
    logger.warning(f"Already in Account '{accountId}', not assuming role...")
    return boto3.Session()

  credentials = sts.assume_role(RoleArn=f"arn:aws:iam::{accountId}:role/OrganizationAccountAccessRole", RoleSessionName="SecurityHubOnboarding")

  logger.info(f"Assumed OrganizationAccountAccessRole in {accountId} for access key: {credentials['Credentials']['AccessKeyId']}")

  assumed = boto3.Session(
      aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
      aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
      aws_session_token=credentials["Credentials"]["SessionToken"]
  )

  return assumed


def findAccountEmail(accountId, region):
  """
  Uses DescribeAccount of Organizations to determine the email address associated with accountId
  """

  organizations = boto3.client("organizations", region_name=region)
  response = organizations.describe_account(AccountId=accountId)
  logger.info(f"Organizations DescribeAccount Response: {response}")

  return response["Account"]["Email"]


def acceptInvite(masterAccountId, memberAccountId, region):
  """
  Assume role in member account and locate and accept invitation from master account
  """

  assumedMemberSession = assumeRole(memberAccountId)
  memberSecurityHub = assumedMemberSession.client("securityhub", region_name=region)

  pages = memberSecurityHub.get_paginator("list_invitations").paginate()
  invitations = [invitation for page in pages for invitation in page["Invitations"] if invitation["AccountId"] == masterAccountId]

  if invitations == []:
    raise Exception(f"No invitation from Account ID '{masterAccountId}' found!")

  invitationId = invitations[0]["InvitationId"]
  response = memberSecurityHub.accept_invitation(MasterId=masterAccountId, InvitationId=invitationId)
  logger.info(f"SecurityHub AcceptInvitation Response: {response}")


def createMemberAndInvite(masterAccountId, memberAccountId, region):
  """
  Assume role in master account to create and invite member
  """

  memberAccountEmail = findAccountEmail(memberAccountId, region)
  assumedMasterSession = assumeRole(masterAccountId)
  masterSecurityHub = assumedMasterSession.client("securityhub", region_name=region)

  response = masterSecurityHub.create_members(AccountDetails=[dict(AccountId=memberAccountId, Email=memberAccountEmail)])
  logger.info(f"SecurityHub CreateMembers Response: {response}")

  response = masterSecurityHub.invite_members(AccountIds=[memberAccountId])
  logger.info(f"SecurityHub InviteMembers Response: {response}")


def removeMember(masterAccountId, memberAccountId, region):
  """
  Assume role in master account to disassociate and delete member
  """

  assumedMasterSession = assumeRole(masterAccountId)
  masterSecurityHub = assumedMasterSession.client("securityhub", region_name=region)

  try:
    response = masterSecurityHub.disassociate_members(AccountIds=[memberAccountId])
  except masterSecurityHub.exceptions.ResourceNotFoundException as e:
    logger.warn(f"Received ResourceNotFoundException for DisassociateMembers for AccountId {memberAccountId}, continuing...")
  finally:
    logger.info(f"SecurityHub DisassociateMembers Response: {response}")

  try:
    response = masterSecurityHub.delete_members(AccountIds=[memberAccountId])
  except masterSecurityHub.exceptions.ResourceNotFoundException as e:
    logger.warn(f"Received ResourceNotFoundException for DeleteMembers for AccountId {memberAccountId}, continuing...")
  finally:
    logger.info(f"SecurityHub DeleteMembers Response: {response}")


@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  accountId = event["ResourceProperties"]["AccountId"]
  masterAccountId = event["ResourceProperties"]["MasterAccountId"]
  region = event["ResourceProperties"]["Region"]

  createMemberAndInvite(masterAccountId, accountId, region)
  acceptInvite(masterAccountId, accountId, region)


@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  accountId = event["ResourceProperties"]["AccountId"]
  masterAccountId = event["ResourceProperties"]["MasterAccountId"]
  region = event["ResourceProperties"]["Region"]

  removeMember(masterAccountId, accountId, region)


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
