@echo off
set VENV_PATH=env
set PYTHON=%VENV_PATH%\Scripts\python.exe

:: Проверяем, установлен ли Python
where python >nul 2>nul
if errorlevel 1 (
    echo Python не найден в PATH. Убедитесь, что Python установлен и добавлен в PATH.
    pause
    exit /b
)

:: Создаем виртуальное окружение, если его нет
if not exist %VENV_PATH% (
    python -m venv %VENV_PATH%
)

:: Устанавливаем зависимости
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install -r requirements.txt

:: Запускаем приложение
%PYTHON% src\app.py

