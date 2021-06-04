import os
import boto3
import logging
from crhelper import CfnResource
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
helper = CfnResource(json_logging=True, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

def transform_response_data(response):
  data = {}


  data["IpAddresses"] = [ip["Ip"] for ip in response["IpAddresses"]]
  data["IpAddressSubnetIds"] = [ip["SubnetId"] for ip in response["IpAddresses"]]
  data["IpAddressStatuses"] = [ip["Status"] for ip in response["IpAddresses"]]

  return data

@helper.create
def create(event, context):
  logger.info("Performing CREATE")

  route53resolver = boto3.client("route53resolver")

  response = route53resolver.list_resolver_endpoint_ip_addresses(ResolverEndpointId=event["ResourceProperties"]["ResolverEndpointId"])
  logger.info(f"Route53Resolver ListResolverEndpointIpAddresses {response}")

  helper.Data = transform_response_data(response)

@helper.delete
def delete(event, context):
  logger.info("Performing DELETE")

  # Delete is no-op


@helper.update
def update(event, context):
  logger.info("Performing UPDATE as CREATE")

  create(event, context)


def handler(event, context):
  logger.info(f"Received event: {event}")
  helper(event, context)
