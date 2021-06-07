#
#	Makefile
#

CfnLint ?= cfn-lint

include */Makefile

Deploy: DeployPipeline SceptreCore SceptreSecurity ## 1.1 Deploy Little Orange

DockerLintCloudFormation: ## 1.2 Run LintCloudFormation target but within Docker image for cfn-lint
DockerLintCloudFormation: CfnLint=docker run --rm -v ${PWD}:/path --name cfn-lint cfn-lint:latest
DockerLintCloudFormation: LintCloudFormation

GenerateAWSProfiles: ## 1.4 Generate AWS Profile entries for accounts in AWS Organization
	@ python3 bin/generate_aws_profiles.py --profile-type SOURCE_PROFILE

GenerateECSAWSProfiles: ## 1.4 Generate AWS Profile entries in ECS format for accounts in AWS Organization
	@ python3 bin/generate_aws_profiles.py --profile-type ECS

GenerateDrawio: NeedsDrawioPath
	drawio --export --output '${DrawioPath}.png' --border 20 '${DrawioPath}.drawio'


Install: DockerBuildCfnLint InstallLib ## 1.1 Handle installing and building prerequisite libraries and images

InstallLib: ## 1.1.1 1.1.2 Install project Python libraries using pip
	pip install lib/*

Lint: LintYaml DockerLintCloudFormation ## 1.2 Run all linting

LintCloudFormation: ## 1.2 Run CloudFormation linting with cfn-lint
	$(info [+] Linting CloudFormation templates...)
	${CfnLint} '**/*.cfn.yml' '**/*.sam.yml' 'cloudformation-resource-providers/**/template.yml' 'cloudformation-resource-providers/**/resource-role.yaml'

LintYaml: ## 1.2 Run YAML linting with yamllint (see .yamllint.yml for config)
	$(info [+] Linting YAML files...)
	yamllint .

Pipenv:	## 1.6 Install Pipenv and use it to create virtual environment of Python dependencies
	$(info [+] Initialising Pipenv...)
	pip install pipenv
	PIPENV_VENV_IN_PROJECT=1 pipenv install --dev
	pipenv --venv
	pipenv run python --version

TestPython: ## 1.3 Run Python unit tests with pytest
	$(info [+] Running Python tests with pytest...)
	pipenv run pytest

#
# Utils
#

Needs%: ## 1.0 Helper target that errors if % isn't set -- i.e. check-TOKEN ensures TOKEN is set
	@: $(if $(value $*),,$(error $* is a required parameter!))

Help: ## 1.0 Help documentation
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