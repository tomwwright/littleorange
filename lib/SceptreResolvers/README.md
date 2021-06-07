# Little Orange Sceptre Custom Resolvers

> 1.1.2 Sceptre Resolver Library

Sceptre Custom Resolvers as per https://sceptre.cloudreach.com/2.3.0/docs/resolvers.html

## Command

Resolves argument as a shell command

```yml
# config/MyGroup/MyStack.yaml
---
template_path: MyStack.yaml
parameters:
  WhereAmI: !Command aws sts get-caller-identity --query 'Account' --output text
```

### Environment Variables

Environment variables `AWS_DEFAULT_REGION` and `AWS_PROFILE` are set in the command's environment if they are set by Sceptre configuration (`region` and `profile`)

## Upload S3

Uploads argument to S3 and resolves to the uploaded S3 URL. Resolved URL is in a format consumable by `TemplateURL` of CloudFormation StackSet. Resolving nested Sceptre Resolver tags is supported one level deep, see example.

```yml
# config/MyGroup/MyStackSet.yaml
---
template_path: MyStackSet.yaml
parameters:
  TemplateURL: !UploadS3
    Bucket: my-deployment-s3-bucket
    Content: !file_contents "{{ project_path }}/templates/MyStack.yaml"
    Key: Sceptre/MyStack # optional, adds prefix to hash
# TemplateUrl: https://my-deployment-s3-bucket.s3.amazonaws.com/Sceptre/MyStack/[MD5HashOfContent]
```
