# Command - Sceptre Custom Resolver

Sceptre Custom Resolver as per https://sceptre.cloudreach.com/2.3.0/docs/resolvers.html

Resolves argument as a shell command

```yml
# config/MyGroup/MyStack.yaml
---
template_path: MyStack.yaml
parameters:
  WhereAmI: !Command aws sts get-caller-identity --query 'Account' --output text
```

## Environment Variables

Environment variables `AWS_DEFAULT_REGION` and `AWS_PROFILE` are set in the command's environment if they are set by Sceptre configuration (`region` and `profile`)
