# Путь к виртуальному окружению
VENV_PATH=env
PYTHON=$(VENV_PATH)/bin/python

# Создание виртуального окружения
env:
	python -m venv $(VENV_PATH)

# Установка зависимостей в виртуальном окружении
install: env
	$(PYTHON) -m pip install -r requirements.txt

# Запуск приложения с использованием интерпретатора из виртуального окружения
run: install
	$(PYTHON) ./src/app.py

