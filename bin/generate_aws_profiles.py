#!/usr/bin/env python3

"""
1.4 AWS SDK Profiles Generation

Generate AWS Profile stubs for Little Orange AWS Accounts for AWS CLI Configuration
"""

import boto3
import argparse
import configparser
import sys

def argument_parser():
  parser = argparse.ArgumentParser(description=__doc__)

  parser.add_argument('--profile-type', choices=["ECS", "SOURCE_PROFILE"], default="ECS", help='AWS CLI profile type to generate')

  return parser

def generate_profiles(profile_type):
  try:
    organizations = boto3.client("organizations")
    accounts = [account for page in organizations.get_paginator("list_accounts").paginate() for account in page["Accounts"]]
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    accounts = []

  created_accounts = [account for account in accounts if account["JoinedMethod"] == "CREATED"]

  config = configparser.ConfigParser()

  for account in created_accounts:
    account_name = account["Name"]
    account_id = account["Id"]

    if profile_type == "ECS":
      add_ecs_profile(config, account_name, account_id)
    elif profile_type == "SOURCE_PROFILE":
      add_source_profile_profile(config, account_name, account_id)
  
  return config

def add_ecs_profile(config, account_name, account_id):
  config[f"profile LittleOrange{account_name}"] = {
        "role_arn": f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole",
        "credential_source": "EcsContainer"
    }

def add_source_profile_profile(config, account_name, account_id):
  config[f"profile LittleOrange{account_name}"] = {
        "role_arn": f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole",
        "source_profile": "LittleOrangeManagement"
    }

def main():

  parser = argument_parser()
  args = parser.parse_args()

  config = generate_profiles(args.profile_type)
  config.write(sys.stdout)

if __name__ == '__main__':
  main()
