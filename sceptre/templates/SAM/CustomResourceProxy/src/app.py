import json
import os
import boto3
import logging
import cfnresponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def constructProxiedEvent(event):
  """
  Unwrap the nested CustomResourceProperties to construct the proxied event that will
  be forwarded to the wrapped ServiceToken Lambda
  """

  return {
      **event,
      "ResourceProperties": event["ResourceProperties"]["CustomResourceProperties"],
      "ServiceToken": event["ResourceProperties"]["CustomResourceProperties"]["ServiceToken"]
  }


def unwrapSnsMessage(event):
  """
  Unwrap and parse an SNS message event, or return as-is if not an SNS event
  """

  try:
    unwrappedEvent = json.loads(event["Records"][0]["Sns"]["Message"])
    return unwrappedEvent
  except KeyError:
    logger.warning(f"Unable to parse as SNS payload -- treating as native Lambda event")
    return event


def handle(event, context):
  """
  Invoke the nested ServiceToken with a rebuilt event. Does not communicate any 
  success or failure back to CloudFormation -- that is the job of the proxied function
  """

  logger.info(f"Received event: {event}")

  proxiedEvent = constructProxiedEvent(event)

  logger.debug(f"Proxied event: {proxiedEvent}")

  lambdaArn = proxiedEvent["ServiceToken"]
  lambdaRegion = lambdaArn.split(":")[3]

  logger.debug(f"Proxying to '{lambdaArn}' in '{lambdaRegion}'")

  lambdaClient = boto3.client('lambda', region_name=lambdaRegion)

  response = lambdaClient.invoke(
      FunctionName=lambdaArn,
      InvocationType="Event",
      Payload=json.dumps(proxiedEvent)
  )

  logger.info(f"Lambda Invoke Response: {response}")


def handler(event, context):
  """
  Communicates any failure back to CloudFormation to avoid hangs and handles unwrapping of potential SNS event
  """
  try:
    event = unwrapSnsMessage(event)
    handle(event, context)
  except Exception as e:
    logger.exception(e)
    cfnresponse.send(event, context, cfnresponse.FAILED, f"{e.__class__.__name__}: {e}")
