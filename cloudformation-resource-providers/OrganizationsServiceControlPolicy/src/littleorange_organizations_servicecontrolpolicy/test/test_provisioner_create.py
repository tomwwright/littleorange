from boto3.session import Session
import logging
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock

from ..models import ResourceModel
from ..provisioner import OrganizationsServiceControlPolicyProvisioner


class TestProvisionerCreate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  def testCreate(self):

    mockClient: Any = Mock()
    mockClient.create_policy.return_value = {
        "Policy": {
            "PolicySummary": {
                "Id": "p-abcd1234",
                "Arn": "arn:aws:organizations::933397847440:policy/o-abcd123456/service_control_policy/p-abcd1234",
                "Name": "Open",
                "Description": "Access to all services",
                "Type": "SERVICE_CONTROL_POLICY",
                "AwsManaged": False
            },
            "Content": "{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Action\": [\n        \"dynamodb:*\",\n        \"iam:*\",\n        \"lambda:*\",\n        \"sns:*\",\n        \"sqs:*\",\n        \"events:*\"\n      ],\n      \"Effect\": \"Allow\",\n      \"Resource\": \"*\"\n    }\n  ]\n}\n"
        }
    }

    desired = ResourceModel._deserialize({
        "Name": "Open",
        "Content": "{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Action\": [\n        \"dynamodb:*\",\n        \"iam:*\",\n        \"lambda:*\",\n        \"sns:*\",\n        \"sqs:*\",\n        \"events:*\"\n      ],\n      \"Effect\": \"Allow\",\n      \"Resource\": \"*\"\n    }\n  ]\n}\n",
        "Description": "Access to all services"
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, mockClient)
    model = provisioner.create(desired)

    assert mockClient.create_policy.call_count == 1
    assert model.Id == "p-abcd1234"
    assert model.Name == "Open"
    assert model.Description == "Access to all services"
