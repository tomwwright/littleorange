import json
import boto3
import logging
import os

# 2.2.2 CloudFormation Macro Proxy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def invokeMacroLambda(lambdaArn, event, requestId):
  region = lambdaArn.split(":")[3]
  lambdaClient = boto3.client("lambda", region_name=region)
  response = lambdaClient.invoke(
      FunctionName=lambdaArn,
      Payload=json.dumps(event)
  )
  payload = json.loads(response["Payload"].read().decode())

  if "FunctionError" in response:
    return {
        "requestId": requestId,
        "status": "failure",
        "error": payload
    }
  else:
    return payload


def retrieveMacroLambdaArn(region, macroName):
  ssmParameterName = f"/LittleOrange/CloudFormation/Macro/{macroName}"
  ssm = boto3.client("ssm", region_name=region)
  parameter = ssm.get_parameter(Name=ssmParameterName)
  macroLambdaArn = parameter["Parameter"]["Value"]

  return macroLambdaArn


def handler(event, context):

  logger.info(f"Received event: {event}")

  region = os.environ.get("LOOKUP_AWS_REGION", os.environ.get("AWS_REGION"))
  requestId = event["requestId"]
  transformId = event["transformId"].split("::")[1]   # transformId format is '000011112222:MacroName' where 000011112222 is account id

  macroLambdaArn = retrieveMacroLambdaArn(region, transformId)
  logger.info(f"Executing Macro Lambda ARN: {macroLambdaArn}")

  response = invokeMacroLambda(macroLambdaArn, event, requestId)
  logger.info(f"Returning response: {response}")
  return response
