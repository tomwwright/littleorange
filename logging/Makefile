BuildEnableIsOrganizationTrail:
	cd logging/EnableIsOrganizationTrail; \
	sam build; \
	sam package

DeployCloudTrail: EnableIsOrganizationTrailServiceToken=`aws cloudformation describe-stacks --stack-name LittleOrangeEnableIsOrganizationTrail --query 'Stacks[0].Outputs[?OutputKey==\`ServiceToken\`].OutputValue' --output text`
DeployCloudTrail:
	$(info [+] Deploying Little Orange CloudTrail)
	aws cloudformation deploy \
		--template-file logging/CloudTrail.cfn.yml \
		--stack-name LittleOrangeCloudTrail \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
				EnableIsOrganizationTrailServiceToken=${EnableIsOrganizationTrailServiceToken}

DeployEnableIsOrganizationTrail: BuildEnableIsOrganizationTrail
DeployEnableIsOrganizationTrail:
	$(info [+] Deploying EnableIsOrganizationTrail CloudFormation Custom Resource)
	cd logging/EnableIsOrganizationTrail; \
	sam deploy \
		--stack-name LittleOrangeEnableIsOrganizationTrail \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset
