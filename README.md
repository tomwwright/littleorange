# littleorange

Stay tuned

## Roadmap

| Category      | Feature                  | Implementation                     |
| ------------- | ------------------------ | ---------------------------------- |
| DevOps        | Pipeline                 | CodePipeline, CodeBuild            |
| Organisations | Org, OUs, SCPs, Accounts | CloudFormation Resource Providders |

| Category        | Feature                                            | Implementation                                        | Progress         |
| --------------- | -------------------------------------------------- | ----------------------------------------------------- | ---------------- |
| Core            | CI/CD DevOps Pipeline                              | GitHub, CodeBuild                                     | `[==>       ]  0%` |
| Core            | Organizations                                      | CloudFormation Resource Providers                     | `[======>   ] 60%` |
| Core            | Account Creation and Onboarding                    | CloudFormation Resource Providers + Step Function     | `[          ]  0%` |
| Core            | Cost and Usage Reports                             | `???`                                                 | `[          ]  0%` |
| IAM             | Federated Login                                    | AWS SSO                                               | `[          ]  0%` |
| IAM             | Delegated IAM                                      | IAM Permissions Boundary                              | `[          ]  0%` |
| Logging + Audit | CloudTrail                                         | Cfn Stack + Custom Resource (for IsOrganizationTrail) | `[======>   ] 60%` |
| Logging + Audit | Config                                             | Cfn Stack + StackSet                                  | `[          ]  0%` |
| Logging + Audit | GuardDuty                                          | Cfn Stack + StackSet                                  | `[=====>    ] 50%` |
| Networking      | VPC Factory                                        | CloudFormation Macro, Service Catalogue               | `[          ]  0%` |
| Networking      | Route 53 Hosted Zone (integrated with VPC Factory) | `???`                                                 | `[          ]  0%` |
| Networking      | Route 53 Resolvers                                 | `???`                                                 | `[          ]  0%` |
| Networking      | Transit Gateway                                    | `???`                                                 | `[          ]  0%` |
| Networking      | Centralised VPC Endpoints                          | `???`                                                 | `[          ]  0%` |
| Networking      | Centralised Egress                                 | Squid in Fargate                                      | `[          ]  0%` |
| Cost Management | Instance Scheduling                                | `???`                                                 | `[          ]  0%` |

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
