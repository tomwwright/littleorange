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
from .provisioner import OrganizationsOrganizationProvisioner

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

resource = Resource(OrganizationsOrganizationProvisioner.TYPE, ResourceModel)
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

  organizations = session.client("organizations")

  provisioner = OrganizationsOrganizationProvisioner(LOG, organizations)
  organization = provisioner.create(request.desiredResourceState)

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=organization,
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

  organizations = session.client("organizations")

  provisioner = OrganizationsOrganizationProvisioner(LOG, organizations)
  organization = provisioner.update(request.previousResourceState, request.desiredResourceState)

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=organization,
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

  organizations = session.client("organizations")

  provisioner = OrganizationsOrganizationProvisioner(LOG, organizations)
  provisioner.delete()

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

  if not request.desiredResourceState or not request.desiredResourceState.Id:
    raise exceptions.InternalFailure("Desired resource state unavailable")

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations = session.client("organizations")
  provisioner = OrganizationsOrganizationProvisioner(LOG, organizations)
  organization = provisioner.get(request.desiredResourceState)

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModel=organization,
  )


@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:

  if not session:
    raise exceptions.InternalFailure(f"boto3 session unavailable")

  organizations = session.client("organizations")

  provisioner = OrganizationsOrganizationProvisioner(LOG, organizations)
  organizationList = provisioner.listResources()

  return ProgressEvent(
      status=OperationStatus.SUCCESS,
      resourceModels=organizationList,
  )
