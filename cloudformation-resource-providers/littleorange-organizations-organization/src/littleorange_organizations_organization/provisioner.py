from cloudformation_cli_python_lib import SessionProxy
from logging import Logger
import mypy_boto3_organizations as Organizations
from typing import cast, Any, Dict, get_type_hints, Type
from .models import ResourceModel


def selectOnlyValidKeys(typeHinted: Any, json: Dict):
  """
  Uses a typing helper to exclude keys from a dict that are not defined in the dataclass
  """

  validKeys = [k for k, v in get_type_hints(typeHinted).items()]
  return {k: v for k, v in json.items() if k in validKeys}


def safeDeserialise(cls: Type[ResourceModel], data: Dict) -> ResourceModel:
  safeData = selectOnlyValidKeys(ResourceModel, data)
  model = cast(ResourceModel, ResourceModel._deserialize(safeData))

  return model


class OrganizationsOrganizationProvisioner(object):

  def __init__(self, logger: Logger, boto3: SessionProxy):
    self.logger = logger
    self.boto3 = boto3

  def __findRoot(self, organizations):

    pages = organizations.get_paginator('list_roots').paginate()
    roots = [root for page in pages for root in page['Roots']]

    for root in roots:
      if root['Name'] == 'Root':
        return root

    raise Exception('Root with name \'Root\' not found')

  def __setEnabledPolicyTypes(self, organizations, policyTypes):
    root = self.__findRoot(organizations)

    enabledPolicyTypes = [policy['Type'] for policy in root['PolicyTypes'] if policy['Status'] == 'ENABLED']

    policyTypesToDisable = [policy for policy in enabledPolicyTypes if policy not in policyTypes]
    policyTypesToEnable = [policy for policy in policyTypes if policy not in enabledPolicyTypes]

    for policy in policyTypesToDisable:
      organizations.disable_policy_type(
          RootId=root['Id'],
          PolicyType=policy
      )

    for policy in policyTypesToEnable:
      organizations.enable_policy_type(
          RootId=root['Id'],
          PolicyType=policy
      )

  def create(self, desired: ResourceModel) -> ResourceModel:

    organizations: Organizations.Client = self.boto3.client('organizations')

    response = organizations.create_organization(
        FeatureSet=cast(Any, desired.FeatureSet)  # generated model doesn't represent type of enums correctly
    )

    if not desired.EnabledPolicyTypes:
      policyTypes = []
    else:
      policyTypes = [policy.Type for policy in desired.EnabledPolicyTypes]

    self.__setEnabledPolicyTypes(organizations, policyTypes)

    data: Any = {
        **response['Organization'],
        'EnabledPolicyTypes': [policyType._serialize() for policyType in (desired.EnabledPolicyTypes or [])]
    }

    return safeDeserialise(ResourceModel, data)
