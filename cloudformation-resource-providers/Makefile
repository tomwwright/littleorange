#
# CloudFormation Resource Providers Makefile
#

validate-resource-provider: needs-ResourceProvider ## Run validation on Resource Provider using CFN CLI, e.g. validate-resouce-provider ResourceProvider=littleorange-organizations-organization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn validate

submit-resource-provider: needs-ResourceProvider ## Submit Resource Provider using CFN CLI, e.g. submit-resouce-provider ResourceProvider=littleorange-organizations-organization
	cd cloudformation-resource-providers/${ResourceProvider} && cfn submit --set-default
