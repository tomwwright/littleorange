import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationProvisioner


class TestOrganizationsOrganizationProvisionerUpdate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testUpdateEnabledPolicyTypes(self):

    current = ResourceModel._deserialize({
        'Id': 'o-abcd123456',
        'Arn': 'arn:aws:organizations::111222333444:organization/o-abcd123456',
        'MasterAccountArn': 'arn:aws:organizations::111222333444:organization/o-abcd123456/111222333444',
        'MasterAccountId': '111222333444',
        'MasterAccountEmail': 'test@testing.com',
        'FeatureSet': 'CONSOLIDATED_BILLING',
        'EnabledPolicyTypes': [
            {'Type': 'SERVICE_CONTROL_POLICY'},
            {'Type': 'BACKUP_POLICY'}
        ],
        'EnabledServices': [
            {'ServicePrincipal': 'guardduty.amazonaws.com'}
        ]
    })

    desired = ResourceModel._deserialize({
        'FeatureSet': 'CONSOLIDATED_BILLING',
        'EnabledPolicyTypes': [
            {'Type': 'SERVICE_CONTROL_POLICY'},
            {'Type': 'TAG_POLICY'}
        ],
        'EnabledServices': [
            {'ServicePrincipal': 'cloudtrail.amazonaws.com'},
            {'ServicePrincipal': 'config.amazonaws.com'}
        ]
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, boto3)
    provisioner.create(current)

    provisioner.update(current, desired)

    organizations: Organizations.Client = boto3.client('organizations')
    root = provisioner.findRoot(organizations)
    assert root['Name'] == 'Root'
    assert len(root['PolicyTypes']) == 2
    assert {'Type': 'SERVICE_CONTROL_POLICY', 'Status': 'ENABLED'} in root['PolicyTypes']
    assert {'Type': 'TAG_POLICY', 'Status': 'ENABLED'} in root['PolicyTypes']
    assert {'Type': 'BACKUP_POLICY', 'Status': 'ENABLED'} not in root['PolicyTypes']

    services = organizations.list_aws_service_access_for_organization()
    assert set([service["ServicePrincipal"] for service in services["EnabledServicePrincipals"]]
               ) == set(["cloudtrail.amazonaws.com", "config.amazonaws.com"])
