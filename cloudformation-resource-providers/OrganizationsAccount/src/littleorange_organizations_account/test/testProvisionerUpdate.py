import boto3
import logging
from moto import mock_organizations
import mypy_boto3_organizations as Organizations
from typing import Any, get_type_hints
from unittest import TestCase
from unittest.mock import patch, Mock


from ..models import ResourceModel
from ..provisioner import OrganizationsAccountProvisioner


class TestProvisionerUpdate(TestCase):

  def setUp(self):
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)

  @mock_organizations
  def testUpdateParentId(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    ou1 = organizations.create_organizational_unit(ParentId=root["Id"], Name="Test1")
    ou2 = organizations.create_organizational_unit(ParentId=root["Id"], Name="Test2")

    desired = ResourceModel._deserialize({
        'Email': "test@littleorange.com.au",
        'Name': 'Test',
        'ParentId': ou1["OrganizationalUnit"]["Id"]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    created = provisioner.create(desired)

    assert created.ParentId == ou1["OrganizationalUnit"]["Id"]

    desiredUpdate = ResourceModel._deserialize({
        **created._serialize(),
        "ParentId": ou2["OrganizationalUnit"]["Id"]
    })

    updated = provisioner.update(created, desiredUpdate)

    parents = organizations.list_parents(ChildId=updated.Id)

    assert parents["Parents"][0]["Id"] == desiredUpdate.ParentId

  @mock_organizations
  def testUpdateRemoveParentId(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    root = organizations.list_roots()["Roots"][0]
    ou1 = organizations.create_organizational_unit(ParentId=root["Id"], Name="Test1")

    desired = ResourceModel._deserialize({
        'Email': "test@littleorange.com.au",
        'Name': 'Test',
        'ParentId': ou1["OrganizationalUnit"]["Id"]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    created = provisioner.create(desired)

    assert created.ParentId == ou1["OrganizationalUnit"]["Id"]

    desiredUpdate = ResourceModel._deserialize({
        **created._serialize()
    })
    desiredUpdate.ParentId = None

    updated = provisioner.update(created, desiredUpdate)

    parents = organizations.list_parents(ChildId=updated.Id)

    assert parents["Parents"][0]["Id"] == root["Id"]

  @mock_organizations
  def testUpdateDelegatedAdministratorServices(self):

    organizations: Organizations.Client = boto3.client("organizations")

    organizations.create_organization(FeatureSet="ALL")
    
    desired = ResourceModel._deserialize({
        "Email": "test@littleorange.com.au",
        "Name": "Test",
        "DelegatedAdministratorServices": [
            "guardduty.amazonaws.com"
        ]
    })

    provisioner = OrganizationsAccountProvisioner(self.logger, organizations)
    created = provisioner.create(desired)

    desiredUpdate = ResourceModel._deserialize({
        **created._serialize(),
        "DelegatedAdministratorServices": [
            "ssm.amazonaws.com"
        ]
    })

    with patch.object(organizations, 'deregister_delegated_administrator', wraps=organizations.deregister_delegated_administrator) as deregisterSpy:
      with patch.object(organizations, 'register_delegated_administrator', wraps=organizations.register_delegated_administrator) as registerSpy:
        updated = provisioner.update(created, desiredUpdate)

        deregisterSpy.assert_called_with(AccountId=created.Id, ServicePrincipal="guardduty.amazonaws.com")
        registerSpy.assert_called_with(AccountId=created.Id, ServicePrincipal="ssm.amazonaws.com")

        assert updated.DelegatedAdministratorServices == ["ssm.amazonaws.com"]
