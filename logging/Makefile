
BuildGuardDutyOrganizationConfiguration:
	cd logging/GuardDutyOrganizationConfiguration; \
	sam build; \
	sam package

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

DeployGuardDutyOrganizationConfiguration: BuildGuardDutyOrganizationConfiguration
DeployGuardDutyOrganizationConfiguration:
	$(info [+] Deploying GuardDutyOrganizationConfiguration CloudFormation Custom Resource)
	cd logging/GuardDutyOrganizationConfiguration; \
	sam deploy \
		--stack-name LittleOrangeGuardDutyOrganizationConfiguration \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset