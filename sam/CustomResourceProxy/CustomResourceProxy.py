#!/usr/bin/env python3

"""
2.2.1 CloudFormation Custom Resource Proxy
"""

import os
import yaml

from aws_cdk import (
    core as Cdk,
    aws_iam as Iam,
    aws_lambda as Lambda,
    aws_sns as Sns,
    aws_ssm as Ssm
)


class CustomResourceProxyStack(Cdk.Stack):

  def __init__(self, scope: Cdk.Construct, id: str, **kwargs) -> None:
    super().__init__(
        scope,
        id,
        description="2.2.1 CloudFormation Custom Resource Lambda for invoking cross-region Custom Resources",
        **kwargs
    )

    allowedRoleNameParameter = Cdk.CfnParameter(
        self, "AllowedRoleName", description="Role name to allow to publish to the SNS topic of the Custom Resource Proxy to enable cross-account use", type="String")
    organizationIdParameter = Cdk.CfnParameter(
        self, "OrganizationId", description="Organization ID to use to allow access to the SNS topic of the Custom Resource Proxy", type="String")

    path = os.path.join(os.path.dirname(__file__), "src/app.py")
    with open(path) as f:
      code = Lambda.Code.from_inline(f.read())

    function = Lambda.Function(
        self, "Function",
        code=code,
        function_name="LittleOrangeCustomResourceProxy",
        handler="index.handler",
        runtime=Lambda.Runtime.PYTHON_3_7,
        timeout=Cdk.Duration.seconds(30)
    )

    topic = Sns.Topic(
        self, "Topic",
        topic_name="LittleOrangeCustomResourceProxy"
    )

    topic.add_to_resource_policy(
        statement=Iam.PolicyStatement(
            sid="OrganizationsCloudFormationAccess",
            actions=["sns:Publish"],
            conditions={
                "StringLike": {
                    "aws:PrincipalArn": f"arn:aws:iam::*:role/{allowedRoleNameParameter.value_as_string}"
                },
                "StringEquals": {
                    "aws:CalledViaLast": "cloudformation.amazonaws.com",
                    "aws:PrincipalOrgID": organizationIdParameter.value_as_string
                }
            },
            effect=Iam.Effect.ALLOW,
            principals=[
                Iam.AnyPrincipal()
            ],
            resources=[topic.topic_arn]
        )
    )

    subscription = Sns.Subscription(
        self, "TopicSubscription",
        topic=topic,
        endpoint=function.function_arn,
        protocol=Sns.SubscriptionProtocol.LAMBDA
    )

    function.add_permission(
        "CloudFormationPermission",
        principal=Iam.ServicePrincipal("cloudformation.amazonaws.com"),
        action="lambda:InvokeFunction"
    )

    function.add_permission(
        "SNSPermission",
        principal=Iam.ServicePrincipal("sns.amazonaws.com"),
        action="lambda:InvokeFunction",
        source_arn=topic.topic_arn
    )

    function.add_to_role_policy(
        Iam.PolicyStatement(
            actions=["lambda:InvokeFunction"],
            effect=Iam.Effect.ALLOW,
            resources=["*"]
        )
    )

    parameter = Ssm.StringParameter(
        self, "ServiceTokenParameter",
        parameter_name="/LittleOrange/CloudFormation/CustomResourceProxyServiceToken",
        description="Lambda ARN for the Custom Resource Proxy CloudFormation Custom Resource in this region",
        type=Ssm.ParameterType.STRING,
        string_value=function.function_arn
    )

    parameterSns = Ssm.StringParameter(
        self, "SNSServiceTokenParameter",
        parameter_name="/LittleOrange/CloudFormation/CustomResourceProxySNSServiceToken",
        description="SNS Topic ARN for the Custom Resource Proxy CloudFormation Custom Resource in this region",
        type=Ssm.ParameterType.STRING,
        string_value=topic.topic_arn
    )

    output = Cdk.CfnOutput(
        self, "ServiceToken",
        value=function.function_arn
    )

    snsOutput = Cdk.CfnOutput(
        self, "SNSServiceToken",
        value=topic.topic_arn
    )


def synth():

  app = Cdk.App()

  stack = CustomResourceProxyStack(app, "CustomResourceProxy")

  return app.synth().get_stack_by_name("CustomResourceProxy").template


def sceptre_handler(sceptre_user_data):
  template = synth()
  return yaml.dump(template)


if __name__ == "__main__":
  template = synth()
  print(yaml.dump(template))
