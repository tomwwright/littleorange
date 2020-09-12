import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationalUnitProvisioner


class TestProvisionerUpdate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testUpdateName(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    createModel = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Test'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(createModel)

    assert model.Name == 'Test'

    model.Name = "TestUpdated"
    updated = provisioner.update(createModel, model)

    ou = organizations.describe_organizational_unit(OrganizationalUnitId=updated.Id)
    assert ou["OrganizationalUnit"]["Name"] == updated.Name == "TestUpdated"
