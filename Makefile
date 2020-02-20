help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

FILENAME=copernic-awesome-data-store

README: README.md  ## generate a README.pdf with `pandoc`
	cp README.md $(FILENAME).md
	pandoc README.md -o $(FILENAME).pdf
	pandoc README.md -o $(FILENAME).html

database-clear:  ## Remove all data from the database
	fdbcli --exec "writemode on; clearrange \x00 \xFF;"

check: ## Run tests
	make database-clear
	PYTHONPATH=$(PWD)/copernic pytest -vvv --cov-config .coveragerc --cov-report html --cov-report xml --cov=copernic copernic
	bandit --skip=B101 copernic/ -r
	@echo "\033[95m\n\nYou may now run 'make lint'.\n\033[0m"

lint: ## Lint the code
	pylama hoply/

clean: ## Clean up
	git clean -fXd

todo: ## Things that should be done
	@grep -nR --color=always TODO .

xxx: ## Things that require attention
	@grep -nR --color=always --before-context=2  --after-context=2 XXX .

publish: check ## Publish to pypi.org
	pipenv run python setup.py sdist upload
