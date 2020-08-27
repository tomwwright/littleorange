#
#	Makefile
#

include devops/Makefile

lint: lint-yaml lint-cloudformation ## Run all linting

lint-cloudformation: ## Run CloudFormation linting with cfn-lint
	$(info [+] Linting CloudFormation templates...)
	cfn-lint '**/*.cfn.yml'

lint-yaml:	## Run YAML linting with yamllint (see .yamllint.yml for config)
	$(info [+] Linting YAML files...)
	yamllint .

pipenv:	## Install Pipenv and use it to create virtual environment of Python dependencies
	$(info [+] Initialising Pipenv...)
	pip install pipenv
	pipenv install
	pipenv run python --version

#
# Utils
#

help: ## Help documentation
	@ echo ""
	@ echo "+------------------------------------+"
	@ echo "|        LITTLE ORANGE HELP          |"
	@ echo "+------------------------------------+"
	@ echo ""
	@ echo "Available targets:"
	@ echo ""
	@ cat $(MAKEFILE_LIST) | grep '##' | sort | awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-%]+:.*?## / {printf "\033[36m%-30s\033[0m%s\n\n", $$1, $$2}'

# Helper function that prints variable out in format MyParameter=${MyParameter} if set, otherwise prints nothing
CloudFormationParam = $(if $(value $(1)), $(1)=$(value $(1)),)

.DEFAULT_GOAL := help