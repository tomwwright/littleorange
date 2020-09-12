import boto3
from botocore.exceptions import ClientError
import logging
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationProvisioner


class TestProvisionerDelete(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  def testDelete(self):

    mockBoto3: Any = Mock()
    mockClient: Any = Mock()
    mockBoto3.client.return_value = mockClient

    provisioner = OrganizationsOrganizationProvisioner(self.logger, mockBoto3)

    provisioner.delete()

    assert mockClient.delete_organization.called
