# littleorange

Stay tuned

## Roadmap

| Category      | Feature                  | Implementation                     |
| ------------- | ------------------------ | ---------------------------------- |
| DevOps        | Pipeline                 | CodePipeline, CodeBuild            |
| Organisations | Org, OUs, SCPs, Accounts | CloudFormation Resource Providders |

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
