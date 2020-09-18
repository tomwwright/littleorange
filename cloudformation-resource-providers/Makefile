#
# CloudFormation Resource Providers Makefile
#

validate-resource-provider: needs-ResourceProvider ## Run validation on Resource Provider using CFN CLI, e.g. validate-resouce-provider ResourceProvider=littleorange-organizations-organization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn validate

submit-resource-provider: needs-ResourceProvider ## Submit Resource Provider using CFN CLI, e.g. submit-resouce-provider ResourceProvider=littleorange-organizations-organization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn submit --set-default -v

deploy-resource-provider-devops: needs-ResourceProvider ## Deploy CodeBuild projects with webhooks for running tests and deployments for a CloudFormation Resource Provider
	$(info [+] Deploying DevOps for CloudFormation Resource Provider '${ResourceProvider}')
	aws cloudformation deploy \
		--template-file cloudformation-resource-providers/devops/cloudformation/ResourceProvider.cfn.yml \
		--stack-name LitleOrangeResourceProvider-${ResourceProvider} \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			$(call CloudFormationParam,ResourceProvider)