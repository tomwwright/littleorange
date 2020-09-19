import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import Mock


from ..models import ResourceModel
from ..provisioner import OrganizationsAccountProvisioner


class TestProvisionerCreate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testDeleteWithoutParent(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")

    desired = ResourceModel._deserialize({
        'Email': "test@littleorange.com.au",
        'Name': 'Test'
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    provisioner.delete(model)

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == model.ParentId

  @mock_organizations
  def testDeleteWithOUParent(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    ou = organizations.create_organizational_unit(ParentId=root["Id"], Name="Test")

    desired = ResourceModel._deserialize({
        'Email': "test@littleorange.com.au",
        'Name': 'Test',
        'ParentId': ou["OrganizationalUnit"]["Id"]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    provisioner.delete(model)

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == root["Id"]

  @mock_organizations
  def testDeleteWithDelegatedAdministratorServices(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    desired = ResourceModel._deserialize({
        "Email": "test@littleorange.com.au",
        "Name": "Test",
        "DelegatedAdministratorServices": [
            "guardduty.amazonaws.com",
            "ssm.amazonaws.com"
        ]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    provisioner.delete(model)

    with self.assertRaises(organizations.exceptions.AccountNotRegisteredException):
      organizations.list_delegated_services_for_account(AccountId=model.Id)
