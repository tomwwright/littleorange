import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import call, patch, Mock


from ..models import ResourceModel
from ..provisioner import OrganizationsAccountProvisioner


class TestProvisionerCreate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testCreateWithoutParent(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    desired = ResourceModel._deserialize({
        'Email': "test@littleorange.com.au",
        'Name': 'Test'
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name == desired.Name
    assert model.Email == desired.Email
    assert model.ParentId == root["Id"]

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == model.ParentId

  @mock_organizations
  def testCreateWithOrganizationRootParent(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]

    desired = ResourceModel._deserialize({
        'Email': "test@littleorange.com.au",
        'Name': 'Test',
        'ParentId': root["Id"]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name == desired.Name
    assert model.Email == desired.Email
    assert model.ParentId == root["Id"]

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == model.ParentId

  @mock_organizations
  def testCreateWithOUParent(self):

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

    assert model.Arn is not None
    assert model.Id is not None
    assert model.Name == desired.Name
    assert model.Email == desired.Email
    assert model.ParentId == ou["OrganizationalUnit"]["Id"]

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == model.ParentId

  @mock_organizations
  def testCreateWithDelegatedAdministratorServices(self):

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

    with patch.object(organizations, 'register_delegated_administrator', wraps=organizations.register_delegated_administrator) as spy:
      model = provisioner.create(desired)

      assert spy.mock_calls == [
          call(AccountId=model.Id, ServicePrincipal="guardduty.amazonaws.com"),
          call(AccountId=model.Id, ServicePrincipal="ssm.amazonaws.com")
      ]

    assert model.DelegatedAdministratorServices == desired.DelegatedAdministratorServices

    services = organizations.list_delegated_services_for_account(AccountId=model.Id)

    assert [service["ServicePrincipal"] for service in services["DelegatedServices"]] == ["guardduty.amazonaws.com", "ssm.amazonaws.com"]
