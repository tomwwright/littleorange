import logging
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationProvisioner


class TestOrganizationsOrganizationProvisionerList(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  def testList(self):

    mockBoto3: Any = Mock()
    mockClient: Any = Mock()
    mockBoto3.client.return_value = mockClient

    mockClient.describe_organization.return_value = {
        'Organization': {
            'Id': 'o-abcd123456',
            'Arn': 'arn:aws:organizations::111222333444:organization/o-abcd123456',
            'FeatureSet': 'CONSOLIDATED_BILLING',
            'MasterAccountArn': 'arn:aws:organizations::111222333444:organization/o-abcd123456/111222333444',
            'MasterAccountId': '111222333444',
            'MasterAccountEmail': 'test@testing.com',
            'AvailablePolicyTypes': [
                {
                    'Type': 'SERVICE_CONTROL_POLICY',
                    'Status': 'ENABLED'
                },
                {
                    'Type': 'BACKUP_POLICY',
                    'Status': 'ENABLED'
                }
            ]
        }
    }

    # list_roots
    mockClient.get_paginator.return_value.paginate.return_value = [
        {
            'Roots': [
                {
                    'Id': 'r-1234',
                    'Arn': 'arn:aws:organizations::111222333444:root/o-abcd123456/r-1234',
                    'Name': 'Root',
                    'PolicyTypes': [
                        {
                            'Type': 'SERVICE_CONTROL_POLICY',
                            'Status': 'ENABLED'
                        },
                        {
                            'Type': 'BACKUP_POLICY',
                            'Status': 'ENABLED'
                        }
                    ]
                }
            ]
        }
    ]

    provisioner = OrganizationsOrganizationProvisioner(self.logger, mockBoto3)
    models = provisioner.listResources()

    assert len(models) == 1
    assert models[0].Id == 'o-abcd123456'
    assert models[0].Arn == 'arn:aws:organizations::111222333444:organization/o-abcd123456'
    assert models[0].FeatureSet == 'CONSOLIDATED_BILLING'
    assert len(models[0].EnabledPolicyTypes) == 2
    assert models[0].EnabledPolicyTypes[0].Type == 'SERVICE_CONTROL_POLICY'
    assert models[0].EnabledPolicyTypes[1].Type == 'BACKUP_POLICY'
