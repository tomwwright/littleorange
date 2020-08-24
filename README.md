# littleorange
Stay tuned

## Roadmap

| Category      | Feature                           | Implementation |
| ------------- | --------------------------------- | -------------- |
| DevOps        | Pipeline                          | CodePipeline   |
| Organisations | Org creation -- OUs/SCPs/Accounts | ?              |
|               | Account Factory                   | ?              |


### AWS Organisations

- Create AWS Organisation
- Create SCPs
- Create OUs
- Assign SCPs to OUs
- Create accounts

## Generate code for resource providers

Use CloudFormation CLI to generate model code from schema definition
```
cd cloudformation-resource-providers/organizations-organization
cfn generate
```

## cloudformation_cli_python_lib.exceptions.InternalFailure: __init__() got an unexpected keyword argument 'region/awsPartition/awsAccountId' (TypeError)

Caused by changes to the contract test request format upstream https://github.com/aws-cloudformation/cloudformation-cli/pull/502

Partial fix applied here https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/pull/107/files, but `cloudformation-cli-python-lib` hasn't released as `v2.1.0` on `pypi` yet

Solution for now is to monkey patch dataclass in `build/cloudformation_cli_python_lib/utils.py` to expect the extra fields:

```py
@dataclass
class UnmodelledRequest:
  clientRequestToken: str
  desiredResourceState: Optional[Mapping[str, Any]] = None
  previousResourceState: Optional[Mapping[str, Any]] = None
  logicalResourceIdentifier: Optional[str] = None
  nextToken: Optional[str] = None       
  region: Optional[str] = None          # <--- add these
  awsAccountId: Optional[str] = None    # <---
  awsPartition: Optional[str] = None    # <---
```

## contract_invalid_create test fails

Running `cfn test -- -k contract_invalid_create` fails with this error:

```
cloudformation_cli_python_lib.exceptions.InternalFailure: __init__() got an unexpected keyword argument 'Arn' (TypeError)
```

Investigating the payload provided to the test endpoint, it fails because the resource properties are in the top-level request object instead of being in `desiredResourceState` and `previousResourceState`.

This seems to be a bug in the code that is generating the "invalid" create request.

Solution is to run tests excluding this problematic test:

```
cfn test -- -k 'not contract_invalid_create'
```