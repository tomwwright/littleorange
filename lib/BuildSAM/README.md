#  Little Orange Sceptre Integration for AWS SAM

> 1.1.3 AWS SAM Build Integration Library

This library provides a Python entrypoint to invoke `make` to build an AWS SAM project and then read and return the resulting CloudFormation template.

## Usage

Invoke from a [Sceptre handler](../../sceptre/templates/BuildSAM.py)

```python
from littleorange_build_sam import sam

def sceptre_handler(sceptre_user_data):
  template = sam.build_sam(sceptre_user_data)
  return template
```

## Options

```python
from littleorange_build_sam import sam

parameters = {
  "SAMProject": "ExampleProject"    # invokes 'make BuildExampleProject' to trigger AWS SAM build. Required.
  "ApplySAMTranslate": True | False # apply the AWS SAM Transform inline to transform the resulting template into vanilla CloudFormation
}

template = sam.build_sam(parameters)
```

