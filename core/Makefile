#
# Little Orange Core Makefile
#

BuildGuardDutyOrganizationAdmin:
	cd core/GuardDutyOrganizationAdmin; \
	sam build; \
	sam package

deploy-core: GuardDutyOrganizationAdminServiceToken=`aws cloudformation describe-stacks --stack-name LittleOrangeGuardDutyOrganizationAdmin --query 'Stacks[0].Outputs[?OutputKey==\`ServiceToken\`].OutputValue' --output text`
deploy-core: ## Deploy 'Core' - Organizations configuration
	$(info [+] Deploying Little Orange 'Core')
	aws cloudformation deploy \
		--template-file core/Organizations.cfn.yml \
		--stack-name LittleOrangeCore \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			GuardDutyOrganizationAdminServiceToken=${GuardDutyOrganizationAdminServiceToken}
	aws cloudformation deploy \
		--template-file core/SAMDeploymentResources.cfn.yml \
		--stack-name LittleOrangeSAMDeploymentResources \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			OrganizationId=`aws organizations describe-organization --query 'Organization.Id' --output text`

DeployGuardDutyOrganizationAdmin: BuildGuardDutyOrganizationAdmin
DeployGuardDutyOrganizationAdmin:
	$(info [+] Deploying GuardDutyOrganizationAdmin CloudFormation Custom Resource)
	cd core/GuardDutyOrganizationAdmin; \
	sam deploy \
		--stack-name LittleOrangeGuardDutyOrganizationAdmin \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset