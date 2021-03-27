from botocore.stub import Stubber, ANY
import boto3
import datetime
import json
from unittest import TestCase
from unittest.mock import call, patch, Mock

from .. import app


def constructMocks(serviceNames):

  session = boto3.Session(aws_access_key_id="mock_access_key_id", aws_secret_access_key="mock_secret_access_key", aws_session_token="mock_session_token")
  services = {service: session.client(service) for service in serviceNames}
  stubs = {k: Stubber(v) for k, v in services.items()}

  mock = Mock()
  mock.return_value = mock
  mock.client.side_effect = lambda service, **kwargs: services[service]

  return mock, services, stubs


class Test(TestCase):

  @patch("time.sleep")
  def testCreate(self, sleep_mock):

    mock, services, stubs = constructMocks(["servicecatalog", "sts"])

    with patch("boto3.client", new=mock.client):
      with patch("boto3.Session", new=mock):

        event = {
            "RequestType": "Create",
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
            "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
            "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
            "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
            "LogicalResourceId": "PortfolioShare",
            "ResourceType": "Custom::ServiceCatalogOrganizationPortfolioShare",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
                "AccountId": "111122223333",
                "Region": "ap-southeast-1",
                "PortfolioShareConfiguration": {
                    "PortfolioId": "port-12345678",
                    "OrganizationNodeId": "o-12345678"
                }
            }
        }
        context = {}

        stubs["sts"].add_response(
            "get_caller_identity",
            {
                "UserId": "AIDAxxxxxxxxxxxxxx37Z2",
                "Account": "222233334444",
                "Arn": "arn:aws:iam::222233334444:user/mock.user"
            }
        )
        stubs["sts"].add_response(
            "assume_role",
            {"Credentials": {"AccessKeyId": "AccessKeyIdXXXXX", "SecretAccessKey": "SecretAccessKey",
                             "SessionToken": "SessionToken", "Expiration": datetime.datetime.now()}},
            expected_params={"RoleArn": "arn:aws:iam::111122223333:role/OrganizationAccountAccessRole",
                             "RoleSessionName": "ServiceCatalogOrganizationPortfolioShare"}
        )

        stubs["servicecatalog"].add_response(
            "create_portfolio_share",
            {
                "PortfolioShareToken": "share-12345678"
            },
            expected_params={
                "OrganizationNode": {
                    "Type": "ORGANIZATION",
                    "Value": event["ResourceProperties"]["PortfolioShareConfiguration"]["OrganizationNodeId"]
                },
                "PortfolioId": event["ResourceProperties"]["PortfolioShareConfiguration"]["PortfolioId"]
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "NOT_STARTED"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "IN_PROGRESS"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "COMPLETED"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        for _, stub in stubs.items():
          stub.activate()

        app.create(event, context)

        assert sleep_mock.call_count == 2
        assert mock.client.mock_calls == [
            call("sts"),
            call("servicecatalog")
        ]

  @patch("time.sleep")
  def testFailedCreate(self, sleep_mock):

    mock, services, stubs = constructMocks(["servicecatalog", "sts"])

    with patch("boto3.client", new=mock.client):
      with patch("boto3.Session", new=mock):

        event = {
            "RequestType": "Create",
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
            "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
            "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
            "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
            "LogicalResourceId": "PortfolioShare",
            "ResourceType": "Custom::ServiceCatalogOrganizationPortfolioShare",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
                "AccountId": "111122223333",
                "Region": "ap-southeast-1",
                "PortfolioShareConfiguration": {
                    "PortfolioId": "port-12345678",
                    "OrganizationNodeId": "o-12345678"
                }
            }
        }
        context = {}

        stubs["sts"].add_response(
            "get_caller_identity",
            {
                "UserId": "AIDAxxxxxxxxxxxxxx37Z2",
                "Account": "222233334444",
                "Arn": "arn:aws:iam::222233334444:user/mock.user"
            }
        )
        stubs["sts"].add_response(
            "assume_role",
            {"Credentials": {"AccessKeyId": "AccessKeyIdXXXXX", "SecretAccessKey": "SecretAccessKey",
                             "SessionToken": "SessionToken", "Expiration": datetime.datetime.now()}},
            expected_params={"RoleArn": "arn:aws:iam::111122223333:role/OrganizationAccountAccessRole",
                             "RoleSessionName": "ServiceCatalogOrganizationPortfolioShare"}
        )

        stubs["servicecatalog"].add_response(
            "create_portfolio_share",
            {
                "PortfolioShareToken": "share-12345678"
            },
            expected_params={
                "OrganizationNode": {
                    "Type": "ORGANIZATION",
                    "Value": event["ResourceProperties"]["PortfolioShareConfiguration"]["OrganizationNodeId"]
                },
                "PortfolioId": event["ResourceProperties"]["PortfolioShareConfiguration"]["PortfolioId"]
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "NOT_STARTED"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "IN_PROGRESS"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "COMPLETED_WITH_ERRORS",
                "ShareDetails": {
                    "SuccessfulShares": [],
                    "ShareErrors": [
                        {
                            "Accounts": ["000011112222"],
                            "Message": "Error happen",
                            "Error": "Yes"
                        },
                    ]
                }
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        for _, stub in stubs.items():
          stub.activate()

        with self.assertRaises(app.PortfolioShareError):
          app.create(event, context)

        assert sleep_mock.call_count == 2
        assert mock.client.mock_calls == [
            call("sts"),
            call("servicecatalog")
        ]

  @patch("time.sleep")
  def testDelete(self, sleep_mock):

    mock, services, stubs = constructMocks(["servicecatalog", "sts"])

    with patch("boto3.client", new=mock.client):
      with patch("boto3.Session", new=mock):

        event = {
            "RequestType": "Delete",
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
            "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
            "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
            "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
            "LogicalResourceId": "PortfolioShare",
            "ResourceType": "Custom::ServiceCatalogOrganizationPortfolioShare",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
                "AccountId": "111122223333",
                "Region": "ap-southeast-1",
                "PortfolioShareConfiguration": {
                    "PortfolioId": "port-12345678",
                    "OrganizationNodeId": "o-12345678"
                }
            }
        }
        context = {}

        stubs["sts"].add_response(
            "get_caller_identity",
            {
                "UserId": "AIDAxxxxxxxxxxxxxx37Z2",
                "Account": "222233334444",
                "Arn": "arn:aws:iam::222233334444:user/mock.user"
            }
        )
        stubs["sts"].add_response(
            "assume_role",
            {"Credentials": {"AccessKeyId": "AccessKeyIdXXXXX", "SecretAccessKey": "SecretAccessKey",
                             "SessionToken": "SessionToken", "Expiration": datetime.datetime.now()}},
            expected_params={"RoleArn": "arn:aws:iam::111122223333:role/OrganizationAccountAccessRole",
                             "RoleSessionName": "ServiceCatalogOrganizationPortfolioShare"}
        )

        stubs["servicecatalog"].add_response(
            "delete_portfolio_share",
            {
                "PortfolioShareToken": "share-12345678"
            },
            expected_params={
                "OrganizationNode": {
                    "Type": "ORGANIZATION",
                    "Value": event["ResourceProperties"]["PortfolioShareConfiguration"]["OrganizationNodeId"]
                },
                "PortfolioId": event["ResourceProperties"]["PortfolioShareConfiguration"]["PortfolioId"]
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "IN_PROGRESS"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        stubs["servicecatalog"].add_response(
            "describe_portfolio_share_status",
            {
                "Status": "COMPLETED"
            },
            expected_params={
                "PortfolioShareToken": "share-12345678"
            }
        )

        for _, stub in stubs.items():
          stub.activate()

        app.delete(event, context)

        assert sleep_mock.call_count == 1
        assert mock.client.mock_calls == [
            call("sts"),
            call("servicecatalog")
        ]

  @patch.object(app, "create")
  @patch.object(app, "delete")
  def testUpdate(self, delete_mock, create_mock):

    event = {
        "RequestType": "Update",
        "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
        "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
        "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
        "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
        "LogicalResourceId": "PortfolioShare",
        "ResourceType": "Custom::ServiceCatalogOrganizationPortfolioShare",
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-ServiceCatalogOrganizationPortfolioShare",
            "AccountId": "111122223333",
            "Region": "ap-southeast-1",
            "PortfolioShareConfiguration": {
                "PortfolioId": "port-12345678",
                "OrganizationNodeId": "o-12345678"
            }
        }
    }
    context = {}

    app.update(event, context)

    assert create_mock.mock_calls == [call(event, context)]
    assert delete_mock.mock_calls == [call(event, context)]
