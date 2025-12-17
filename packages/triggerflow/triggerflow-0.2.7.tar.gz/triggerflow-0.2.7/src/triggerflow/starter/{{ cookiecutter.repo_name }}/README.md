# {{ cookiecutter.project_name }}

- conda env create --file=environment.yml
- conda activate {{ cookiecutter.project_name }}

## Data versioning
When a dataset changes one can do (TODO: add this to pipeline to compare the hash):
- dvc add data/01_raw/companies.csv
- git add data/01_raw/companies.csv.dvc
- git commit -m "Track dataset changes with DVC"

## Run CI local
- brew install gitlab-ci-local
- gitlab-ci-local --list
- gitlab-ci-local

## ToDos:
- move functionality of uhh_mlatl1 to pipeline
- if case in base dataloader for classification or not
- add model evaluation steps
- automation of dvc in CI pipeline
- move {{ cookiecutter.project_name }} meta data json to dvc
- add linting and type checking
- write tests
- write out reporting / logging / plots etc.
- track plots with dvc?
- cross check pipeline afterwards with {{ cookiecutter.project_name }} team
- make starter pipeline as template
- add {{ cookiecutter.project_name }} model
