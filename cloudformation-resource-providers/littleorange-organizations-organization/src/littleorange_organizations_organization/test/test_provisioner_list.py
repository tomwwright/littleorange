import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock, patch

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationProvisioner


class TestOrganizationsOrganizationProvisionerList(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testList(self):

    organizations: Organizations.Client = boto3.client("organizations")

    mockBoto3: Any = Mock()
    mockBoto3.client.return_value = organizations

    with patch.object(organizations, 'describe_organization') as describeOrganizationMock:
      with patch.object(organizations, 'list_roots') as listRootsMock:
        with patch.object(organizations, 'list_aws_service_access_for_organization') as listServicesMock:

          describeOrganizationMock.return_value = {
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

          listRootsMock.side_effect = [
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

          listServicesMock.side_effect = [
              {
                  "EnabledServicePrincipals": [
                      {
                          "ServicePrincipal": "cloudtrail.amazonaws.com",
                          "DateEnabled": 1601103993.982
                      }
                  ],
                  "NextToken": "xxxx"
              },
              {
                  "EnabledServicePrincipals": [
                      {
                          "ServicePrincipal": "config.amazonaws.com",
                          "DateEnabled": 1601103993.982
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
          assert models[0].EnabledServices[0].ServicePrincipal == "cloudtrail.amazonaws.com"
          assert models[0].EnabledServices[1].ServicePrincipal == "config.amazonaws.com"
          
