import logging
from typing import cast, Any, List, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

import mypy_boto3_organizations as Organizations

from .models import BaseModel, ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "LittleOrange::Organizations::Organization"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  LOG.info(request)

  model = request.desiredResourceState

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  organizations: Organizations.Client = session.client('organizations')
  organization = organizations.create_organization(
      FeatureSet=cast(Any, request.desiredResourceState.FeatureSet)  # generated model doesn't represent type of enums correctly
  )["Organization"]
  model = ResourceModel._deserialize(organization)

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=model,
  )


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  LOG.info(request)

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations: Organizations.Client = session.client('organizations')

  try:
    organizations.delete_organization()
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    raise exceptions.NotFound(TYPE_NAME, "any")

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=None,
  )


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
  model = request.desiredResourceState

  if not request.desiredResourceState or not request.desiredResourceState.Id:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations: Organizations.Client = session.client('organizations')

  try:
    organization = organizations.describe_organization()["Organization"]
    model = ResourceModel._deserialize(organization)
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    raise exceptions.NotFound(TYPE_NAME, request.desiredResourceState.Id)

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=model,
  )


@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations: Organizations.Client = session.client('organizations')
  models: List[Any] = []

  try:
    organization = organizations.describe_organization()["Organization"]
    models = [ResourceModel._deserialize(organization)]
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    models = []

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModels=models,
  )
