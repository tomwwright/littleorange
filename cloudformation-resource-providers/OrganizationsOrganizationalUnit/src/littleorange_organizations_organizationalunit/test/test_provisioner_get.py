import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationalUnitProvisioner


class TestProvisionerGet(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testGet(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    desired = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Test'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    desired = ResourceModel._deserialize({
        "Id": model.Id
    })
    model = provisioner.get(desired)

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name is not None
    assert model.ParentId == root['Id']
    assert model.PolicyIds == OrganizationsOrganizationalUnitProvisioner.DEFAULT_POLICY_IDS

  @mock_organizations
  def testGetWithOURoot(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    outerDesired = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Outer'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    outerModel = provisioner.create(outerDesired)

    innerDesired = ResourceModel._deserialize({
        'ParentId': outerModel.Id,
        'Name': 'Inner'
    })

    innerModel = provisioner.create(innerDesired)

    desired = ResourceModel._deserialize({
        "Id": innerModel.Id
    })
    model = provisioner.get(desired)

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name is not None
    assert model.ParentId == outerModel.Id
    assert model.PolicyIds == OrganizationsOrganizationalUnitProvisioner.DEFAULT_POLICY_IDS
