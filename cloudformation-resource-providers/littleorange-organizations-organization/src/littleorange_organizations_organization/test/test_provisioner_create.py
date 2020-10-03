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

    organizations: Organizations.Client = boto3.client('organizations')

    desired = ResourceModel._deserialize({
        'FeatureSet': 'CONSOLIDATED_BILLING',
        'EnabledPolicyTypes': [
            {'Type': 'SERVICE_CONTROL_POLICY'},
            {'Type': 'TAG_POLICY'}
        ]
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.Id is not None
    assert len(model.EnabledPolicyTypes) == 2
    modelEnabledPolicyTypes = [policy.Type for policy in model.EnabledPolicyTypes]
    assert "SERVICE_CONTROL_POLICY" in modelEnabledPolicyTypes
    assert "TAG_POLICY" in modelEnabledPolicyTypes

    organization = organizations.describe_organization()

    assert organization['Organization']['FeatureSet'] == 'CONSOLIDATED_BILLING'

    root = provisioner.findRoot()

    assert root['Name'] == 'Root'
    assert len(root['PolicyTypes']) == 2
    assert {'Type': 'SERVICE_CONTROL_POLICY', 'Status': 'ENABLED'} in root['PolicyTypes']
    assert {'Type': 'TAG_POLICY', 'Status': 'ENABLED'} in root['PolicyTypes']

    services = organizations.list_aws_service_access_for_organization()

    assert [service["ServicePrincipal"] for service in services["EnabledServicePrincipals"]] == []

  @mock_organizations
  def testCreateNoPolicyTypesNoServices(self):

    organizations: Organizations.Client = boto3.client('organizations')

    desired = ResourceModel._deserialize({
        'FeatureSet': 'ALL',
        'EnabledPolicyTypes': [],
        'EnabledServices': []
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.Id is not None


    organization = organizations.describe_organization()

    assert organization['Organization']['FeatureSet'] == 'ALL'

    root = provisioner.findRoot()

    assert root['Name'] == 'Root'
    assert len(root['PolicyTypes']) == 0

    services = organizations.list_aws_service_access_for_organization()

    assert [service["ServicePrincipal"] for service in services["EnabledServicePrincipals"]] == []

  @mock_organizations
  def testCreateWithServices(self):

    organizations: Organizations.Client = boto3.client('organizations')

    desired = ResourceModel._deserialize({
        'FeatureSet': 'ALL',
        'EnabledServices': [
            {'ServicePrincipal': 'cloudtrail.amazonaws.com'},
            {'ServicePrincipal': 'guardduty.amazonaws.com'}
        ]
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.Id is not None

    organization = organizations.describe_organization()

    assert organization['Organization']['FeatureSet'] == 'ALL'

    root = provisioner.findRoot()

    assert root['Name'] == 'Root'
    assert len(root['PolicyTypes']) == 0

    services = organizations.list_aws_service_access_for_organization()

    assert set([service["ServicePrincipal"] for service in services["EnabledServicePrincipals"]]
               ) == set(["cloudtrail.amazonaws.com", "guardduty.amazonaws.com"])
