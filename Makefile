#
#	Makefile
#

pipenv:	## Install Pipenv and use it to create virtual environment of Python dependencies
	$(info [+] Initialising Pipenv...)
	pip install pipenv
	pipenv install
	pipenv run python --version

lint: lint-yaml lint-cloudformation ## Run all linting

lint-cloudformation: ## Run CloudFormation linting with cfn-lint
	$(info [+] Linting CloudFormation templates...)
	cfn-lint '**/*.cfn.yml'

lint-yaml:	## Run YAML linting with yamllint (see .yamllint.yml for config)
	$(info [+] Linting YAML files...)
	yamllint .

help: ## Help documentation
	@ echo ""
	@ echo "+------------------------------------+"
	@ echo "|        LITTLE ORANGE HELP          |"
	@ echo "+------------------------------------+"
	@ echo ""
	@ echo "Available targets:"
	@ echo ""
	@ awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-%]+:.*?## / {printf "\033[36m%-30s\033[0m \n > %s\n\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help