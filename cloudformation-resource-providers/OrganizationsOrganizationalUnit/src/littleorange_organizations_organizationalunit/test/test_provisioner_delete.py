import boto3
from botocore.stub import Stubber
from cloudformation_cli_python_lib import exceptions
import logging
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationalUnitProvisioner


class TestProvisionerDelete(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  def testDelete(self):

    organizations: Organizations.Client = boto3.client("organizations")
    stub = Stubber(organizations)

    stub.add_response("delete_organizational_unit", {}, {"OrganizationalUnitId": "ou-xxxx-xxxxxxxxx"})
    stub.activate()

    model = ResourceModel._deserialize({
        "Id": "ou-xxxx-xxxxxxxxx"
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    provisioner.delete(model)

    stub.assert_no_pending_responses()
    stub.deactivate()

  def testDeleteNoExists(self):

    organizations: Organizations.Client = boto3.client("organizations")
    stub = Stubber(organizations)

    stub.add_client_error("delete_organizational_unit", "OrganizationalUnitNotFoundException",
                          "Not Found", 404, {}, {"OrganizationalUnitId": "ou-xxxx-xxxxxxxxx"})
    stub.activate()

    model = ResourceModel._deserialize({
        "Id": "ou-xxxx-xxxxxxxxx"
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)

    with self.assertRaises(exceptions.NotFound):
      provisioner.delete(model)

    stub.assert_no_pending_responses()
    stub.deactivate()

  def testDeleteCannotDelete(self):

    organizations: Organizations.Client = boto3.client("organizations")
    stub = Stubber(organizations)

    stub.add_client_error("delete_organizational_unit", "OrganizationalUnitNotEmptyException",
                          "Organizational Unit has children", 400, {}, {"OrganizationalUnitId": "ou-xxxx-xxxxxxxxx"})
    stub.activate()

    model = ResourceModel._deserialize({
        "Id": "ou-xxxx-xxxxxxxxx"
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)

    with self.assertRaises(exceptions.ResourceConflict):
      provisioner.delete(model)

    stub.assert_no_pending_responses()
    stub.deactivate()
