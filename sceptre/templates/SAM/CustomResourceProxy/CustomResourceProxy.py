#!/usr/bin/env python3

import os
import yaml

from aws_cdk import (
    core as Cdk,
    aws_iam as Iam,
    aws_lambda as Lambda,
    aws_ssm as Ssm
)


class CustomResourceProxyStack(Cdk.Stack):

  def __init__(self, scope: Cdk.Construct, id: str, **kwargs) -> None:
    super().__init__(
        scope,
        id,
        description="CloudFormation Custom Resource Lambda for invoking cross-region Custom Resources",
        **kwargs
    )

    path = os.path.join(os.path.dirname(__file__), "src/app.py")
    with open(path) as f:
      code = Lambda.Code.from_inline(f.read())

    function = Lambda.Function(
        self, "Function",
        code=code,
        function_name="CustomResourceProxy",
        handler="index.handler",
        runtime=Lambda.Runtime.PYTHON_3_7,
        timeout=Cdk.Duration.seconds(30)
    )

    function.add_permission(
        "CloudFormationPermission",
        principal=Iam.ServicePrincipal("cloudformation.amazonaws.com"),
        action="lambda:InvokeFunction"
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

    output = Cdk.CfnOutput(
        self, "ServiceToken",
        value=function.function_arn
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
