
# Dynamically generates BuildXYZ targets from listing the SAM project directory
SAMProjects := $(notdir $(wildcard sam/*))
SAMBuildProjects := $(addprefix Build, ${SAMProjects})

${SAMBuildProjects}: ## AWS SAM CLI build and package, e.g. BuildEnableIsOrganizationTrail
	$(info )
	$(info [+] SAM Build + Package on '$(subst Build,,$@)')
	$(info )
	cd sam/$(subst Build,,$@); \
	sam build && sam package