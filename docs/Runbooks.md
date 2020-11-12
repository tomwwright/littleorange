# Little Orange Runbooks

This page documents instructions for deploying Little Orange.

## Prerequisites

- Docker
- Python 3 (+ `pip`)
- AWS CLI

## Development Environment Setup

Little Orange uses `pipenv` for managing Python dependencies.

```sh
# install pipenv and project dependencies
make Pipenv
```

Little Orange contains some small Python libraries that are required, primarily by Sceptre.

```sh
# install Python libraries
make InstallLib
```

Linting can be run via `Make` targets

```sh
# cfn-lint is run via Docker image due to dependency conflict, need to build cfn-lint image
make DockerBuildCfnLint

# run linting
make LintYaml
make LintCloudFormation

# run all linting
make Lint
```

Python `pytest` tests can be run via `Make` target

```sh
# run Python tests
make TestPython
```

## Configuring GitHub Credentials in target AWS account

Valid GitHub credentials (in form of a Personal Access Token / PAT) need to be provided and configured in the target AWS account if deployment automation is leveraged. Permissions on the Little Orange repository need to be `Admin` when deploying deployment automation because of webhook registration.

```sh
# deploy GitHub credentials -- careful not to let them get saved in shell history!
 export GitHubToken=[GITHUB-PAT-TOKEN]
make DeployGitHubCredentials GitHubUsername=tomwwright
```

## CloudFormation Resource Providers for AWS Organizations

Little Orange deployment leverages Resource Providers for AWS Organizations resources, so these need to be deployed first. DevOps automation exists for handling deployment of the Resource Providers, and to manage deploying changes as they occur in version control.

```sh
# deploy deployment automation for a single resource provider
make DeployResourceProviderDevOps ResourceProvider=OrganizationsAccount

# deploy deployment automation for all resource providers
make DeployResourceProviders

# other useful targets...
make ValidateResourceProvider ResourceProvider=OrganizationsAccount   # run validation of Resource Provider schema using CloudFormation CLI
make SubmitResourceProvider ResourceProvider=OrganizationsAccount     # manually execute Resource Provider submission
```

### Attach KMS Key Alias to managed upload infrastructure deployed by CloudFormation CLI

The CloudFormation CLI responsible for deploying the Resource Providers deploys some ancillary infrastructure for handling uploads to S3. Part of this infrastructure is a KMS Key without an alias, which makes it difficult to identify when inspecting KMS Keys.

```sh
# execute after at least one Resource Provider has been deployed to attach KMS Key Alias
make CreateKMSKeyAliasForCloudFormationCLI
```

## Deploying Little Orange

Little Orange is deployed via Sceptre. Deployment automation exists for running Little Orange deployment from AWS CodeBuild, and configuring a webhook to ensure deployment is executed for new changes in version control and tests are run against pull requests on the repository.

```sh
# deploy Little Orange deployment automation
make DeployPipeline
```
