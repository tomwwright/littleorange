#
# Little Orange Core Makefile
#

deploy-core: GuardDutyOrganizationAdminServiceToken=`aws cloudformation describe-stacks --stack-name LittleOrangeGuardDutyOrganizationAdmin --query 'Stacks[0].Outputs[?OutputKey==\`ServiceToken\`].OutputValue' --output text`
deploy-core: ## Deploy 'Core' - Organizations configuration
	$(info [+] Deploying Little Orange 'Core')
	aws cloudformation deploy \
		--template-file core/Organizations.cfn.yml \
		--stack-name LittleOrangeCore \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset
	aws cloudformation deploy \
		--template-file core/SAMDeploymentResources.cfn.yml \
		--stack-name LittleOrangeSAMDeploymentResources \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			OrganizationId=`aws organizations describe-organization --query 'Organization.Id' --output text`
