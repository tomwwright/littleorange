# littleorange

Stay tuned

## Roadmap

| Category      | Feature                  | Implementation                     |
| ------------- | ------------------------ | ---------------------------------- |
| DevOps        | Pipeline                 | CodePipeline, CodeBuild            |
| Organisations | Org, OUs, SCPs, Accounts | CloudFormation Resource Providders |

| Category        | Feature                                            | Implementation                                        |
| --------------- | -------------------------------------------------- | ----------------------------------------------------- |
| Core            | CI/CD DevOps Pipeline                              | GitHub, CodeBuild                                     |
| Core            | Organizations                                      | CloudFormation Resource Providers                     |
| Core            | Account Onboarding                                 | CloudFormation Resource Providers                     |
| Core            | Cost and Usage Reports                             | `???`                                                 |
| IAM             | Federated Login                                    | AWS SSO                                               |
| IAM             | Delegated IAM                                      | IAM Permissions Boundary                              |
| Logging + Audit | CloudTrail                                         | Cfn Stack + Custom Resource (for IsOrganizationTrail) |
| Logging + Audit | Config                                             | Cfn Stack + StackSet                                  |
| Logging + Audit | GuardDuty                                          | Cfn Stack + StackSet                                  |
| Networking      | VPC Factory                                        | CloudFormation Macro, Service Catalogue               |
| Networking      | Route 53 Hosted Zone (integrated with VPC Factory) | `???`                                                 |
| Networking      | Route 53 Resolvers                                 | `???`                                                 |
| Networking      | Transit Gateway                                    | `???`                                                 |
| Networking      | Centralised VPC Endpoints                          | `???`                                                 |
| Networking      | Centralised Egress                                 | Squid in Fargate                                      |
| Cost Management | Instance Scheduling                                | `???`                                                 |

- Automated account creation and onboarding
- GuardDuty
- CloudTrail
- Config
- Security Hub
- VPC Flow Logs
- Centralised CloudWatch Logging
- Automated Athena configuration/consumption of the above
- Delete default VPC
- CIS Compliance checks and autoremediation where possible
- SSM Patching (baseline scan and scaffold to implement)
- Instance scheduling
- Route 53 Resolvers
- Centralised VPC Endpoints (resolvable from workload VPCs)
- AWS SSO
- Developer IAM Role with Permissions Boundary
- VPC Factory via Service Catalogue

### AWS Organisations

- Create AWS Organisation
- Create SCPs
- Create OUs
- Assign SCPs to OUs
- Create accounts
- Assign accounts to OUs

## Tools and Implementation

- Make
- CloudFormation
- Python
- CloudFormation Resource Providers - https://docs.amazonaws.cn/en_us/cloudformation-cli/latest/userguide/what-is-cloudformation-cli.html

### Python Unit Testing

Unit Testing of Python

- moto - https://github.com/spulec/moto - mock implementations of `boto3`
- Botocore Stubber - https://botocore.amazonaws.com/v1/documentation/api/latest/reference/stubber.html - provided stubbing in botocore
- Python Mocking - https://docs.python.org/3/library/unittest.mock.html - roll own mocking from scratch in Python (not preferred)
