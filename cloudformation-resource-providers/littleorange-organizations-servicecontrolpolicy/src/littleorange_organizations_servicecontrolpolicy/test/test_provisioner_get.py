import boto3
from cloudformation_cli_python_lib import exceptions
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase

from ..models import ResourceModel
from ..provisioner import OrganizationsServiceControlPolicyProvisioner


class TestProvisionerGet(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testGet(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")

    create = ResourceModel._deserialize({
        "Name": "TestPolicy",
        "Description": "Test Description",
        "Content": "{\"Version\": \"2012-10-17\", \"Statement\": {\"Effect\": \"Deny\", \"Action\": [ \"iam:*\", \"ec2:*\", \"rds:*\" ], \"Resource\": \"*\"}}"
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)
    model = provisioner.create(create)

    desired = ResourceModel._deserialize({
        "Id": model.Id
    })

    model = provisioner.get(desired)

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name == create.Name
    assert model.Description == create.Description
    assert model.Content == create.Content

  @mock_organizations
  def testGetNoExists(self):

    organizations: Organizations.Client = boto3.client("organizations")

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)

    desired = ResourceModel._deserialize({
        "Id": "p-xxxxxxxx"
    })

    # mock for DescribePolicy doesn't return an error in the right format to be captured by the code so just check for the correct error code here
    with self.assertRaises(Exception) as e:
      provisioner.get(desired)
      assert "PolicyNotFoundException" in e.msg
