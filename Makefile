#
#	Makefile
#

CfnLint ?= cfn-lint

include */Makefile

Deploy: DeployPipeline SceptreCore SceptreSecurity ## Deploy Little Orange

DockerLintCloudFormation: ## Run LintCloudFormation target but within Docker image for cfn-lint
DockerLintCloudFormation: CfnLint=docker run --rm -v ${PWD}:/path --name cfn-lint cfn-lint:latest
DockerLintCloudFormation: LintCloudFormation

GenerateAWSProfiles:
	@ python3 bin/generate_aws_profiles.py

Install: DockerBuildCfnLint InstallLib

InstallLib: ## Install project Python libraries using pip
	pip install lib/*

Lint: LintYaml DockerLintCloudFormation ## Run all linting

LintCloudFormation: ## Run CloudFormation linting with cfn-lint
	$(info [+] Linting CloudFormation templates...)
	${CfnLint} '**/*.cfn.yml' '**/*.sam.yml' 'cloudformation-resource-providers/**/template.yml' 'cloudformation-resource-providers/**/resource-role.yaml'

LintYaml:	## Run YAML linting with yamllint (see .yamllint.yml for config)
	$(info [+] Linting YAML files...)
	yamllint .

Pipenv:	## Install Pipenv and use it to create virtual environment of Python dependencies
	$(info [+] Initialising Pipenv...)
	pip install pipenv
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
	pipenv --venv
	pipenv run python --version

TestPython: ## Run pytest tests
	$(info [+] Running Python tests with pytest...)
	pipenv run pytest

#
# Utils
#

needs-%: ## Helper target that errors if % isn't set -- i.e. check-TOKEN ensures TOKEN is set
	@: $(if $(value $*),,$(error $* is a required parameter!))

Help: ## Help documentation
	@ echo ""
	@ echo "+------------------------------------+"
	@ echo "|        LITTLE ORANGE HELP          |"
	@ echo "+------------------------------------+"
	@ echo ""
	@ echo "Available targets:"
	@ echo ""
	@ cat $(MAKEFILE_LIST) | grep '##' | sort | awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_\-%]+:.*?## / {printf "\033[36m%-30s\033[0m%s\n", $$1, $$2}'

# Helper function that prints variable out in format MyParameter=${MyParameter} if set, otherwise prints nothing
CloudFormationParam = $(if $(value $(1)), $(1)=$(value $(1)),)

.DEFAULT_GOAL := Help