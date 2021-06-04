import boto3
import cfnresponse
import json
from unittest import TestCase
from unittest.mock import patch, Mock

from .. import app


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

    app.handler(event, context)

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

    app.handler(event, context)

    mockSend.assert_called_with(event, context, cfnresponse.FAILED, "KeyError: 'CustomResourceProperties'")

  @patch.object(app, "handle")
  def testSnsEvent(self, mockHandle):

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
    snsEvent = {
        "Records": [
            {
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
                "EventSource": "aws:sns",
                "Sns": {
                    "SignatureVersion": "1",
                    "Timestamp": "2019-01-02T12:45:07.000Z",
                    "Signature": "tcc6faL2yUC6dgZdmrwh1Y4cGa/ebXEkAi6RibDsvpi+tE/1+82j...65r==",
                    "SigningCertUrl": "https://sns.us-east-2.amazonaws.com/SimpleNotificationService-ac565b8b1a6c5d002d285f9598aa1d9b.pem",
                    "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                    "Message": json.dumps(event),
                    "MessageAttributes": {
                        "Test": {
                            "Type": "String",
                            "Value": "TestString"
                        },
                        "TestBinary": {
                            "Type": "Binary",
                            "Value": "TestBinary"
                        }
                    },
                    "Type": "Notification",
                    "UnsubscribeUrl": "https://sns.us-east-2.amazonaws.com/?Action=Unsubscribe&amp;SubscriptionArn=arn:aws:sns:us-east-2:123456789012:test-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
                    "TopicArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda",
                    "Subject": "TestInvoke"
                }
            }
        ]
    }

    context = {}

    app.handler(snsEvent, context)

    mockHandle.assert_called_with(event, context)

  @patch.object(app, "handle")
  def testNotSnsEvent(self, mockHandle):

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

    app.handler(event, context)

    mockHandle.assert_called_with(event, context)
