import boto3
import cfnresponse
import json
from unittest import TestCase
from unittest.mock import patch, Mock

from ..app import handler


class Test(TestCase):

  @patch("boto3.client")
  @patch("cfnresponse.send")
  def testSuccess(self, mockSend, mockClient):

    mockClient.return_value.invoke.return_value = {
        "StatusCode": 202
    }

    event = {
        "RequestType": "Create",
        "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:CustomResourceProxyLambda",
        "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A000011112222%3Astack/LittleOrangeGuardDuty/cbb30f50-0160-11eb-b815-0674a4b2xxxxxxx",
        "StackId": "arn:aws:cloudformation:ap-southeast-2:000011112222:stack/LittleOrangeGuardDuty/cbb30f50-0160-11eb-b815-0674a4b20bdc",
        "RequestId": "ec179708-db2f-433c-a365-750251237371",
        "LogicalResourceId": "GuardDutyOrganizationConfiguration",
        "ResourceType": "Custom::GuardDutyOrganizationConfiguration",
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:CustomResourceProxyLambda",
            "CustomResourceProperties": {
                "ServiceToken": "arn:aws:lambda:us-east-1:000011112222:function:LittleOrangeGuardDutyOrga-CloudFormationCustomReso-1QY3RLUI3JWRB",
                "Region": "ap-southeast-2",
                "OrganizationConfiguration": {
                    "AutoEnable": "true",
                    "DataSources": {
                        "S3Logs": {
                            "AutoEnable": "true"
                        }
                    },
                    "DetectorId": "98ba69dda262a09cebd6464f88aa2fda"
                }
            }
        }
    }
    context = {}

    payload = {
        "RequestType": "Create",
        "ServiceToken": "arn:aws:lambda:us-east-1:000011112222:function:LittleOrangeGuardDutyOrga-CloudFormationCustomReso-1QY3RLUI3JWRB",
        "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A000011112222%3Astack/LittleOrangeGuardDuty/cbb30f50-0160-11eb-b815-0674a4b2xxxxxxx",
        "StackId": "arn:aws:cloudformation:ap-southeast-2:000011112222:stack/LittleOrangeGuardDuty/cbb30f50-0160-11eb-b815-0674a4b20bdc",
        "RequestId": "ec179708-db2f-433c-a365-750251237371",
        "LogicalResourceId": "GuardDutyOrganizationConfiguration",
        "ResourceType": "Custom::GuardDutyOrganizationConfiguration",
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:us-east-1:000011112222:function:LittleOrangeGuardDutyOrga-CloudFormationCustomReso-1QY3RLUI3JWRB",
            "Region": "ap-southeast-2",
            "OrganizationConfiguration": {
                "AutoEnable": "true",
                "DataSources": {
                        "S3Logs": {
                            "AutoEnable": "true"
                        }
                },
                "DetectorId": "98ba69dda262a09cebd6464f88aa2fda"
            }
        }
    }

    handler(event, context)

    mockClient.assert_called_with("lambda", region_name="us-east-1")
    assert not mockSend.called

    mockClient.return_value.invoke.assert_called_with(
        FunctionName="arn:aws:lambda:us-east-1:000011112222:function:LittleOrangeGuardDutyOrga-CloudFormationCustomReso-1QY3RLUI3JWRB",
        InvocationType="Event",
        Payload=json.dumps(payload)
    )

  @patch("cfnresponse.send")
  def testBadEvent(self, mockSend):

    event = {
        "RequestType": "Create",
        "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:CustomResourceProxyLambda",
        "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A000011112222%3Astack/LittleOrangeGuardDuty/cbb30f50-0160-11eb-b815-0674a4b20bdc%7CGuardDutyOrganizationConfiguration%7Cec179708-db2f-433c-a365-750251237371?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20200928T084617Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20200928%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=0e51f6dd618a80ef28481fc1bd849571759cd1ba3827e620a882c49b679e4aee",
        "StackId": "arn:aws:cloudformation:ap-southeast-2:000011112222:stack/LittleOrangeGuardDuty/cbb30f50-0160-11eb-b815-0674a4b20bdc",
        "RequestId": "ec179708-db2f-433c-a365-750251237371",
        "LogicalResourceId": "GuardDutyOrganizationConfiguration",
        "ResourceType": "Custom::GuardDutyOrganizationConfiguration",
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:ap-southeast-2:000011112222:function:CustomResourceProxyLambda",
            "IncorrectParameters": "should have CustomResourceProperties"
        }
    }
    context = {}

    handler(event, context)

    mockSend.assert_called_with(event, context, cfnresponse.FAILED, "KeyError: 'CustomResourceProperties'")
