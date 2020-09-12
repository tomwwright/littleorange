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

  def get(self, desired: ResourceModel) -> ResourceModel:

    ou = self.organizations.describe_organizational_unit(OrganizationalUnitId=desired.Id)
    parents = self.organizations.list_parents(ChildId=desired.Id)

    return ResourceModel._deserialize({
        "Arn": ou["OrganizationalUnit"]["Arn"],
        "Id": ou["OrganizationalUnit"]["Id"],
        "Name": ou["OrganizationalUnit"]["Name"],
        "ParentId": parents["Parents"][0]["Id"]
    })
