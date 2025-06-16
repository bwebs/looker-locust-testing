.PHONY: docs build

docs:
	typer lkr/main.py utils docs --output lkr.md

build:
	gcloud builds submit -t us-central1-docker.pkg.dev/lkr-dev-production/load-tests/lkr-load-test . 