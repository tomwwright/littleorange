# -----------------------------
# 2.1.1 CloudFormation Resource Providers for AWS Organizations
# -----------------------------

ValidateResourceProvider: NeedsResourceProvider ## 2.1.1 Run validation on Resource Provider using CFN CLI, e.g. validate-resouce-provider ResourceProvider=OrganizationsOrganization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn validate

SubmitResourceProvider: NeedsResourceProvider ## 2.1.1 Submit Resource Provider using CFN CLI, e.g. submit-resouce-provider ResourceProvider=OrganizationsOrganization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn submit --set-default -v

DeployResourceProviderDevOps: NeedsResourceProvider ## 2.1.1 Deploy CodeBuild projects with webhooks for running tests and deployments for a CloudFormation Resource Provider
	$(info [+] Deploying DevOps for CloudFormation Resource Provider '${ResourceProvider}')
	aws cloudformation deploy \
		--template-file cloudformation-resource-providers/devops/cloudformation/ResourceProvider.cfn.yml \
		--stack-name LitleOrangeResourceProvider${ResourceProvider} \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			$(call CloudFormationParam,ResourceProvider)

DeployResourceProviders: ## 2.1.1 Deploys DevOps automation for all Resource Providers
	@ $(MAKE) DeployResourceProviderDevOps ResourceProvider=OrganizationsAccount
	@ $(MAKE) DeployResourceProviderDevOps ResourceProvider=OrganizationsOrganization
	@ $(MAKE) DeployResourceProviderDevOps ResourceProvider=OrganizationsOrganizationalUnit
	@ $(MAKE) DeployResourceProviderDevOps ResourceProvider=OrganizationsServiceControlPolicy

# CloudFormation CLI deploys a CloudFormation stack for uploading resources when deploying resource providers
# This target attaches an alias to the KMS Key that is deployed so it is identifiable. Run this target after at least one resource provider has been deployed
CreateKMSKeyAliasForCloudFormationCLI: KmsKeyId=$(shell aws cloudformation describe-stack-resources --stack-name CloudFormationManagedUploadInfrastructure --logical-resource-id EncryptionKey --query 'StackResources[0].PhysicalResourceId' --output text)
CreateKMSKeyAliasForCloudFormationCLI:
	$(info [+] Creating KMS Key Alias for CloudFormationManagedUploadInfrastructure (${KmsKeyId}))
	aws kms create-alias --alias-name alias/CloudFormationManagedUploadInfrastructure --target-key-id ${KmsKeyId}

HackPipenvForCloudFormationCLI:
	pip install 'urllib3<1.26' 'colorama>=0.4.1' 'networkx~=2.4'
