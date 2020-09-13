from cloudformation_cli_python_lib import SessionProxy, exceptions
from logging import Logger
import mypy_boto3_organizations as Organizations
from typing import cast, get_type_hints, Any, Dict, Optional, Sequence, Type
from .models import ResourceModel


class OrganizationsOrganizationalUnitProvisioner(object):

  TYPE: str = "LittleOrange::Organizations::OrganizationalUnit"

  DEFAULT_POLICY_IDS = [
      "p-FullAWSAccess"
  ]

  def __init__(self, logger: Logger, organizations: Organizations.Client):
    self.logger = logger
    self.organizations = organizations

  def __listServiceControlPolicyIds(self, organizationalUnitId) -> Sequence[str]:

    paginator = self.organizations.get_paginator("list_policies_for_target")
    parameters = {
        "TargetId": organizationalUnitId,
        "Filter": "SERVICE_CONTROL_POLICY"
    }

    policies = []
    for page in paginator.paginate(**parameters):
      policies += page["Policies"]

    return [policy["Id"] for policy in policies]

  def __updateServiceControlPolicyIds(self, organizationalUnitId, desiredPolicyIds):

    currentPolicyIds = self.__listServiceControlPolicyIds(organizationalUnitId)

    policyIdsToDetach = set(currentPolicyIds) - set(desiredPolicyIds)
    for policyId in policyIdsToDetach:
      self.organizations.detach_policy(
          PolicyId=policyId,
          TargetId=organizationalUnitId
      )

    policyIdsToAttach = set(desiredPolicyIds) - set(currentPolicyIds)
    for policyId in policyIdsToAttach:
      self.organizations.attach_policy(
          PolicyId=policyId,
          TargetId=organizationalUnitId
      )

  def create(self, desired: ResourceModel) -> ResourceModel:

    ou = self.organizations.create_organizational_unit(
        ParentId=desired.ParentId,
        Name=desired.Name
    )

    policyIds = desired.PolicyIds if desired.PolicyIds != None else self.DEFAULT_POLICY_IDS

    self.__updateServiceControlPolicyIds(ou["OrganizationalUnit"]["Id"], policyIds)

    return ResourceModel._deserialize({
        "Arn": ou["OrganizationalUnit"]["Arn"],
        "Id": ou["OrganizationalUnit"]["Id"],
        "Name": ou["OrganizationalUnit"]["Name"],
        "ParentId": desired.ParentId,
        "PolicyIds": policyIds
    })

  def delete(self, desired: ResourceModel):

    try:
      self.organizations.delete_organizational_unit(OrganizationalUnitId=desired.Id)
    except self.organizations.exceptions.OrganizationalUnitNotFoundException:
      raise exceptions.NotFound(self.TYPE, desired.Id)
    except self.organizations.exceptions.OrganizationalUnitNotEmptyException:
      raise exceptions.ResourceConflict(f"Organizational Unit {desired.Id} cannot be deleted as it is not empty")

  def get(self, desired: ResourceModel) -> ResourceModel:

    ou = self.organizations.describe_organizational_unit(OrganizationalUnitId=desired.Id)
    parents = self.organizations.list_parents(ChildId=desired.Id)
    policyIds = self.__listServiceControlPolicyIds(desired.Id)

    return ResourceModel._deserialize({
        "Arn": ou["OrganizationalUnit"]["Arn"],
        "Id": ou["OrganizationalUnit"]["Id"],
        "Name": ou["OrganizationalUnit"]["Name"],
        "ParentId": parents["Parents"][0]["Id"],
        "PolicyIds": policyIds
    })

  def update(self, current: ResourceModel, desired: ResourceModel) -> ResourceModel:

    if current.Name != desired.Name:
      try:
        self.organizations.update_organizational_unit(
            OrganizationalUnitId=desired.Id,
            Name=desired.Name
        )
      except self.organizations.exceptions.OrganizationalUnitNotFoundException:
        raise exceptions.NotFound(self.TYPE, desired.Id)

    policyIds = desired.PolicyIds if desired.PolicyIds != None else self.DEFAULT_POLICY_IDS

    self.__updateServiceControlPolicyIds(desired.Id, policyIds)

    return self.get(desired)
