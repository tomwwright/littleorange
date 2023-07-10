#!/usr/bin/env python3

# 2.2.2 CloudFormation Macro Proxy

import os
import yaml

from aws_cdk import (
    core as Cdk,
    aws_iam as Iam,
    aws_lambda as Lambda
)


class CloudFormationMacroProxyStack(Cdk.Stack):

  def __init__(self, scope: Cdk.Construct, id: str, **kwargs) -> None:
    super().__init__(
        scope,
        id,
        description="Lambda function for invoking cross-region CloudFormation Macros",
        **kwargs
    )

    lookupRegionParameter = Cdk.CfnParameter(
        self, "LookupRegion", description="Region that Macro Proxy will look up SSM Parameters in", type="String")

    path = os.path.join(os.path.dirname(__file__), "src/app.py")
    with open(path) as f:
      code = Lambda.Code.from_inline(f.read())

    function = Lambda.Function(
        self, "Function",
        code=code,
        environment={
            "LOOKUP_AWS_REGION": lookupRegionParameter.value_as_string
        },
        function_name="LittleOrangeCloudFormationMacroProxy",
        handler="index.handler",
        runtime=Lambda.Runtime.PYTHON_3_7,
        timeout=Cdk.Duration.seconds(30)
    )

    function.add_permission(
        "CloudFormationPermission",
        principal=Iam.ServicePrincipal("cloudformation.amazonaws.com"),
        action="lambda:InvokeFunction"
    )

    # Allowing Principal * is a security issue
    # https://github.com/tomwwright/littleorange/issues/29
    function.add_permission(
        "AllAccountsPermission",
        principal=Iam.AccountPrincipal("*"),
        action="lambda:InvokeFunction"
    )

    function.add_to_role_policy(
        Iam.PolicyStatement(
            actions=["lambda:InvokeFunction"],
            effect=Iam.Effect.ALLOW,
            resources=["*"]
        )
    )

    function.add_to_role_policy(
        Iam.PolicyStatement(
            actions=["ssm:GetParameter"],
            effect=Iam.Effect.ALLOW,
            resources=["arn:aws:ssm:*:*:parameter/LittleOrange/CloudFormation/*"]
        )
    )

    output = Cdk.CfnOutput(
        self, "LambdaArn",
        value=function.function_arn
    )

    output = Cdk.CfnOutput(
        self, "LambdaName",
        value=function.function_name
    )


def synth():

  app = Cdk.App()

  stack = CloudFormationMacroProxyStack(app, "CloudFormationMacroProxy")

  return app.synth().get_stack_by_name("CloudFormationMacroProxy").template


def sceptre_handler(sceptre_user_data):
  template = synth()
  return yaml.dump(template)


if __name__ == "__main__":
  template = synth()
  print(yaml.dump(template))
