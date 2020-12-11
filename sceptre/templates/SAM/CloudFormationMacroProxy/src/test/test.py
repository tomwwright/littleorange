import boto3
from botocore.stub import Stubber
from io import BytesIO
import json
import os
from unittest import TestCase
from unittest.mock import call, patch, Mock

from .. import app


def constructMocks():

  session = boto3.Session(aws_access_key_id="mock_access_key_id", aws_secret_access_key="mock_secret_access_key", aws_session_token="mock_session_token")
  services = {s: session.client(s) for s in ["ssm", "lambda"]}
  stubs = {k: Stubber(v) for k, v in services.items()}

  mock = Mock()
  mock.return_value = mock
  mock.client.side_effect = lambda service, **kwargs: services[service]

  return mock, services, stubs


class Test(TestCase):

  def testSuccess(self):

    mock, services, stubs = constructMocks()

    event = {
        'accountId': '933397847440',
        'fragment': {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'Little Orange Minimal VPC',
            'Parameters': {
                'VPCCIDR': {
                    'Type': 'String'
                }
            },
            'Metadata': {
                'cfn-lint': {
                    'config': {
                        'ignore_checks': ['E3001']
                    }
                }
            },
            'Resources': {
                'VPC': {
                    'Type': 'LittleOrange::Networking::VPC',
                    'Properties': {
                            'AvailabilityZones': 2,
                            'CIDR': {
                                'Ref': 'VPCCIDR'
                            },
                        'InternetGateway': False,
                        'NATGateways': False
                    }
                }
            }
        },
        'transformId': '933397847440::NetworkingVPC',
        'requestId': '0fe67481-875a-40c5-b0c8-a5189c178662',
        'region': 'ap-southeast-2',
        'params': {},
        'templateParameterValues': {
            'VPCCIDR': '10.0.0.0/24'
        }
    }
    context = {}

    expectedPayload = {
        "ReturnedFragment": "AsJson"
    }

    with patch("boto3.client", new=mock.client):
      with patch.dict(os.environ, {"LOOKUP_AWS_REGION": "ap-southeast-1"}):
        stubs["ssm"].add_response(
            "get_parameter",
            {
                "Parameter": {
                    "Name": "/LittleOrange/CloudFormation/Macro/NetworkingVPC",
                    "Type": "String",
                    "Value": "arn:aws:lambda:ap-south-1:933397847440:function:LittleOrange-Core-VPCMacr-CloudFormationMacroFunct-7LO4YC80J73Y",
                    "Version": 1,
                    "LastModifiedDate": 1579074189.439,
                    "ARN": "arn:aws:ssm:ap-southeast-1:933397847440:parameter/LittleOrange/CloudFormation/Macro/NetworkingVPC",
                    "DataType": "text"
                }
            },
            expected_params={"Name": "/LittleOrange/CloudFormation/Macro/NetworkingVPC"}
        )
        stubs["lambda"].add_response(
            "invoke",
            {
                'StatusCode': 200,
                'LogResult': 'string',
                'Payload': BytesIO(json.dumps(expectedPayload).encode("utf-8")),
                'ExecutedVersion': '1'
            },
            expected_params={
                "FunctionName": "arn:aws:lambda:ap-south-1:933397847440:function:LittleOrange-Core-VPCMacr-CloudFormationMacroFunct-7LO4YC80J73Y", "Payload": json.dumps(event)}
        )

        for _, stub in stubs.items():
          stub.activate()

        response = app.handler(event, context)

    assert mock.client.mock_calls == [
        call("ssm", region_name="ap-southeast-1"),
        call("lambda", region_name="ap-south-1"),
    ]

    assert response == expectedPayload

  def testFailure(self):

    mock, services, stubs = constructMocks()

    event = {
        'accountId': '933397847440',
        'fragment': {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'Little Orange Minimal VPC',
            'Parameters': {
                'VPCCIDR': {
                    'Type': 'String'
                }
            },
            'Metadata': {
                'cfn-lint': {
                    'config': {
                        'ignore_checks': ['E3001']
                    }
                }
            },
            'Resources': {
                'VPC': {
                    'Type': 'LittleOrange::Networking::VPC',
                    'Properties': {
                            'AvailabilityZones': 2,
                            'CIDR': {
                                'Ref': 'VPCCIDR'
                            },
                        'InternetGateway': False,
                        'NATGateways': False
                    }
                }
            }
        },
        'transformId': '933397847440::NetworkingVPC',
        'requestId': '0fe67481-875a-40c5-b0c8-a5189c178662',
        'region': 'ap-southeast-2',
        'params': {},
        'templateParameterValues': {
            'VPCCIDR': '10.0.0.0/24'
        }
    }
    context = {}

    with patch("boto3.client", new=mock.client):
      with patch.dict(os.environ, {"LOOKUP_AWS_REGION": "ap-southeast-1"}):
        stubs["ssm"].add_response(
            "get_parameter",
            {
                "Parameter": {
                    "Name": "/LittleOrange/CloudFormation/Macro/NetworkingVPC",
                    "Type": "String",
                    "Value": "arn:aws:lambda:ap-south-1:933397847440:function:LittleOrange-Core-VPCMacr-CloudFormationMacroFunct-7LO4YC80J73Y",
                    "Version": 1,
                    "LastModifiedDate": 1579074189.439,
                    "ARN": "arn:aws:ssm:ap-southeast-1:933397847440:parameter/LittleOrange/CloudFormation/Macro/NetworkingVPC",
                    "DataType": "text"
                }
            },
            expected_params={"Name": "/LittleOrange/CloudFormation/Macro/NetworkingVPC"}
        )
        stubs["lambda"].add_response(
            "invoke",
            {
                'StatusCode': 500,
                'FunctionError': "Yeah something bad happened",
                'LogResult': 'string',
                'Payload': BytesIO(json.dumps({"Error": "Things occurred bad"}).encode("utf-8")),
                'ExecutedVersion': '1'
            },
            expected_params={
                "FunctionName": "arn:aws:lambda:ap-south-1:933397847440:function:LittleOrange-Core-VPCMacr-CloudFormationMacroFunct-7LO4YC80J73Y", "Payload": json.dumps(event)}
        )

        for _, stub in stubs.items():
          stub.activate()

        response = app.handler(event, context)

    assert mock.client.mock_calls == [
        call("ssm", region_name="ap-southeast-1"),
        call("lambda", region_name="ap-south-1"),
    ]

    assert response == {
        "requestId": '0fe67481-875a-40c5-b0c8-a5189c178662',
        "status": "failure",
        "error": {"Error": "Things occurred bad"}
    }
