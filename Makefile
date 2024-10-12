PYTHON = python
UVICORN = uvicorn
SRC_DIR = src
MAIN_MODULE = main
APP_NAME = app

.PHONY: lint lint-black lint-ruff lint-mypy lint-isort start production

lint: lint-black lint-ruff lint-mypy lint-isort

lint-black:
	$(PYTHON) -m black .

lint-ruff:
	$(PYTHON) -m ruff check . --fix

lint-mypy:
	$(PYTHON) -m mypy ./$(SRC_DIR)

lint-isort:
	$(PYTHON) -m isort .

start:
	$(UVICORN) $(SRC_DIR).$(MAIN_MODULE):$(APP_NAME) --host 0.0.0.0 --reload

production:
	$(UVICORN) $(SRC_DIR).$(MAIN_MODULE):$(APP_NAME) --workers 4