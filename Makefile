install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run --debug

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 page_analyzer

lint-install:
	poetry add --group dev flake8

test:
	poetry run pytest

package-reinstall:
	python3 -m pip install --user --force-reinstall dist/*.whl