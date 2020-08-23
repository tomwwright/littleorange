import logging
from typing import Any, List, MutableMapping, Optional

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
TYPE_NAME = "AWS::Organizations::Organization"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
  model = request.desiredResourceState
  progress: ProgressEvent = ProgressEvent(
      status=OperationStatus.IN_PROGRESS,
      resourceModel=model,
  )
  # TODO: put code here

  # Example:
  try:
    if isinstance(session, SessionProxy):
      client = session.client("s3")
    # Setting Status to success will signal to cfn that the operation is complete
    progress.status = OperationStatus.SUCCESS
  except TypeError as e:
    # exceptions module lets CloudFormation know the type of failure that occurred
    raise exceptions.InternalFailure(f"was not expecting type {e}")
    # this can also be done by returning a failed progress event
    # return ProgressEvent.failed(HandlerErrorCode.InternalFailure, f"was not expecting type {e}")
  return progress


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
  model = request.desiredResourceState
  progress: ProgressEvent = ProgressEvent(
      status=OperationStatus.IN_PROGRESS,
      resourceModel=model,
  )
  # TODO: put code here
  return progress


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
  model = request.desiredResourceState

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations: Organizations.Client = session.client('organizations')
  model = None

  try:
    organization = organizations.describe_organization()
    model = ResourceModel._deserialize(organization["Organization"])]
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    pass

  return ProgressEvent(
      status = OperationStatus.SUCCESS,
      resourceModel = model,
  )


@ resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],


) -> ProgressEvent:

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations: Organizations.Client=session.client('organizations')
  models: List[Any]=[]

  try:
    organization=organizations.describe_organization()
    models=[ResourceModel._deserialize(organization["Organization"])]
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    models=[]

  return ProgressEvent(
      status = OperationStatus.SUCCESS,
      resourceModels = models,
  )
