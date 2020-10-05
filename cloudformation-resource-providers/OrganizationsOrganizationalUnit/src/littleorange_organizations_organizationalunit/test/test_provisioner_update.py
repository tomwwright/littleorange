import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
import os
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import patch

from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationalUnitProvisioner


class TestProvisionerUpdate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

    os.environ["AWS_ACCESS_KEY_ID"] = "xxxx"

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

  @mock_organizations
  def testUpdateAddPolicy(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    policy = organizations.create_policy(
        Content="{\"Version\": \"2012-10-17\", \"Statement\": {\"Effect\": \"Deny\", \"Action\": [ \"iam:*\", \"ec2:*\", \"rds:*\" ], \"Resource\": \"*\"}}",
        Description="Testing",
        Name="Testing",
        Type="SERVICE_CONTROL_POLICY"
    )

    policyId = policy["Policy"]["PolicySummary"]["Id"]

    createModel = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Test'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(createModel)

    assert model.Name == 'Test'
    assert model.PolicyIds == OrganizationsOrganizationalUnitProvisioner.DEFAULT_POLICY_IDS

    model.PolicyIds = ["p-FullAWSAccess", policyId]

    with patch.object(organizations, 'attach_policy', wraps=organizations.attach_policy) as spy:
      updated = provisioner.update(createModel, model)

      spy.assert_called_with(TargetId=model.Id, PolicyId=policyId)

    policies = organizations.list_policies_for_target(TargetId=updated.Id, Filter="SERVICE_CONTROL_POLICY")
    assert model.PolicyIds == [policy["Id"] for policy in policies["Policies"]]

  @mock_organizations
  def testUpdateChangePolicies(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    policy = organizations.create_policy(
        Content="{\"Version\": \"2012-10-17\", \"Statement\": {\"Effect\": \"Deny\", \"Action\": [ \"iam:*\", \"ec2:*\", \"rds:*\" ], \"Resource\": \"*\"}}",
        Description="Testing",
        Name="Testing",
        Type="SERVICE_CONTROL_POLICY"
    )

    policyId = policy["Policy"]["PolicySummary"]["Id"]

    createModel = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Test'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(createModel)

    assert model.Name == 'Test'
    assert model.PolicyIds == OrganizationsOrganizationalUnitProvisioner.DEFAULT_POLICY_IDS

    model.PolicyIds = [policyId]

    with patch.object(organizations, 'attach_policy', wraps=organizations.attach_policy) as attachSpy:
      with patch.object(organizations, 'detach_policy') as detachMock:
        updated = provisioner.update(createModel, model)

        attachSpy.assert_called_with(TargetId=model.Id, PolicyId=policyId)
        detachMock.assert_called_with(TargetId=model.Id, PolicyId="p-FullAWSAccess")

    policies = organizations.list_policies_for_target(TargetId=updated.Id, Filter="SERVICE_CONTROL_POLICY")
    assert policyId in [policy["Id"] for policy in policies["Policies"]]  # cannot test for other policy being attached because relying on mock detach_policy
