#
# Little Orange Core Makefile
#

deploy-core: ## Deploy 'Core' - Organizations configuration
	$(info [+] Deploying Little Orange 'Core')
	aws cloudformation deploy \
		--template-file core/Organizations.cfn.yml \
		--stack-name LittleOrangeCore \
		--capabilities CAPABILITY_NAMED_IAM \
		--no-fail-on-empty-changeset