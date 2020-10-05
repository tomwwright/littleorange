#
# CloudFormation Resource Providers Makefile
#

ValidateResourceProvider: needs-ResourceProvider ## Run validation on Resource Provider using CFN CLI, e.g. validate-resouce-provider ResourceProvider=OrganizationsOrganization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn validate

SubmitResourceProvider: needs-ResourceProvider ## Submit Resource Provider using CFN CLI, e.g. submit-resouce-provider ResourceProvider=OrganizationsOrganization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn submit --set-default -v

DeployResourceProviderDevOps: needs-ResourceProvider ## Deploy CodeBuild projects with webhooks for running tests and deployments for a CloudFormation Resource Provider
	$(info [+] Deploying DevOps for CloudFormation Resource Provider '${ResourceProvider}')
	aws cloudformation deploy \
		--template-file cloudformation-resource-providers/devops/cloudformation/ResourceProvider.cfn.yml \
		--stack-name LitleOrangeResourceProvider${ResourceProvider} \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			$(call CloudFormationParam,ResourceProvider)