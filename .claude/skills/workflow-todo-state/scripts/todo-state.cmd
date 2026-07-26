@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%todo-state.py"

if not exist "%PY_SCRIPT%" (
  echo todo-state: Python implementation not found: %PY_SCRIPT% 1>&2
  exit /b 1
)

py -3 "%PY_SCRIPT%" %*
if not errorlevel 9009 exit /b %errorlevel%

python "%PY_SCRIPT%" %*
exit /b %errorlevel%
