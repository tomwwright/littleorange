import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock


from ..models import ResourceModel
from ..provisioner import OrganizationsOrganizationalUnitProvisioner


class TestProvisionerCreate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testCreateWithOrganizationRoot(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    desired = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Test'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name is not None
    assert model.ParentId is not None
    assert model.PolicyIds == OrganizationsOrganizationalUnitProvisioner.DEFAULT_POLICY_IDS

  @mock_organizations
  def testCreateWithOURoot(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    outerDesired = ResourceModel._deserialize({
        'ParentId': root["Id"],
        'Name': 'Outer'
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    outerModel = provisioner.create(outerDesired)

    innerDesired = ResourceModel._deserialize({
        'ParentId': outerModel.Id,
        'Name': 'Inner'
    })

    innerModel = provisioner.create(innerDesired)

    assert innerModel.Arn is not None
    assert innerModel.Id is not None
    assert innerModel.Name is not None
    assert innerModel.ParentId == outerModel.Id
    assert innerModel.PolicyIds == OrganizationsOrganizationalUnitProvisioner.DEFAULT_POLICY_IDS

  @mock_organizations
  def testCreateWithNoPolicyIds(self):
    organizations: Organizations.Client = boto3.client("organizations")

    organizations.detach_policy = Mock()
    organizations.detach_policy

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    desired = ResourceModel._deserialize({
        "ParentId": root["Id"],
        "Name": "Testing",
        "PolicyIds": []
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert organizations.detach_policy.called
    assert organizations.detach_policy.call_args.kwargs == {"TargetId": model.Id, "PolicyId": "p-FullAWSAccess"}

  @mock_organizations
  def testCreateWithPolicyIds(self):
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

    desired = ResourceModel._deserialize({
        "ParentId": root["Id"],
        "Name": "Testing",
        "PolicyIds": [
            "p-FullAWSAccess",
            policyId
        ]
    })

    provisioner = OrganizationsOrganizationalUnitProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.PolicyIds == desired.PolicyIds

    policies = organizations.list_policies_for_target(TargetId=model.Id, Filter="SERVICE_CONTROL_POLICY")

    assert len(policies["Policies"]) == 2  # expect the FullAWSAccess policy
    assert policyId in [policy["Id"] for policy in policies["Policies"]]
    assert "p-FullAWSAccess" in [policy["Id"] for policy in policies["Policies"]]
