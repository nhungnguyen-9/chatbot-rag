.PHONY: install test run deploy

install:
	pip install -r requirements.txt

test:
	python -m unittest discover tests

run:
	streamlit run frontend/main.py

deploy:
	cd infra/cdk && cdk deploy --all