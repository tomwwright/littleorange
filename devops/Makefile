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
