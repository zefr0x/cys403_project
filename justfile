project_name := "cys403_project"

alias t := test
alias r := run

_default:
	@just --list

run:
	python -m {{ project_name }}

test:
	pytest -v tests/

lint_all:
	pre-commit run --all-files

compile_dep:
	pre-commit run pip-compile --all-files

sync_dep:
	uv pip sync requirements/requirements.txt requirements/requirements-dev.txt

todo:
	rg ".(TODO|FIXME|FIX|HACK|WARN|PREF|NOTE): " --glob !{{ file_name(justfile()) }}
