from cloudformation_cli_python_lib import SessionProxy, exceptions
from logging import Logger
import mypy_boto3_organizations as Organizations
from typing import cast, get_type_hints, Any, Dict, Optional, Sequence, Type
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

  TYPE: str = "LittleOrange::Organizations::Organization"

  def __init__(self, logger: Logger, organizations: Organizations.Client):
    self.logger = logger
    self.organizations = organizations

  def findRoot(self):

    pages = self.organizations.get_paginator('list_roots').paginate()
    roots = [root for page in pages for root in page['Roots']]

    for root in roots:
      if root['Name'] == 'Root':
        return root

    raise Exception('Root with name \'Root\' not found')

  def __handleEnabledPolicyTypes(self, desired: ResourceModel):
    if not desired.EnabledPolicyTypes:
      policyTypes = []
    else:
      policyTypes = [policy.Type for policy in desired.EnabledPolicyTypes]

    root = self.__setEnabledPolicyTypes(policyTypes)

    return root

  def __handleEnabledAWSServices(self, desired: ResourceModel):
    desiredServiceObjects = desired.EnabledServices or []
    desiredServices = [service.ServicePrincipal for service in desiredServiceObjects]

    services = self.__setEnabledAWSServices(desiredServices)
    return services

  def __listEnabledAWSServices(self):
    pages = self.organizations.get_paginator("list_aws_service_access_for_organization").paginate()
    services = [{
        "ServicePrincipal": service["ServicePrincipal"]
    } for page in pages for service in page["EnabledServicePrincipals"]]

    return services

  def __setEnabledPolicyTypes(self, policyTypes: Sequence[Optional[str]]):
    root = self.findRoot()

    enabledPolicyTypes = [policy['Type'] for policy in root['PolicyTypes'] if policy['Status'] == 'ENABLED']

    policyTypesToDisable = [policy for policy in enabledPolicyTypes if policy not in policyTypes]
    policyTypesToEnable = [policy for policy in policyTypes if policy not in enabledPolicyTypes]

    for policy in policyTypesToDisable:
      self.organizations.disable_policy_type(
          RootId=root['Id'],
          PolicyType=policy
      )

    for policy in policyTypesToEnable:
      self.organizations.enable_policy_type(
          RootId=root['Id'],
          PolicyType=policy
      )

    # return refreshed to reflect policy changes
    return self.findRoot()
  
  def __setEnabledAWSServices(self, desiredServices: Sequence[Optional[str]]):
    currentServices = [service["ServicePrincipal"] for service in self.__listEnabledAWSServices()]

    servicesToDisable = [service for service in currentServices if service not in desiredServices]
    servicesToEnable = [service for service in desiredServices if service not in currentServices]

    for service in servicesToDisable:
      self.organizations.disable_aws_service_access(ServicePrincipal=service)

    for service in servicesToEnable:
      self.organizations.enable_aws_service_access(ServicePrincipal=service)

    return self.__listEnabledAWSServices()


  def create(self, desired: ResourceModel) -> ResourceModel:

    organizations: Organizations.Client = self.boto3.client('organizations')

    response = organizations.create_organization(
        FeatureSet=cast(Any, desired.FeatureSet)  # generated model doesn't represent type of enums correctly
    )

    root = self.__handleEnabledPolicyTypes(organizations, desired)
    services = self.__handleEnabledAWSServices(organizations, desired)

    modelData: Any = {
        **response['Organization'],
        'RootId': root['Id'],
        'EnabledPolicyTypes': [{'Type': policy['Type']} for policy in root['PolicyTypes'] if policy['Status'] == 'ENABLED'],
        'EnabledServices': services
    }

    return safeDeserialise(ResourceModel, modelData)

  def delete(self):

    try:
      self.organizations.delete_organization()
    except self.organizations.exceptions.AWSOrganizationsNotInUseException:
      raise exceptions.NotFound(OrganizationsOrganizationProvisioner.TYPE, "NoID")

  def get(self, desired: ResourceModel) -> ResourceModel:

    try:
      organization = self.organizations.describe_organization()["Organization"]
      root = self.findRoot()
      services = self.__listEnabledAWSServices()
    except self.organizations.exceptions.AWSOrganizationsNotInUseException:
      raise exceptions.NotFound(self.TYPE, desired.Id or 'NoID')

    modelData: Any = {
        **organization,
        'RootId': root['Id'],
        'EnabledPolicyTypes': [{'Type': policy['Type']} for policy in root['PolicyTypes'] if policy['Status'] == 'ENABLED'],
        'EnabledServices': services
    }

    return safeDeserialise(ResourceModel, modelData)

  def listResources(self) -> Sequence[ResourceModel]:

    desired = ResourceModel._deserialize({})

    return [self.get(desired)]

  def update(self, current: ResourceModel, desired: ResourceModel) -> ResourceModel:

    self.__handleEnabledPolicyTypes(desired)
    self.__handleEnabledAWSServices(desired)

    modelData: Any = {
        **current._serialize(),
        **desired._serialize()
    }

    return safeDeserialise(ResourceModel, modelData)
