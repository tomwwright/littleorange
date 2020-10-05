# LilOrange::Organizations:Organization Resource Provider

## Commands

Regenerate code from schema definition

```
cfn generate
```

Build code to be able to run tests (don't forget to monkey patch -- see below)

```
cfn submit --dry-run
```

Run tests (excluding problematic test -- see below)

```
cfn test -- -k 'not contract_invalid_create'
```

Submit resource provider to CloudFormation

```
cfn submit

# or, to submit and also set default version

cfn submit --set-default
```

Update default version of submitted type

```
aws cloudformation set-type-default-version --arn arn:aws:cloudformation:ap-southeast-2:933397847440:type/resource/LilOrange-Organizations-Organization/00000003
# or
aws cloudformation set-type-default-version --type RESOURCE --type-name LilOrange::Organizations::Organization --version-id 00000002 
```

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