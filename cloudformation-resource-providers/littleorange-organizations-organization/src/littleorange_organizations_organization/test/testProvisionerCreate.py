from boto3.session import Session
import logging
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationProvisioner


class TestOrganizationsOrganizationProvisionerCreate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  def testCreate(self):

    mockBoto3: Any = Mock()
    mockClient: Any = Mock()
    mockBoto3.client.return_value = mockClient

    mockClient.create_organization.return_value = {
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
                    'PolicyTypes': []
                }
            ]
        }
    ]

    desired = ResourceModel._deserialize({
        'FeatureSet': 'CONSOLIDATED_BILLING',
        'EnabledPolicyTypes': [
            {'Type': 'SERVICE_CONTROL_POLICY'},
            {'Type': 'TAG_POLICY'}
        ]
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, mockBoto3)
    model = provisioner.create(desired)

    assert mockClient.create_organization.call_count == 1
    assert mockClient.enable_policy_type.call_count == 2
    assert mockClient.disable_policy_type.call_count == 0
    enablePolicyTypeCallArgs = [kwargs for _, kwargs in mockClient.enable_policy_type.call_args_list]
    assert enablePolicyTypeCallArgs == [
        {'RootId': 'r-1234', 'PolicyType': 'SERVICE_CONTROL_POLICY'},
        {'RootId': 'r-1234', 'PolicyType': 'TAG_POLICY'},
    ]
    assert model.Id == 'o-abcd123456'
    assert model.Arn == 'arn:aws:organizations::111222333444:organization/o-abcd123456'
    assert model.FeatureSet == 'CONSOLIDATED_BILLING'

  def testCreateNoPolicyTypes(self):

    mockBoto3: Any = Mock()
    mockClient: Any = Mock()
    mockBoto3.client.return_value = mockClient

    mockClient.create_organization.return_value = {
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
                    'PolicyTypes': []
                }
            ]
        }
    ]

    desired = ResourceModel._deserialize({
        'FeatureSet': 'CONSOLIDATED_BILLING'
    })

    provisioner = OrganizationsOrganizationProvisioner(self.logger, mockBoto3)
    model = provisioner.create(desired)

    assert mockClient.create_organization.call_count == 1
    assert mockClient.enable_policy_type.call_count == 0
    assert mockClient.disable_policy_type.call_count == 0
    assert model.Id == 'o-abcd123456'
    assert model.Arn == 'arn:aws:organizations::111222333444:organization/o-abcd123456'
    assert model.FeatureSet == 'CONSOLIDATED_BILLING'
