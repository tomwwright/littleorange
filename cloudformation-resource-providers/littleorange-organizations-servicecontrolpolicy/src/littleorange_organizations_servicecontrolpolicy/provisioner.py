from cloudformation_cli_python_lib import SessionProxy, exceptions
from logging import Logger
import mypy_boto3_organizations as Organizations
from typing import cast, get_type_hints, Any, Dict, Optional, Sequence, Type
from .models import ResourceModel


class OrganizationsServiceControlPolicyProvisioner(object):

  TYPE: str = "LittleOrange::Organizations::ServiceControlPolicy"

  def __init__(self, logger: Logger, boto3: SessionProxy):
    self.logger = logger
    self.boto3 = boto3

  def create(self, desired: ResourceModel):

    organizations: Organizations.Client = self.boto3.client('organizations')

    scp = organizations.create_policy(
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
