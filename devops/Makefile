#
# DevOps Makefile
# 

deploy-github-credentials: ## Deploy stack to store GitHub credentials in Secrets Manager
	$(info [+] Deploying GitHub credentials...)
	aws cloudformation deploy \
		--template-file devops/cloudformation/GithubCredentials.cfn.yml \
		--stack-name LittleOrangeGithubCredentials \
		--no-fail-on-empty-changeset \
		--parameter-overrides a=b \
			$(call CloudFormationParam,GitHubToken) \
			$(call CloudFormationParam,GitHubUsername)

deploy-pull-request-tests: ## Deploy CodeBuild project with webhook that runs tests on GitHub pull requests
	$(info [+] Deploying GitHub Pull Request tests)
	aws cloudformation deploy \
		--template-file devops/cloudformation/PRTests.cfn.yml \
		--stack-name LittleOrangePRTests \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset

deploy-resource-provider-devops: needs-ResourceProvider ## Deploy CodeBuild projects with webhooks for running tests and deployments for a CloudFormation Resource Provider
	$(info [+] Deploying DevOps for CloudFormation Resource Provider '${ResourceProvider}')
	aws cloudformation deploy \
		--template-file devops/cloudformation/ResourceProvider.cfn.yml \
		--stack-name LitleOrangeResourceProvider-${ResourceProvider} \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset \
		--parameter-overrides \
			$(call CloudFormationParam,ResourceProvider)