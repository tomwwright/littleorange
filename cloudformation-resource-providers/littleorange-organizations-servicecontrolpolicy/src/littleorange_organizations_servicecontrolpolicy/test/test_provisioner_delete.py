import boto3
from botocore.stub import Stubber
from cloudformation_cli_python_lib import exceptions
import logging
import mypy_boto3_organizations as Organizations
from unittest import TestCase

from ..models import ResourceModel
from ..provisioner import OrganizationsServiceControlPolicyProvisioner


class TestProvisionerDelete(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  def testDelete(self):

    organizations: Organizations.Client = boto3.client("organizations")
    stub = Stubber(organizations)

    stub.add_response("delete_policy", {}, {"PolicyId": "p-xxxxxxxx"})
    stub.activate()

    model = ResourceModel._deserialize({
        "Id": "p-xxxxxxxx"
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)
    provisioner.delete(model)

    stub.assert_no_pending_responses()
    stub.deactivate()

  def testDeleteNoExists(self):

    organizations: Organizations.Client = boto3.client("organizations")
    stub = Stubber(organizations)

    stub.add_client_error("delete_policy", "PolicyNotFoundException",
                          "Not Found", 404, {}, {"PolicyId": "p-xxxxxxxx"})
    stub.activate()

    model = ResourceModel._deserialize({
        "Id": "p-xxxxxxxx"
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)

    with self.assertRaises(exceptions.NotFound):
      provisioner.delete(model)

    stub.assert_no_pending_responses()
    stub.deactivate()

  def testDeleteCannotDelete(self):

    organizations: Organizations.Client = boto3.client("organizations")
    stub = Stubber(organizations)

    stub.add_client_error("delete_policy", "PolicyInUseException",
                          "Policy is in use and cannot be deleted", 400, {}, {"PolicyId": "p-xxxxxxxx"})
    stub.activate()

    model = ResourceModel._deserialize({
        "Id": "p-xxxxxxxx"
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)

    with self.assertRaises(exceptions.ResourceConflict):
      provisioner.delete(model)

    stub.assert_no_pending_responses()
    stub.deactivate()
