import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationProvisioner


class TestOrganizationsOrganizationProvisionerCreate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testCreate(self):

    desired = ResourceModel._deserialize({
        'FeatureSet': 'CONSOLIDATED_BILLING',
        'EnabledPolicyTypes': [
            {'Type': 'SERVICE_CONTROL_POLICY'},
            {'Type': 'TAG_POLICY'}
        ]
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, boto3)
    model = provisioner.create(desired)

    assert model.Id is not None

    organizations: Organizations.Client = boto3.client('organizations')

    organization = organizations.describe_organization()

    assert organization['Organization']['FeatureSet'] == 'CONSOLIDATED_BILLING'

    root = provisioner.findRoot(organizations)

    assert root['Name'] == 'Root'
    assert len(root['PolicyTypes']) == 2
    assert {'Type': 'SERVICE_CONTROL_POLICY', 'Status': 'ENABLED'} in root['PolicyTypes']
    assert {'Type': 'TAG_POLICY', 'Status': 'ENABLED'} in root['PolicyTypes']

  @mock_organizations
  def testCreateNoPolicyTypes(self):

    desired = ResourceModel._deserialize({
        'FeatureSet': 'ALL',
        'EnabledPolicyTypes': []
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, boto3)
    model = provisioner.create(desired)

    assert model.Id is not None

    organizations: Organizations.Client = boto3.client('organizations')

    organization = organizations.describe_organization()

    assert organization['Organization']['FeatureSet'] == 'ALL'

    root = provisioner.findRoot(organizations)

    assert root['Name'] == 'Root'
    assert len(root['PolicyTypes']) == 0
