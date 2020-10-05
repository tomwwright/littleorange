#!/usr/bin/env python3

import boto3
import configparser
import sys


def main():

  try:
    organizations = boto3.client("organizations")
    accounts = [account for page in organizations.get_paginator("list_accounts").paginate() for account in page["Accounts"]]
  except organizations.exceptions.AWSOrganizationsNotInUseException:
    accounts = []

  createdAccounts = [account for account in accounts if account["JoinedMethod"] == "CREATED"]

  config = configparser.ConfigParser()

  for account in createdAccounts:
    accountName = account["Name"]
    accountId = account["Id"]

    config[f"profile LittleOrange{accountName}"] = {
        "role_arn": f"arn:aws:iam::{accountId}:role/OrganizationAccountAccessRole",
        "credential_source": "EcsContainer"
    }

  config.write(sys.stdout)


if __name__ == '__main__':
  main()
