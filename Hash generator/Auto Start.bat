@echo off
REM Change directory to the folder where this batch file is located
cd /d "%~dp0"

REM Check if the venv folder exists in the current directory.
REM If the venv folder is not found, set up the environment using the following commands:
REM   - Create the virtual environment: python -m venv venv
REM   - Activate it: .\venv\Scripts\activate
REM   - Install dependencies: pip install -r .\requirements.txt

if not exist ".\venv\" (
    echo Error: venv folder not found.
    echo Please set up the environment using the following commands:
    echo   python -m venv venv
    echo   .\venv\Scripts\activate
    echo   pip install -r .\requirements.txt
    pause
    exit /b
)

REM Check if Hash_generator.py exists in the current directory
if not exist "Hash_generator.py" (
    echo Error: Hash_generator.py not found.
    pause
    exit /b
)

REM Activate the virtual environment
call .\venv\Scripts\activate

REM Run the Python script
python "Hash_generator.py"