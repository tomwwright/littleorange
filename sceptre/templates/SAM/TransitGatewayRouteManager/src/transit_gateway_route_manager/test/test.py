from botocore.stub import Stubber, ANY
import boto3
import datetime
import json
from unittest import TestCase
from unittest.mock import call, patch, Mock

from .. import app, stack

test_event_created = {
    "version": "0",
    "id": "b980c34a-b6bd-3665-394e-97e2561ea82e",
    "detail-type": "Network Manager Topology Change",
    "source": "aws.networkmanager",
    "account": "730376727266",
    "time": "2021-04-13T11:26:49Z",
    "region": "us-west-2",
    "resources": [
        "arn:aws:networkmanager::730376727266:global-network/global-network-045b4adcd4fc2e8c7",
        "arn:aws:ec2:ap-southeast-2:730376727266:transit-gateway/tgw-0884b6f7fff781ea3"
    ],
    "detail": {
        "changeType": "VPC-ATTACHMENT-CREATED",
        "changeDescription": "A VPC attachment has been created.",
        "region": "ap-southeast-2",
        "transitGatewayAttachmentArn": "arn:aws:ec2:ap-southeast-2:730376727266:transit-gateway-attachment/tgw-attach-0374f7d5c0eb3e485",
        "vpcArn": "arn:aws:ec2:ap-southeast-2:730376727266:vpc/vpc-09c59db392c66a47a",
        "transitGatewayArn": "arn:aws:ec2:ap-southeast-2:730376727266:transit-gateway/tgw-0884b6f7fff781ea3"
    }
}

test_event_deleted = {
    "version": "0",
    "id": "cc16b592-dbd9-672b-dee4-5992422bbd1d",
    "detail-type": "Network Manager Topology Change",
    "source": "aws.networkmanager",
    "account": "730376727266",
    "time": "2021-04-15T11:36:50Z",
    "region": "us-west-2",
    "resources": [
        "arn:aws:networkmanager::730376727266:global-network/global-network-045b4adcd4fc2e8c7",
        "arn:aws:ec2:ap-southeast-2:730376727266:transit-gateway/tgw-0884b6f7fff781ea3"
    ],
    "detail": {
        "changeType": "VPC-ATTACHMENT-DELETED",
        "changeDescription": "A VPC attachment has been deleted.",
        "region": "ap-southeast-2",
        "transitGatewayAttachmentArn": "arn:aws:ec2:ap-southeast-2:730376727266:transit-gateway-attachment/tgw-attach-0374f7d5c0eb3e485",
        "vpcArn": "arn:aws:ec2:ap-southeast-2:730376727266:vpc/vpc-09c59db392c66a47a",
        "transitGatewayArn": "arn:aws:ec2:ap-southeast-2:730376727266:transit-gateway/tgw-0884b6f7fff781ea3"
    }
}

event_transit_gateway_attachment_id = "tgw-attach-0374f7d5c0eb3e485"
event_transit_gateway_id = "tgw-0884b6f7fff781ea3"
expected_stack_name = f"TransitGatewayRouteManager-{event_transit_gateway_attachment_id}"
expected_stack_template = json.dumps(stack.generate_cdk_stack_template(event_transit_gateway_attachment_id, "ROUTE_TABLE_ID_A", ["ROUTE_TABLE_ID_B", "ROUTE_TABLE_ID_C"]))

def constructMocks(serviceNames):

    session = boto3.Session(aws_access_key_id="mock_access_key_id",
                            aws_secret_access_key="mock_secret_access_key", aws_session_token="mock_session_token")
    services = {service: session.client(service) for service in serviceNames}
    stubs = {k: Stubber(v) for k, v in services.items()}

    mock = Mock()
    mock.return_value = mock
    mock.client.side_effect = lambda service, **kwargs: services[service]

    return mock, services, stubs

