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
  def testGetById(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    ou = organizations.create_organizational_unit(ParentId=root["Id"], Name="Test")

    desired = ResourceModel._deserialize({
        "Email": "test@littleorange.com.au",
        "Name": 'Test',
        "ParentId": ou["OrganizationalUnit"]["Id"]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    query = ResourceModel._deserialize({
        'Id': model.Id
    })

    model = provisioner.get(query)

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == model.ParentId
    assert model.DelegatedAdministratorServices == []

  @mock_organizations
  def testGetWithDelegatedAdministratorServices(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    ou = organizations.create_organizational_unit(ParentId=root["Id"], Name="Test")

    desired = ResourceModel._deserialize({
        "Email": "test@littleorange.com.au",
        "Name": 'Test',
        "ParentId": ou["OrganizationalUnit"]["Id"],
        "DelegatedAdministratorServices": [
            "guardduty.amazonaws.com",
            "ssm.amazonaws.com"
        ]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    model = provisioner.create(desired)

    query = ResourceModel._deserialize({
        'Id': model.Id
    })

    model = provisioner.get(query)

    account = organizations.describe_account(AccountId=model.Id)
    parents = organizations.list_parents(ChildId=model.Id)
    services = [service["ServicePrincipal"] for service in organizations.list_delegated_services_for_account(AccountId=model.Id)["DelegatedServices"]]

    assert account["Account"]["Arn"] == model.Arn
    assert account["Account"]["Email"] == model.Email
    assert account["Account"]["Id"] == model.Id
    assert account["Account"]["Name"] == model.Name
    assert parents["Parents"][0]["Id"] == model.ParentId
    assert len(services) == 2
    assert "guardduty.amazonaws.com" in services
    assert "ssm.amazonaws.com" in services
