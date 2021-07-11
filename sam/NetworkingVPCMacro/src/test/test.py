import copy
import json
import os
from unittest import TestCase

from ..macro import app, util


class Test(TestCase):

  def testResolveParameter(self):
    parameters = util.StackParameters({
        "A": "One",
        "B": "Two",
        "C": "Three",
        "D": ["Four", "Five"]
    })

    assert parameters.resolve({"Ref": "A"}) == "One"
    assert parameters.resolve({"Fn::Ref": "B"}) == "Two"
    assert parameters.resolve("Literal") == "Literal"
    assert parameters.resolve(123) == 123
    assert parameters.resolve({
        "Fn::Join": [
            ",",
            [{"Ref": "A"}, {"Ref": "C"}]
        ]
    }) == "One,Three"
    assert parameters.resolve({
        "Fn::Split": [
            ",",
            "Hello,World"
        ]
    }) == ["Hello", "World"]
    assert parameters.resolve({
        "Fn::Split": [
            ",",
            {
                "Fn::Join": [
                    ",",
                    [{"Ref": "B"}, {"Ref": "A"}, {"Ref": "C"}]
                ]
            }
        ]
    }) == ["Two", "One", "Three"]
    assert parameters.resolve({
        "Fn::Split": [
            ",",
            {
                "Fn::Join": [
                    ",",
                    [
                        {"Ref": "B"},
                        {
                            "Fn::Join": [
                                ",",
                                {"Ref": "D"}
                            ]
                        }
                    ]
                ]
            }
        ]
    }) == ["Two", "Four", "Five"]

  def testNoop(self):

    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Little Orange CloudFormation Macro for LittleOrange::Networking::VPC Resource",
        "Resources": {
            "CloudFormationMacroFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Description": "CloudFormation Macro for LittleOrange::Networking::VPC Resource",
                    "CodeUri": "./src",
                    "Handler": "app.handler",
                    "MemorySize": 128,
                    "Runtime": "python3.8",
                    "Role": {"Ref": "Role"},
                    "Timeout": 30
                }
            },
            "CloudFormationMacroPermission": {
                "Type": "AWS::Lambda::Permission",
                "Properties": {
                    "Action": "lambda:InvokeFunction",
                    "FunctionName": {"GetAtt": "CloudFormationMacroFunction.Arn"},
                    "Principal": "cloudformation.amazonaws.com"
                }
            },
            "Role": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "lambda.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    },
                    "Path": "/LittleOrange/",
                    "Policies": [
                        {
                            "PolicyName": "CloudWatchLogs",
                            "PolicyDocument": {
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": [
                                            "logs:CreateLogGroup",
                                            "logs:CreateLogStream",
                                            "logs:PutLogEvents"
                                        ],
                                        "Resource": "*"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        },
        "Outputs": {
            "FunctionArn": {
                "Value": {"GetAtt": "CloudFormationMacroFunction.Arn"}
            }
        }
    }

    event = {
        "region": "us-east-1",
        "accountId": "000011112222",
        "fragment": template,
        "transformId": "LittleOrange::Networking::VPC",
        "params": {},
        "requestId": "REQUEST_ID_0001",
        "templateParameterValues": {}
    }
    context = {}

    response = app.handler(event, context)

    assert response["status"] == "success"
    assert response["requestId"] == event["requestId"]
    assert response["fragment"] == event["fragment"]

  def testBasicVPC(self):

    with open(os.path.join(os.path.dirname(__file__), "fixtures/BasicVPCInput.cfn.json"), 'r') as f:
      inputTemplate = json.load(f)
    with open(os.path.join(os.path.dirname(__file__), "fixtures/BasicVPCOutput.cfn.json"), 'r') as f:
      outputTemplate = json.load(f)

    event = {
        "region": "us-east-1",
        "accountId": "000011112222",
        "fragment": inputTemplate,
        "transformId": "LittleOrange::Networking::VPC",
        "params": {},
        "requestId": "REQUEST_ID_0002",
        "templateParameterValues": {
            "VPCCIDR": "10.0.0.0/22"
        }
    }
    context = {}

    response = app.handler(event, context)

    assert response["status"] == "success"
    assert response["requestId"] == event["requestId"]
    assert response["fragment"] == outputTemplate

  def testMinimalVPC(self):

    with open(os.path.join(os.path.dirname(__file__), "fixtures/MinimalVPCInput.cfn.json"), 'r') as f:
      inputTemplate = json.load(f)
    with open(os.path.join(os.path.dirname(__file__), "fixtures/MinimalVPCOutput.cfn.json"), 'r') as f:
      outputTemplate = json.load(f)

    event = {
        "region": "us-east-1",
        "accountId": "000011112222",
        "fragment": inputTemplate,
        "transformId": "LittleOrange::Networking::VPC",
        "params": {},
        "requestId": "REQUEST_ID_0002",
        "templateParameterValues": {
            "VPCCIDR": "10.0.0.0/22"
        }
    }
    context = {}

    response = app.handler(event, context)

    assert response["status"] == "success"
    assert response["requestId"] == event["requestId"]
    assert response["fragment"] == outputTemplate

  def testDifferentSizesVPC(self):

    with open(os.path.join(os.path.dirname(__file__), "fixtures/DifferentSizesVPCInput.cfn.json"), 'r') as f:
      inputTemplate = json.load(f)
    with open(os.path.join(os.path.dirname(__file__), "fixtures/DifferentSizesVPCOutput.cfn.json"), 'r') as f:
      outputTemplate = json.load(f)

    event = {
        "region": "us-east-1",
        "accountId": "000011112222",
        "fragment": inputTemplate,
        "transformId": "LittleOrange::Networking::VPC",
        "params": {},
        "requestId": "REQUEST_ID_0002",
        "templateParameterValues": {
            "VPCCIDR": "10.0.0.0/22"
        }
    }
    context = {}

    response = app.handler(event, context)

    assert response["status"] == "success"
    assert response["requestId"] == event["requestId"]
    assert response["fragment"] == outputTemplate

  def testGetAttVPC(self):

    with open(os.path.join(os.path.dirname(__file__), "fixtures/GetAttVPCInput.cfn.json"), 'r') as f:
      inputTemplate = json.load(f)
    with open(os.path.join(os.path.dirname(__file__), "fixtures/GetAttVPCOutput.cfn.json"), 'r') as f:
      outputTemplate = json.load(f)

    event = {
        "region": "us-east-1",
        "accountId": "000011112222",
        "fragment": inputTemplate,
        "transformId": "LittleOrange::Networking::VPC",
        "params": {},
        "requestId": "REQUEST_ID_0002",
        "templateParameterValues": {
            "VPCCIDR": "10.0.0.0/22"
        }
    }
    context = {}

    response = app.handler(event, context)

    assert response["status"] == "success"
    assert response["requestId"] == event["requestId"]
    assert response["fragment"] == outputTemplate
