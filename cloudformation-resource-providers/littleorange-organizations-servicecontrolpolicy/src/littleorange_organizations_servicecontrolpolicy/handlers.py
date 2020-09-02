import logging
from typing import Any, MutableMapping, Optional

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

from .models import ResourceHandlerRequest, ResourceModel

LOG = logging.getLogger(__name__)
TYPE_NAME = "LittleOrange::Organizations::ServiceControlPolicy"

SERVICE_CONTROL_POLICY = "SERVICE_CONTROL_POLICY"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  LOG.info(request)

  print(request)

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  model = request.desiredResourceState

  organizations: Organizations.Client = session.client('organizations')
  scp = organizations.create_policy(
      Name=model.Name,
      Description=model.Description or "",
      Content=model.Content,
      Type=SERVICE_CONTROL_POLICY
  )["Policy"]

  model = ResourceModel._deserialize({
      "Arn": scp["PolicySummary"]["Arn"],
      "Description": scp["PolicySummary"]["Description"],
      "Content": scp["Content"],
      "Id": scp["PolicySummary"]["Id"],
      "Name": scp["PolicySummary"]["Name"]
  })

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=model,
  )


@resource.handler(Action.UPDATE)
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  LOG.info(request)

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  model = request.desiredResourceState

  try:
    organizations: Organizations.Client = session.client('organizations')
    scp = organizations.update_policy(
        PolicyId=model.Id,
        Description=model.Description,
        Content=model.Content,
        Name=model.Name
    )["Policy"]
  except organizations.exceptions.PolicyNotFoundException:
    raise exceptions.NotFound(TYPE_NAME, model.Id)

  model = ResourceModel._deserialize({
      "Arn": scp["PolicySummary"]["Arn"],
      "Description": scp["PolicySummary"]["Description"],
      "Content": scp["Content"],
      "Id": scp["PolicySummary"]["Id"],
      "Name": scp["PolicySummary"]["Name"]
  })

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

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  model = request.desiredResourceState

  try:
    organizations: Organizations.Client = session.client('organizations')
    organizations.delete_policy(PolicyId=model.Id)
  except organizations.exceptions.PolicyNotFoundException:
    raise exceptions.NotFound(TYPE_NAME, model.Id)

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

  LOG.info(request)

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  model = request.desiredResourceState

  organizations: Organizations.Client = session.client('organizations')

  try:
    scp = organizations.describe_policy(PolicyId=model.Id)["Policy"]
  except organizations.exceptions.PolicyNotFoundException:
    raise exceptions.NotFound(TYPE_NAME, model.Id)

  model = ResourceModel._deserialize({
      "Arn": scp["PolicySummary"]["Arn"],
      "Description": scp["PolicySummary"]["Description"],
      "Content": scp["Content"],
      "Id": scp["PolicySummary"]["Id"],
      "Name": scp["PolicySummary"]["Name"]
  })

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=model,
  )
