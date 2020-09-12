import logging
from typing import Any, MutableMapping, Optional
import mypy_boto3_organizations as Organizations
from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

from .models import ResourceHandlerRequest, ResourceModel
from .provisioner import OrganizationsOrganizationalUnitProvisioner

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

resource = Resource(OrganizationsOrganizationalUnitProvisioner.TYPE, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  LOG.info(request)

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  organizations: Organizations.Client = session.client('organizations')

  provisioner = OrganizationsOrganizationalUnitProvisioner(LOG, organizations)
  model = provisioner.create(request.desiredResourceState)

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

  if not request.previousResourceState:
    raise exceptions.InternalFailure("Previous resource state unavailable")

  if not request.desiredResourceState:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  organizations: Organizations.Client = session.client('organizations')

  provisioner = OrganizationsOrganizationalUnitProvisioner(LOG, organizations)
  model = provisioner.update(request.previousResourceState, request.desiredResourceState)

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

  if not request.desiredResourceState or not request.desiredResourceState.Id:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations: Organizations.Client = session.client('organizations')

  provisioner = OrganizationsOrganizationalUnitProvisioner(LOG, organizations)
  ou = provisioner.get(request.desiredResourceState)

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=ou,
  )
