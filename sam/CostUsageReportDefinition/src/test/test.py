from botocore.stub import Stubber, ANY
import boto3
import datetime
import json
from unittest import TestCase
from unittest.mock import call, patch, Mock

from .. import app


def constructMocks(serviceNames):

  session = boto3.Session(aws_access_key_id="mock_access_key_id", aws_secret_access_key="mock_secret_access_key", aws_session_token="mock_session_token")
  services = {service: session.client(service) for service in serviceNames}
  stubs = {k: Stubber(v) for k, v in services.items()}

  mock = Mock()
  mock.return_value = mock
  mock.client.side_effect = lambda service, **kwargs: services[service]

  return mock, services, stubs


class Test(TestCase):

  def testCreate(self):

    mock, services, stubs = constructMocks(["cur"])

    with patch("boto3.client", new=mock.client):

      event = {
          "RequestType": "Create",
          "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-CostUsa-CloudFormationCustomReso-1VRRT8OXAC1H0",
          "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
          "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
          "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
          "LogicalResourceId": "CostUsageReport",
          "ResourceType": "Custom::CostUsageReportDefinition",
          "ResourceProperties": {
              "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-CostUsa-CloudFormationCustomReso-1VRRT8OXAC1H0",
              "ReportName": "LittleOrangeCostUsageReport",
              "ReportDefinition": {
                  "AdditionalArtifacts": [
                      "ATHENA"
                  ],
                  "Compression": "Parquet",
                  "Format": "Parquet",
                  "RefreshClosedReports": "false",
                  "S3Bucket": "littleorange-billing",
                  "ReportVersioning": "OVERWRITE_REPORT",
                  "S3Region": "ap-southeast-2",
                  "TimeUnit": "DAILY",
                  "S3Prefix": "LittleOrange",
                  "AdditionalSchemaElements": [
                      "RESOURCES"
                  ]
              }
          }
      }
      context = {}

      stubs["cur"].add_response(
          "put_report_definition",
          {},
          expected_params={
              "ReportDefinition": {
                  "ReportName": "LittleOrangeCostUsageReport",
                  "AdditionalArtifacts": [
                      "ATHENA"
                  ],
                  "Compression": "Parquet",
                  "Format": "Parquet",
                  "RefreshClosedReports": False,
                  "S3Bucket": "littleorange-billing",
                  "ReportVersioning": "OVERWRITE_REPORT",
                  "S3Region": "ap-southeast-2",
                  "TimeUnit": "DAILY",
                  "S3Prefix": "LittleOrange",
                  "AdditionalSchemaElements": [
                      "RESOURCES"
                  ]
              }
          }
      )

      for _, stub in stubs.items():
        stub.activate()

      app.create(event, context)

      assert mock.client.mock_calls == [
          call("cur", region_name="us-east-1")
      ]

  def testUpdate(self):

    mock, services, stubs = constructMocks(["cur"])

    with patch("boto3.client", new=mock.client):

      event = {
          "RequestType": "Update",
          "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-CostUsa-CloudFormationCustomReso-1VRRT8OXAC1H0",
          "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
          "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
          "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
          "LogicalResourceId": "CostUsageReport",
          "ResourceType": "Custom::CostUsageReportDefinition",
          "ResourceProperties": {
              "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-CostUsa-CloudFormationCustomReso-1VRRT8OXAC1H0",
              "ReportName": "LittleOrangeCostUsageReport",
              "ReportDefinition": {
                  "AdditionalArtifacts": [
                      "ATHENA"
                  ],
                  "Compression": "Parquet",
                  "Format": "Parquet",
                  "RefreshClosedReports": "true",
                  "S3Bucket": "littleorange-billing",
                  "ReportVersioning": "OVERWRITE_REPORT",
                  "S3Region": "ap-southeast-2",
                  "TimeUnit": "DAILY",
                  "S3Prefix": "LittleOrange",
                  "AdditionalSchemaElements": [
                      "RESOURCES"
                  ]
              }
          }
      }
      context = {}

      stubs["cur"].add_response(
          "modify_report_definition",
          {},
          expected_params={
              "ReportName": "LittleOrangeCostUsageReport",
              "ReportDefinition": {
                  "ReportName": "LittleOrangeCostUsageReport",
                  "AdditionalArtifacts": [
                      "ATHENA"
                  ],
                  "Compression": "Parquet",
                  "Format": "Parquet",
                  "RefreshClosedReports": True,
                  "S3Bucket": "littleorange-billing",
                  "ReportVersioning": "OVERWRITE_REPORT",
                  "S3Region": "ap-southeast-2",
                  "TimeUnit": "DAILY",
                  "S3Prefix": "LittleOrange",
                  "AdditionalSchemaElements": [
                      "RESOURCES"
                  ]
              }
          }
      )

      for _, stub in stubs.items():
        stub.activate()

      app.update(event, context)

      assert mock.client.mock_calls == [
          call("cur", region_name="us-east-1")
      ]

  def testDelete(self):

    mock, services, stubs = constructMocks(["cur"])

    with patch("boto3.client", new=mock.client):

      event = {
          "RequestType": "Delete",
          "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-CostUsa-CloudFormationCustomReso-1VRRT8OXAC1H0",
          "ResponseURL": "https://cloudformation-custom-resource-response-apsoutheast2.s3-ap-southeast-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aap-southeast-2%3A123456789012%3Astack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280%7CCostUsageReport%7C2db99329-c31e-439b-9aa0-38fcfd943ee2?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20201018T105949Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6MM33IIZTBPQJUYB%2F20201018%2Fap-southeast-2%2Fs3%2Faws4_request&X-Amz-Signature=99400812bf7218b5a8289dbe8e6d1073950f618082ea0b3e4b1626ecc0759047",
          "StackId": "arn:aws:cloudformation:ap-southeast-2:123456789012:stack/LittleOrange-Core-Billing/cc156700-112c-11eb-9721-0ad242f2b280",
          "RequestId": "2db99329-c31e-439b-9aa0-38fcfd943ee2",
          "LogicalResourceId": "CostUsageReport",
          "ResourceType": "Custom::CostUsageReportDefinition",
          "PhysicalResourceId": "LittleOrange-Core-Billing_CostUsageReport_42MQHE4H",
          "ResourceProperties": {
              "ServiceToken": "arn:aws:lambda:ap-southeast-2:123456789012:function:LittleOrange-Core-CostUsa-CloudFormationCustomReso-1VRRT8OXAC1H0",
              "ReportName": "LittleOrangeCostUsageReport",
              "ReportDefinition": {
                  "AdditionalArtifacts": [
                      "ATHENA"
                  ],
                  "Compression": "Parquet",
                  "Format": "Parquet",
                  "RefreshClosedReports": "true",
                  "S3Bucket": "littleorange-billing",
                  "ReportVersioning": "OVERWRITE_REPORT",
                  "S3Region": "ap-southeast-2",
                  "TimeUnit": "DAILY",
                  "S3Prefix": "LittleOrange",
                  "AdditionalSchemaElements": [
                      "RESOURCES"
                  ]
              }
          }
      }
      context = {}

      stubs["cur"].add_response(
          "delete_report_definition",
          {
              "ResponseMessage": "Report Definition successfully deleted"
          },
          expected_params={
              "ReportName": "LittleOrangeCostUsageReport"
          }
      )

      for _, stub in stubs.items():
        stub.activate()

      app.delete(event, context)

      assert mock.client.mock_calls == [
          call("cur", region_name="us-east-1")
      ]
