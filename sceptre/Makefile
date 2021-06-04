
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
