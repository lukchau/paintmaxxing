set VENV_PATH=env
set PYTHON=%VENV_PATH%\Scripts\python.exe

if not exist %VENV_PATH% (
    python -m venv %VENV_PATH%
)

%PYTHON% -m pip install -r requirements.txt

%PYTHON% src\app.py
