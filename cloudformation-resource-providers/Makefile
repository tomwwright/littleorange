
validate-littleorange-organizations-organizations: ResourceProvider=littleorange-organizations-organization
validate-littleorange-organizations-organizations: validate-resource-provider

validate-resource-provider: needs-ResourceProvider
	cd cloudformation-resource-providers/${ResourceProvider} && cfn validate

submit-resource-provider: needs-ResourceProvider
	cd cloudformation-resource-providers/${ResourceProvider} && cfn submit --set-default
