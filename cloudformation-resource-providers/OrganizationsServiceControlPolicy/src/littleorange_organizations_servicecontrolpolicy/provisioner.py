from cloudformation_cli_python_lib import exceptions
from logging import Logger
import mypy_boto3_organizations as Organizations
from typing import cast, get_type_hints, Any, Dict, Optional, Sequence, Type
from .models import ResourceModel


class OrganizationsServiceControlPolicyProvisioner(object):

  TYPE: str = "LittleOrange::Organizations::ServiceControlPolicy"

  def __init__(self, logger: Logger, organizations: Organizations.Client):
    self.logger = logger
    self.organizations = organizations

  def create(self, desired: ResourceModel):

    scp = self.organizations.create_policy(
        Name=desired.Name,
        Description=desired.Description or "",
        Content=desired.Content,
        Type="SERVICE_CONTROL_POLICY"
    )["Policy"]

    return ResourceModel._deserialize({
        "Arn": scp["PolicySummary"]["Arn"],
        "Description": scp["PolicySummary"]["Description"],
        "Content": scp["Content"],
        "Id": scp["PolicySummary"]["Id"],
        "Name": scp["PolicySummary"]["Name"]
    })

  def delete(self, desired: ResourceModel):

    try:
      self.organizations.delete_policy(PolicyId=desired.Id)
    except self.organizations.exceptions.PolicyNotFoundException:
      raise exceptions.NotFound(OrganizationsServiceControlPolicyProvisioner.TYPE, desired.Id)
    except self.organizations.exceptions.PolicyInUseException:
      raise exceptions.ResourceConflict(f"Policy {desired.Id} cannot be deleted as it is currently in use")

  def get(self, desired: ResourceModel):

    try:
      scp = self.organizations.describe_policy(PolicyId=desired.Id)["Policy"]
    except self.organizations.exceptions.PolicyNotFoundException:
      raise exceptions.NotFound(OrganizationsServiceControlPolicyProvisioner.TYPE, desired.Id)

    return ResourceModel._deserialize({
        "Arn": scp["PolicySummary"]["Arn"],
        "Description": scp["PolicySummary"]["Description"],
        "Content": scp["Content"],
        "Id": scp["PolicySummary"]["Id"],
        "Name": scp["PolicySummary"]["Name"]
    })

  def update(self, current: ResourceModel, desired: ResourceModel):

    try:
      scp = self.organizations.update_policy(
          PolicyId=desired.Id,
          Description=desired.Description,
          Content=desired.Content,
          Name=desired.Name
      )["Policy"]
    except self.organizations.exceptions.PolicyNotFoundException:
      raise exceptions.NotFound(OrganizationsServiceControlPolicyProvisioner.TYPE, desired.Id)

    return ResourceModel._deserialize({
        "Arn": scp["PolicySummary"]["Arn"],
        "Description": scp["PolicySummary"]["Description"],
        "Content": scp["Content"],
        "Id": scp["PolicySummary"]["Id"],
        "Name": scp["PolicySummary"]["Name"]
    })
