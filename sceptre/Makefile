
Sceptre%: ## Run 'sceptre launch' with PATH as %
	$(info )
	$(info [+] Sceptre launch on '$*')
	$(info )
	sceptre --dir sceptre launch $*

SceptreInstallResolvers: ## Install Sceptre Custom Resolvers
	pip install sceptre/resolvers/*
	
SceptreValidate%: ## Run 'sceptre validate' with PATH as %
	$(info )
	$(info [+] Sceptre validate on '$*')
	$(info )
	sceptre --dir sceptre validate $*

SAMProjects := $(notdir $(wildcard sceptre/templates/SAM/*))
SAMBuildProjects := $(addprefix Build, ${SAMProjects})

${SAMBuildProjects}: ## AWS SAM CLI build and package, e.g. BuildEnableIsOrganizationTrail
	$(info )
	$(info [+] SAM Build + Package on '$(subst Build,,$@)')
	$(info )
	cd sceptre/templates/SAM/$(subst Build,,$@); \
	sam build; \
	sam package