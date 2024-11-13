VENV_PATH=env
PYTHON=$(VENV_PATH)/bin/python


env:
	python -m venv $(VENV_PATH)

install: env
	$(PYTHON) -m pip install -r requirements.txt

run: install
	$(PYTHON) ./src/app.py

