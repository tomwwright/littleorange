import botocore
import boto3
import logging
import json
from . import stack


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def assume_role(account_id, region):
    sts = boto3.client("sts")
    role_name = "TransitGatewayRouteManagerRole"

    credentials = sts.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}", RoleSessionName="TransitGatewayRouteManager")
    logger.info(
        f"Assumed {role_name} in {account_id} for access key: {credentials['Credentials']['AccessKeyId']}")

    assumed = boto3.Session(
        aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
        aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
        aws_session_token=credentials["Credentials"]["SessionToken"],
        region_name=region
    )

    return assumed


def discover_attachment_tags(transit_gateway_attachment_arn):
    _, _, _, region, account_id, _ = transit_gateway_attachment_arn.split(":")
    _, transit_gateway_attachment_id = transit_gateway_attachment_arn.split(
        "/")

    session = assume_role(account_id, region)
    ec2 = session.client("ec2")

    response = ec2.describe_transit_gateway_attachments(
        TransitGatewayAttachmentIds=[transit_gateway_attachment_id]
    )
    transit_gateway_id = response["TransitGatewayAttachments"][0]["TransitGatewayId"]
    tags_as_dict = {tag["Key"]: tag["Value"]
                    for tag in response["TransitGatewayAttachments"][0]["Tags"]}

    return transit_gateway_id, tags_as_dict.get("TransitGateway:AssociateWith", "Default"), tags_as_dict.get("TransitGateway:PropagateTo", "Default").split(",")


def enumerate_transit_gateway_route_tables(transit_gateway_id):
    ec2 = boto3.client("ec2")

    route_tables_mapping = {}
    response = ec2.describe_transit_gateway_route_tables(
        Filters=[{"Name": "transit-gateway-id", "Values": [transit_gateway_id]}])
    while True:
        for table in response["TransitGatewayRouteTables"]:
            tags_as_dict = tags_as_dict = {
                tag["Key"]: tag["Value"] for tag in table["Tags"]}
            name_or_id = tags_as_dict.get(
                "Name", table["TransitGatewayRouteTableId"])

            route_tables_mapping[name_or_id] = table["TransitGatewayRouteTableId"]

        if "NextToken" in response:
            response = ec2.describe_transit_gateway_route_tables(
                Filters=[{"Name": "transit-gateway-id", "Values": [transit_gateway_id]}], NextToken=response["NextToken"])
        else:
            break

    return route_tables_mapping


def generate_stack_template(transit_gateway_attachment_arn):

    _, transit_gateway_attachment_id = transit_gateway_attachment_arn.split(
        "/")
    transit_gateway_id, associate_with, propagate_to = discover_attachment_tags(
        transit_gateway_attachment_arn)

    route_tables_mapping = enumerate_transit_gateway_route_tables(
        transit_gateway_id)
    logger.info(f"Route Tables Mapping: {route_tables_mapping}")
    associate_with = route_tables_mapping[associate_with]
    propagate_to = [route_tables_mapping[name] for name in propagate_to]

    template = stack.generate_cdk_stack_template(
        transit_gateway_attachment_id, associate_with, propagate_to)
    return template

def does_stack_exist(cloudformation, stack_name):
  try: 
    response = cloudformation.describe_stacks(
        StackName=stack_name
    )
    logger.info(f"CloudFormation DescribeStacks Response {response}")
    return True
  except botocore.exceptions.ClientError as e:
    if e.response["Error"]["Code"] == "ValidationError" and e.response["Error"]["Message"] == f"Stack with id {stack_name} does not exist":
      return False
    raise



def handle_attach(transit_gateway_attachment_arn):
    _, transit_gateway_attachment_id = transit_gateway_attachment_arn.split(
        "/")
    stack_name = f"TransitGatewayRouteManager-{transit_gateway_attachment_id}"
    cloudformation = boto3.client("cloudformation")

    stack_exists = does_stack_exist(cloudformation, stack_name)
    stack_template = json.dumps(
        generate_stack_template(transit_gateway_attachment_arn))

    if stack_exists:
        response = cloudformation.update_stack(
            StackName=stack_name,
            TemplateBody=stack_template,
        )
        logger.info(f"CloudFormation UpdateStack Response {response}")
    else:
        response = cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=stack_template,
        )
        logger.info(f"CloudFormation CreateStack Response {response}")


def handle_detach(transit_gateway_attachment_arn):

    _, transit_gateway_attachment_id = transit_gateway_attachment_arn.split(
        "/")
    stack_name = f"TransitGatewayRouteManager-{transit_gateway_attachment_id}"
    cloudformation = boto3.client("cloudformation")

    stack_exists = does_stack_exist(cloudformation, stack_name)

    if stack_exists:
        response = cloudformation.delete_stack(StackName=stack_name)
        logger.info(f"CloudFormation DeleteStack Response {response}")
    else:
        logger.info("Stack does not exist -- nothing to do")


def handler(event, context):
    logger.info(f"Received event: {event}")

    if event["detail"]["changeType"] == "VPC-ATTACHMENT-CREATED":
        handle_attach(event["detail"]["transitGatewayAttachmentArn"])

    if event["detail"]["changeType"] == "VPC-ATTACHMENT-DELETED":
        handle_detach(event["detail"]["transitGatewayAttachmentArn"])

def snshandler(sns_event, context):
  event = json.loads(sns_event["Records"][0]["Sns"]["Message"])
  return handler(event, context)


if __name__ == '__main__':
    template = stack.generate_cdk_stack_template("ATTACHMENT_ID", "ASSOCIATE_WITH", [
                                  "PROPAGATE_1", "PROPAGATE_2"])
    print(template)
