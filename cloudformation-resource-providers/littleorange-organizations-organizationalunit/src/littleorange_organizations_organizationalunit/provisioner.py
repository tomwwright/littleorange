from cloudformation_cli_python_lib import SessionProxy, exceptions
from logging import Logger
import mypy_boto3_organizations as Organizations
from typing import cast, get_type_hints, Any, Dict, Optional, Sequence, Type
from .models import ResourceModel


class OrganizationsOrganizationalUnitProvisioner(object):

  TYPE: str = "LittleOrange::Organizations::OrganizationalUnit"

  def __init__(self, logger: Logger, organizations: Organizations.Client):
    self.logger = logger
    self.organizations = organizations

  def create(self, desired: ResourceModel) -> ResourceModel:

    ou = self.organizations.create_organizational_unit(
        ParentId=desired.ParentId,
        Name=desired.Name
    )

    return ResourceModel._deserialize({
        "Arn": ou["OrganizationalUnit"]["Arn"],
        "Id": ou["OrganizationalUnit"]["Id"],
        "Name": ou["OrganizationalUnit"]["Name"],
        "ParentId": desired.ParentId
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

    return ResourceModel._deserialize({
        "Arn": ou["OrganizationalUnit"]["Arn"],
        "Id": ou["OrganizationalUnit"]["Id"],
        "Name": ou["OrganizationalUnit"]["Name"],
        "ParentId": parents["Parents"][0]["Id"]
    })

  def update(self, current: ResourceModel, desired: ResourceModel) -> ResourceModel:

    try:
      self.organizations.update_organizational_unit(
          OrganizationalUnitId=desired.Id,
          Name=desired.Name
      )
    except self.organizations.exceptions.OrganizationalUnitNotFoundException:
      raise exceptions.NotFound(self.TYPE, desired.Id)

    return self.get(desired)
