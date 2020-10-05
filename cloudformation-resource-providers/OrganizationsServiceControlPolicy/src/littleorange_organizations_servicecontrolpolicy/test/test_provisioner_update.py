import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock

from ..models import ResourceModel
from ..provisioner import OrganizationsServiceControlPolicyProvisioner


class TestProvisionerUpdate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testUpdateName(self):

    organizations: Organizations.Client = boto3.client('organizations')
    organizations.create_organization(FeatureSet="ALL")
    policy = organizations.create_policy(
        Content="{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Action\": [\n        \"dynamodb:*\",\n        \"iam:*\",\n        \"lambda:*\",\n        \"sns:*\",\n        \"sqs:*\",\n        \"events:*\"\n      ],\n      \"Effect\": \"Allow\",\n      \"Resource\": \"*\"\n    }\n  ]\n}\n",
        Description="Access to all services",
        Name="Open",
        Type="SERVICE_CONTROL_POLICY"
    )['Policy']

    current = ResourceModel._deserialize({
        "Id": policy["PolicySummary"]["Id"],
        "Name": policy["PolicySummary"]["Name"],
        "Content": policy["Content"],
        "Description": policy["PolicySummary"]["Description"]
    })

    desired = ResourceModel._deserialize({
        "Id": current.Id,
        "Name": "OpenUpdated",
        "Content": current.Content,
        "Description": current.Description
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)
    model = provisioner.update(current, desired)

    updatedPolicy = organizations.describe_policy(PolicyId=policy["PolicySummary"]["Id"])["Policy"]

    assert updatedPolicy["PolicySummary"]["Name"] == model.Name == "OpenUpdated"

  @mock_organizations
  def testUpdateContent(self):

    organizations: Organizations.Client = boto3.client('organizations')
    organizations.create_organization(FeatureSet="ALL")
    policy = organizations.create_policy(
        Content="{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Action\": [\n        \"dynamodb:*\",\n        \"iam:*\",\n        \"lambda:*\",\n        \"sns:*\",\n        \"sqs:*\",\n        \"events:*\"\n      ],\n      \"Effect\": \"Allow\",\n      \"Resource\": \"*\"\n    }\n  ]\n}\n",
        Description="Access to all services",
        Name="Open",
        Type="SERVICE_CONTROL_POLICY"
    )['Policy']

    current = ResourceModel._deserialize({
        "Id": policy["PolicySummary"]["Id"],
        "Name": policy["PolicySummary"]["Name"],
        "Content": policy["Content"],
        "Description": policy["PolicySummary"]["Description"]
    })

    desired = ResourceModel._deserialize({
        "Id": current.Id,
        "Name": current.Name,
        "Content": "{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Action\": [\n        \"rds:*\",\n        \"iam:*\",\n        \"lambda:*\",\n        \"sns:*\",\n        \"sqs:*\",\n        \"events:*\"\n      ],\n      \"Effect\": \"Allow\",\n      \"Resource\": \"*\"\n    }\n  ]\n}\n",
        "Description": current.Description
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)
    model = provisioner.update(current, desired)

    updatedPolicy = organizations.describe_policy(PolicyId=policy["PolicySummary"]["Id"])["Policy"]

    assert "rds" in updatedPolicy["Content"]
    assert "rds" in model.Content

  @mock_organizations
  def testUpdateDescription(self):

    organizations: Organizations.Client = boto3.client('organizations')
    organizations.create_organization(FeatureSet="ALL")
    policy = organizations.create_policy(
        Content="{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [\n    {\n      \"Action\": [\n        \"dynamodb:*\",\n        \"iam:*\",\n        \"lambda:*\",\n        \"sns:*\",\n        \"sqs:*\",\n        \"events:*\"\n      ],\n      \"Effect\": \"Allow\",\n      \"Resource\": \"*\"\n    }\n  ]\n}\n",
        Description="Access to all services",
        Name="Open",
        Type="SERVICE_CONTROL_POLICY"
    )['Policy']

    current = ResourceModel._deserialize({
        "Id": policy["PolicySummary"]["Id"],
        "Name": policy["PolicySummary"]["Name"],
        "Content": policy["Content"],
        "Description": policy["PolicySummary"]["Description"]
    })

    desired = ResourceModel._deserialize({
        "Id": current.Id,
        "Name": current.Name,
        "Content": current.Content,
        "Description": "Updated description"
    })

    provisioner = OrganizationsServiceControlPolicyProvisioner(self.logger, organizations)
    model = provisioner.update(current, desired)

    updatedPolicy = organizations.describe_policy(PolicyId=policy["PolicySummary"]["Id"])["Policy"]

    assert updatedPolicy["PolicySummary"]["Description"] == model.Description == "Updated description"
