BuildEnableIsOrganizationTrail:
	cd logging/EnableIsOrganizationTrail; \
	sam build; \
	sam package

BuildGuardDutyOrganizationAdmin:
	cd logging/GuardDutyOrganizationAdmin; \
	sam build; \
	sam package

BuildGuardDutyOrganizationConfiguration:
	cd logging/GuardDutyOrganizationConfiguration; \
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

DeployGuardDutyDelegated: DetectorId=`aws guardduty list-detectors --query 'DetectorIds[0]' --output text`
DeployGuardDutyDelegated: GuardDutyOrganizationConfigurationServiceToken=`aws cloudformation describe-stacks --stack-name LittleOrangeGuardDutyOrganizationConfiguration --query 'Stacks[0].Outputs[?OutputKey==\`ServiceToken\`].OutputValue' --output text`
DeployGuardDutyDelegated: MasterAccountEmail=`aws organizations list-accounts --query 'Accounts[?Name==\`Thomas Wright\`].Email' --output text`
DeployGuardDutyDelegated: MasterAccountId=`aws organizations list-accounts --query 'Accounts[?Name==\`Thomas Wright\`].Id' --output text`
DeployGuardDutyDelegated: SandboxAccountEmail=`aws organizations list-accounts --query 'Accounts[?Name==\`Sandbox\`].Email' --output text`
DeployGuardDutyDelegated: SandboxAccountId=`aws organizations list-accounts --query 'Accounts[?Name==\`Sandbox\`].Id' --output text`
DeployGuardDutyDelegated:
	$(info [+] Deploying Little Orange GuardDuty Organization Admin)
	aws cloudformation deploy \
		--template-file logging/GuardDutyDelegated.cfn.yml \
		--stack-name LittleOrangeGuardDuty \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
				DetectorId=${DetectorId} \
				GuardDutyOrganizationConfigurationServiceToken=${GuardDutyOrganizationConfigurationServiceToken} \
				MasterAccountEmail=${MasterAccountEmail} \
				MasterAccountId=${MasterAccountId} \
				SandboxAccountEmail=${SandboxAccountEmail} \
				SandboxAccountId=${SandboxAccountId}

DeployGuardDutyMaster: GuardDutyAdminAccountId=`aws organizations list-accounts --query 'Accounts[?Name==\`Security\`].Id' --output text`
DeployGuardDutyMaster: GuardDutyOrganizationAdminServiceToken=`aws cloudformation describe-stacks --stack-name LittleOrangeGuardDutyOrganizationAdmin --query 'Stacks[0].Outputs[?OutputKey==\`ServiceToken\`].OutputValue' --output text`
DeployGuardDutyMaster:
	$(info [+] Deploying Little Orange GuardDuty for Organization Master)
	aws cloudformation deploy \
		--template-file logging/GuardDutyMaster.cfn.yml \
		--stack-name LittleOrangeGuardDuty \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
				GuardDutyAdminAccountId=${GuardDutyAdminAccountId} \
				GuardDutyOrganizationAdminServiceToken=${GuardDutyOrganizationAdminServiceToken}

DeployGuardDutyOrganizationAdmin: BuildGuardDutyOrganizationAdmin
DeployGuardDutyOrganizationAdmin:
	$(info [+] Deploying GuardDutyOrganizationAdmin CloudFormation Custom Resource)
	cd logging/GuardDutyOrganizationAdmin; \
	sam deploy \
		--stack-name LittleOrangeGuardDutyOrganizationAdmin \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset

DeployGuardDutyOrganizationConfiguration: BuildGuardDutyOrganizationConfiguration
DeployGuardDutyOrganizationConfiguration:
	$(info [+] Deploying GuardDutyOrganizationConfiguration CloudFormation Custom Resource)
	cd logging/GuardDutyOrganizationConfiguration; \
	sam deploy \
		--stack-name LittleOrangeGuardDutyOrganizationConfiguration \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset