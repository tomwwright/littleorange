# -------------
# 1.1 Sceptre for CloudFormation Orchestration
# -------------

SceptreCommand := sceptre --dir "./sceptre" --var-file=./sceptre/littleorange.yaml

Sceptre%: ## 1.1 Run 'sceptre launch' with PATH as %
	$(info )
	$(info [+] Sceptre launch on '$*')
	$(info )
	${SceptreCommand} launch -y $*

SceptreValidate%: ## 1.1 Run 'sceptre validate' with PATH as %
	$(info )
	$(info [+] Sceptre validate on '$*')
	$(info )
	${SceptreCommand} validate $*
