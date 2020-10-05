#
# DevOps Makefile
# 

DeployGitHubCredentials: ## Deploy stack to store GitHub credentials in Secrets Manager and create CodeBuild credentials
	$(info [+] Deploying GitHub credentials...)
	aws cloudformation deploy \
		--template-file devops/cloudformation/GithubCredentials.cfn.yml \
		--stack-name LittleOrangeGithubCredentials \
		--no-fail-on-empty-changeset \
		--parameter-overrides a=b \
			$(call CloudFormationParam,GitHubToken) \
			$(call CloudFormationParam,GitHubUsername)

DeployPipeline: ## Deploy CodeBuild projects with webhook to run tests on GitHub pull requests and deploy on merge
	$(info [+] Deploying GitHub Pull Request tests)
	aws cloudformation deploy \
		--template-file devops/cloudformation/LittleOrangePipeline.cfn.yml \
		--stack-name LittleOrangePipeline \
		--capabilities CAPABILITY_IAM \
		--no-fail-on-empty-changeset
