from botocore.stub import Stubber, ANY
import boto3
import datetime
import json
from unittest import TestCase
from unittest.mock import call, patch, Mock

from .. import app


def constructMocks():

  session = boto3.Session(aws_access_key_id="mock_access_key_id", aws_secret_access_key="mock_secret_access_key", aws_session_token="mock_session_token")
  services = {
      "organizations": session.client("organizations"),
      "securityhub": session.client("securityhub"),
      "sts": session.client("sts")
  }
  stubs = {k: Stubber(v) for k, v in services.items()}

  mock = Mock()
  mock.return_value = mock
  mock.client.side_effect = lambda service, **kwargs: services[service]

  return mock, services, stubs


class Test(TestCase):

  def testCreate(self):

    mock, services, stubs = constructMocks()

    with patch("boto3.client", new=mock.client):
      with patch("boto3.Session", new=mock):

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
            expected_params={"RoleArn": "arn:aws:iam::111122223333:role/OrganizationAccountAccessRole", "RoleSessionName": "SecurityHubOnboarding"}
        )
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
            expected_params={"RoleArn": "arn:aws:iam::000011112222:role/OrganizationAccountAccessRole", "RoleSessionName": "SecurityHubOnboarding"}
        )
        stubs["organizations"].add_response(
            "describe_account",
            {
                "Account":
                    {
                        "Id": "000011112222",
                        "Arn": "arn:aws:organizations::933397847440:account/o-wvehzxxxxx/000011112222",
                        "Email": "little.orange.aws+test@gmail.com",
                        "Name": "Test",
                        "Status": "ACTIVE",
                        "JoinedMethod": "CREATED",
                        "JoinedTimestamp": 1601288149.621
                    }
            },
            expected_params={"AccountId": "000011112222"}
        )
        stubs["securityhub"].add_response(
            "create_members",
            {},
            expected_params={"AccountDetails": [{"AccountId": "000011112222", "Email": "little.orange.aws+test@gmail.com"}]}
        )
        stubs["securityhub"].add_response(
            "invite_members",
            {},
            expected_params={"AccountIds": ["000011112222"]}
        )
        stubs["securityhub"].add_response(
            "list_invitations",
            {
                "Invitations": [
                    {
                        "AccountId": "111122223333",
                        "InvitationId": "MockInvitationId",
                        "InvitedAt": datetime.datetime(2015, 1, 1),
                        "MemberStatus": "INVITED"
                    },
                ]
            }
        )
        stubs["securityhub"].add_response(
            "accept_invitation",
            {},
            expected_params={"MasterId": "111122223333", "InvitationId": "MockInvitationId"}
        )

        for _, stub in stubs.items():
          stub.activate()

        event = {
            "RequestType": "Create",
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:SecurityHubOnboarding",
            "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A000011112222%3Astack/xxxx/cbb30f50-0160-11eb-b815-0674a4b2xxxxxxx",
            "StackId": "arn:aws:cloudformation:ap-southeast-2:000011112222:stack/xxxx/cbb30f50-0160-11eb-b815-0674a4b20bdc",
            "RequestId": "ec179708-db2f-433c-a365-750251237371",
            "LogicalResourceId": "Onboarding",
            "ResourceType": "Custom::SecurityHubOnboarding",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:SecurityHubOnboarding",
                "AccountId": "000011112222",
                "MasterAccountId": "111122223333",
                "Region": "us-east-1"
            }
        }
        context = {}

        app.create(event, context)

        assert mock.client.mock_calls == [
            call("organizations", region_name="us-east-1"),
            call("sts"),
            call("securityhub", region_name="us-east-1"),
            call("sts"),
            call("securityhub", region_name="us-east-1")
        ]

  def testDelete(self):

    mock, services, stubs = constructMocks()

    with patch("boto3.client", new=mock.client):
      with patch("boto3.Session", new=mock):

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
            expected_params={"RoleArn": "arn:aws:iam::111122223333:role/OrganizationAccountAccessRole", "RoleSessionName": "SecurityHubOnboarding"}
        )
        stubs["securityhub"].add_response(
            "disassociate_members",
            {},
            expected_params={"AccountIds": ["000011112222"]}
        )
        stubs["securityhub"].add_response(
            "delete_members",
            {},
            expected_params={"AccountIds": ["000011112222"]}
        )

        for _, stub in stubs.items():
          stub.activate()

        event = {
            "RequestType": "Delete",
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:SecurityHubOnboarding",
            "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A000011112222%3Astack/xxxx/cbb30f50-0160-11eb-b815-0674a4b2xxxxxxx",
            "StackId": "arn:aws:cloudformation:ap-southeast-2:000011112222:stack/xxxx/cbb30f50-0160-11eb-b815-0674a4b20bdc",
            "RequestId": "ec179708-db2f-433c-a365-750251237371",
            "LogicalResourceId": "Onboarding",
            "ResourceType": "Custom::SecurityHubOnboarding",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:SecurityHubOnboarding",
                "AccountId": "000011112222",
                "MasterAccountId": "111122223333",
                "Region": "us-west-1"
            }
        }
        context = {}

        app.delete(event, context)

        assert mock.client.mock_calls == [
            call("sts"),
            call("securityhub", region_name="us-west-1")
        ]

  def testAssumeRoleSameAccount(self):

    mock, services, stubs = constructMocks()

    with patch("boto3.client", new=mock.client):
      with patch("boto3.Session", new=mock):

        stubs["sts"].add_response(
            "get_caller_identity",
            {
                "UserId": "AIDAxxxxxxxxxxxxxx37Z2",
                "Account": "222233334444",
                "Arn": "arn:aws:iam::222233334444:user/mock.user"
            }
        )

        for _, stub in stubs.items():
          stub.activate()

        app.assumeRole("222233334444")