def setup_transit_gateway_responses(stubs):
  
  stubs["sts"].add_response(
      "assume_role",
      {"Credentials": {"AccessKeyId": "AccessKeyIdXXXXX", "SecretAccessKey": "SecretAccessKey",
                        "SessionToken": "SessionToken", "Expiration": datetime.datetime.now()}},
      expected_params={"RoleArn": "arn:aws:iam::730376727266:role/TransitGatewayRouteManagerRole",
                        "RoleSessionName": "TransitGatewayRouteManager"}
  )

  stubs["ec2"].add_response(
      "describe_transit_gateway_attachments",
      {
          "TransitGatewayAttachments": [
              {
                  # truncated object for testing
                  "TransitGatewayId": event_transit_gateway_id,
                  "TransitGatewayAttachmentId": event_transit_gateway_attachment_id,
                  "Tags": [
                      {
                          "Key": "TransitGateway:AssociateWith",
                          "Value": "RouteTableA"
                      },
                      {
                          "Key": "TransitGateway:PropagateTo",
                          "Value": "RouteTableB,RouteTableC"
                      },
                  ]
              },
          ]
      },
      expected_params={
          "TransitGatewayAttachmentIds": [event_transit_gateway_attachment_id]
      }
  )

  stubs["ec2"].add_response(
      "describe_transit_gateway_route_tables",
      {
          "TransitGatewayRouteTables": [
              {
                  "TransitGatewayRouteTableId": "ROUTE_TABLE_ID_A",
                  "TransitGatewayId": event_transit_gateway_id,
                  # truncated object for testing
                  "Tags": [
                      {
                          "Key": "Name",
                          "Value": "RouteTableA"
                      },
                  ]
              },
              {
                  "TransitGatewayRouteTableId": "ROUTE_TABLE_ID_B",
                  "TransitGatewayId": event_transit_gateway_id,
                  # truncated object for testing
                  "Tags": [
                      {
                          "Key": "Name",
                          "Value": "RouteTableB"
                      },
                  ]
              }
          ],
          "NextToken": "NextToken1234"
      },
      expected_params={
          "Filters": [{"Name": "transit-gateway-id", "Values": [event_transit_gateway_id]}]
      }
  )

  stubs["ec2"].add_response(
      "describe_transit_gateway_route_tables",
      {
          "TransitGatewayRouteTables": [
              {
                  "TransitGatewayRouteTableId": "ROUTE_TABLE_ID_C",
                  "TransitGatewayId": event_transit_gateway_id,
                  # truncated object for testing
                  "Tags": [
                      {
                          "Key": "Name",
                          "Value": "RouteTableC"
                      },
                  ]
              },
          ]
      },
      expected_params={
          "Filters": [{"Name": "transit-gateway-id", "Values": [event_transit_gateway_id]}],
          "NextToken": "NextToken1234"
      }
  )

class Test(TestCase):

    def testCreate(self):

        mock, service, stubs = constructMocks(
            ["cloudformation", "ec2", "sts"])

        with patch("boto3.client", new=mock.client):
            with patch("boto3.Session", new=mock):

                context = {}

                setup_transit_gateway_responses(stubs)

                stubs["cloudformation"].add_client_error("describe_stacks", "ValidationError", f"Stack with id {expected_stack_name} does not exist", 404)

                stubs["cloudformation"].add_response(
                    "create_stack",
                    {
                        "StackId": "Placeholder"
                    },
                    expected_params={
                        "StackName": expected_stack_name,
                        "TemplateBody": expected_stack_template
                    }
                )

                for _, stub in stubs.items():
                    stub.activate()

                app.handler(test_event_created, context)

                assert mock.client.mock_calls == [
                    call("cloudformation"),
                    call("sts"),
                    call("ec2"),
                    call("ec2"),
                ]

    def testUpdate(self):

        mock, service, stubs = constructMocks(
            ["cloudformation", "ec2", "sts"])

        with patch("boto3.client", new=mock.client):
            with patch("boto3.Session", new=mock):

                context = {}

                setup_transit_gateway_responses(stubs)

                stubs["cloudformation"].add_response(
                  "describe_stacks",
                  {
                    "Stacks": [
                      {
                        "StackId": "Placeholder",
                        "StackName": expected_stack_name,
                        "CreationTime": datetime.datetime.now(),
                        "StackStatus": "Placeholder"
                      }
                    ]
                  },
                  expected_params={
                    "StackName": expected_stack_name
                  }
                )
                stubs["cloudformation"].add_response(
                    "update_stack",
                    {
                        "StackId": "Placeholder"
                    },
                    expected_params={
                        "StackName": expected_stack_name,
                        "TemplateBody": expected_stack_template
                    }
                )

                for _, stub in stubs.items():
                    stub.activate()

                app.handler(test_event_created, context)

                assert mock.client.mock_calls == [
                    call("cloudformation"),
                    call("sts"),
                    call("ec2"),
                    call("ec2"),
                ]

    def testDelete(self):

        mock, service, stubs = constructMocks(
            ["cloudformation", "ec2", "sts"])

        with patch("boto3.client", new=mock.client):
            with patch("boto3.Session", new=mock):

                context = {}

                stubs["cloudformation"].add_response(
                  "describe_stacks",
                  {
                    "Stacks": [
                      {
                        "StackId": "Placeholder",
                        "StackName": expected_stack_name,
                        "CreationTime": datetime.datetime.now(),
                        "StackStatus": "Placeholder"
                      }
                    ]
                  },
                  expected_params={
                    "StackName": expected_stack_name
                  }
                )

                stubs["cloudformation"].add_response(
                    "delete_stack",
                    {},
                    expected_params={
                        "StackName": expected_stack_name
                    } 
                )

                for _, stub in stubs.items():
                    stub.activate()

                app.handler(test_event_deleted, context)

                assert mock.client.mock_calls == [
                    call("cloudformation")
                ]

    def testDeleteNoExists(self):

        mock, service, stubs = constructMocks(
            ["cloudformation"])

        with patch("boto3.client", new=mock.client):
            with patch("boto3.Session", new=mock):

                context = {}

                stubs["cloudformation"].add_client_error("describe_stacks", "ValidationError", f"Stack with id {expected_stack_name} does not exist", 404)

                for _, stub in stubs.items():
                    stub.activate()

                app.handler(test_event_deleted, context)

                assert mock.client.mock_calls == [
                    call("cloudformation")
                ]

