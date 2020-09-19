from cloudformation_cli_python_lib import exceptions
from logging import Logger
import mypy_boto3_organizations as Organizations
import time
from typing import cast, get_type_hints, Any, Dict, Optional, Sequence, Type
from .models import ResourceModel


class OrganizationsAccountProvisioner(object):

  TYPE: str = "LittleOrange::Organizations::Account"

  def __init__(self, logger: Logger, organizations: Organizations.Client):
    self.logger = logger
    self.organizations = organizations

  def findAccountByNameOrEmail(self, name: str, email: str):
    pages = self.organizations.get_paginator("list_accounts").paginate()
    for account in [account for page in pages for account in page["Accounts"]]:
      if account["Name"] == name and account["Email"] == email:
        return account
      elif account["Name"] == name or account["Email"] == email:
        raise Exception(f"Existing account with (name={account['Name']} email={account['Email']}) instead of ({name=} {email=})")

    return None

  def listDelegatedAdministratorServices(self, accountId):
    try:
      pages = self.organizations.get_paginator("list_delegated_services_for_account").paginate(AccountId=accountId)
      return [service["ServicePrincipal"] for page in pages for service in page["DelegatedServices"]]
    except self.organizations.exceptions.AccountNotRegisteredException:
      return []
      
  def findOrganizationRoot(self):

    pages = self.organizations.get_paginator('list_roots').paginate()
    roots = [root for page in pages for root in page['Roots']]

    for root in roots:
      if root['Name'] == 'Root':
        return root

    raise Exception('Root with name \'Root\' not found')

  def create(self, desired: ResourceModel):

    # if account already exists execute update path to adopt it into stack
    existingAccount = self.findAccountByNameOrEmail(desired.Name, desired.Email)
    if existingAccount:
      query = ResourceModel._deserialize({
          "Id": existingAccount["Id"]
      })
      existingModel = self.get(query)

      return self.update(existingModel, desired)

    createAccountStatus = self.organizations.create_account(
        AccountName=desired.Name,
        Email=desired.Email,
        IamUserAccessToBilling="ALLOW",
        RoleName="OrganizationAccountAccessRole"
    )["CreateAccountStatus"]

    while createAccountStatus["State"] == "IN_PROGRESS":
      time.sleep(15)
      createAccountStatus = self.organizations.describe_create_account_status(CreateAccountRequestId=createAccountStatus["Id"])["CreateAccountStatus"]

    if createAccountStatus["State"] == "FAILED":
      raise exceptions.InternalFailure(f"Create account request failed with reason: {createAccountStatus.get('FailureReason', 'NONE_PROVIDED')}")

    organizationRootId = self.findOrganizationRoot()["Id"]
    if desired.ParentId:
      self.organizations.move_account(
          AccountId=createAccountStatus["AccountId"],
          SourceParentId=organizationRootId,
          DestinationParentId=desired.ParentId)

    delegatedAdministratorServices = desired.DelegatedAdministratorServices or []
    for service in delegatedAdministratorServices:
      self.organizations.register_delegated_administrator(
          AccountId=createAccountStatus["AccountId"],
          ServicePrincipal=service
      )

    query = ResourceModel._deserialize({
        "Id": createAccountStatus["AccountId"]
    })

    return self.get(query)

  def delete(self, desired: ResourceModel):

    organizationRootId = self.findOrganizationRoot()["Id"]
    account = self.get(desired)

    if account.ParentId != organizationRootId:
      self.organizations.move_account(AccountId=desired.Id, SourceParentId=account.ParentId,
                                      DestinationParentId=organizationRootId)

    delegatedAdministratorServices = self.listDelegatedAdministratorServices(desired.Id)
    for service in delegatedAdministratorServices:
      self.organizations.deregister_delegated_administrator(
          AccountId=desired.Id,
          ServicePrincipal=service
      )


  def get(self, desired: ResourceModel):

    try:
      account = self.organizations.describe_account(AccountId=desired.Id)
    except self.organizations.exceptions.AccountNotFoundException:
      raise exceptions.NotFound(OrganizationsAccountProvisioner.TYPE, desired.Id)

    parents = self.organizations.list_parents(ChildId=desired.Id)

    delegatedAdministratorServices = self.listDelegatedAdministratorServices(desired.Id)

    return ResourceModel._deserialize({
        "Arn": account["Account"]["Arn"],
        "DelegatedAdministratorServices": delegatedAdministratorServices,
        "Email": account["Account"]["Email"],
        "Id": account["Account"]["Id"],
        "Name": account["Account"]["Name"],
        "ParentId": parents["Parents"][0]["Id"],
        "Status": account["Account"]["Status"]
    })

  def update(self, current: ResourceModel, desired: ResourceModel):

    sourceParentId = current.ParentId
    destinationParentId = desired.ParentId

    if not sourceParentId or not destinationParentId:
      organizationRootId = self.findOrganizationRoot()["Id"]

    if not sourceParentId:
      sourceParentId = organizationRootId

    if not destinationParentId:
      destinationParentId = organizationRootId

    if sourceParentId != destinationParentId:
      self.organizations.move_account(AccountId=desired.Id, SourceParentId=sourceParentId,
                                      DestinationParentId=destinationParentId)

    currentDelegatedAdministratorServices = self.listDelegatedAdministratorServices(desired.Id)
    desiredDelegatedAdministratorServices = desired.DelegatedAdministratorServices or []

    servicesToDeregister = set(currentDelegatedAdministratorServices) - set(desiredDelegatedAdministratorServices)
    for service in servicesToDeregister:
      self.organizations.deregister_delegated_administrator(
          AccountId=desired.Id,
          ServicePrincipal=service
      )

    servicesToRegister = set(desiredDelegatedAdministratorServices) - set(currentDelegatedAdministratorServices)
    for service in servicesToRegister:
      self.organizations.register_delegated_administrator(
          AccountId=desired.Id,
          ServicePrincipal=service
      )

    return self.get(desired)
