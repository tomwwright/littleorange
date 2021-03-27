import re
import os
import traceback
import json
import logging

from .macro import NetworkingVPCMacro

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handle(event):
  macro = NetworkingVPCMacro()
  template = event["fragment"]
  parameters = event.get("templateParameterValues", {})

  return macro.transform(template, parameters)


def handler(event, context):
  logger.info(f"Received event: {event}")
  response = {
      "requestId": event["requestId"],
      "status": "success"
  }
  try:
    fragment = handle(event)
    response["fragment"] = fragment
  except Exception as e:
    traceback.print_exc()
    response["status"] = "failure"
    response["errorMessage"] = str(e)

  logger.info(json.dumps(response["fragment"]))

  logger.info(f"Returning response: {response}")
  return response
