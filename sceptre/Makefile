
SceptreCommand := sceptre --dir "./sceptre" --var-file=./sceptre/littleorange.yaml

Sceptre%: ## Run 'sceptre launch' with PATH as %
	$(info )
	$(info [+] Sceptre launch on '$*')
	$(info )
	${SceptreCommand} launch -y $*

SceptreValidate%: ## Run 'sceptre validate' with PATH as %
	$(info )
	$(info [+] Sceptre validate on '$*')
	$(info )
	${SceptreCommand} validate $*

# Dynamically generates BuildXYZ targets from listing the SAM project directory
SAMProjects := $(notdir $(wildcard sceptre/templates/SAM/*))
SAMBuildProjects := $(addprefix Build, ${SAMProjects})

${SAMBuildProjects}: ## AWS SAM CLI build and package, e.g. BuildEnableIsOrganizationTrail
	$(info )
	$(info [+] SAM Build + Package on '$(subst Build,,$@)')
	$(info )
	cd sceptre/templates/SAM/$(subst Build,,$@); \
	sam build && sam package