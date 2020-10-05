#
#	Makefile
#

include */Makefile

deploy: deploy-pipeline SceptreCore SceptreSecurity ## Deploy Little Orange

docker-lint-cloudformation: CfnLint=docker run --rm -v ${PWD}:/path --name cfn-lint cfn-lint:latest
docker-lint-cloudformation: lint-cloudformation

GenerateAWSProfiles:
	@ python3 bin/generate_aws_profiles.py

install: pipenv SceptreInstallResolvers

lint: lint-yaml docker-lint-cloudformation ## Run all linting

CfnLint ?= cfn-lint

lint-cloudformation: ## Run CloudFormation linting with cfn-lint
	$(info [+] Linting CloudFormation templates...)
	${CfnLint} '**/*.cfn.yml' '**/*.sam.yml' 'cloudformation-resource-providers/**/template.yml' 'cloudformation-resource-providers/**/resource-role.yaml'

lint-yaml:	## Run YAML linting with yamllint (see .yamllint.yml for config)
	$(info [+] Linting YAML files...)
	yamllint .

pipenv:	## Install Pipenv and use it to create virtual environment of Python dependencies
	$(info [+] Initialising Pipenv...)
	pip install pipenv
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
	pipenv --venv
	pipenv run python --version

#
# Utils
#

needs-%: ## Helper target that errors if % isn't set -- i.e. check-TOKEN ensures TOKEN is set
	@: $(if $(value $*),,$(error $* is a required parameter!))

help: ## Help documentation
	@ echo ""
	@ echo "+------------------------------------+"
	@ echo "|        LITTLE ORANGE HELP          |"
	@ echo "+------------------------------------+"
	@ echo ""
	@ echo "Available targets:"
	@ echo ""
	@ cat $(MAKEFILE_LIST) | grep '##' | sort | awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-%]+:.*?## / {printf "\033[36m%-30s\033[0m%s\n", $$1, $$2}'

# Helper function that prints variable out in format MyParameter=${MyParameter} if set, otherwise prints nothing
CloudFormationParam = $(if $(value $(1)), $(1)=$(value $(1)),)

.DEFAULT_GOAL := help