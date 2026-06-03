@echo off
cd /d "%~dp0"
echo Starting Expense Tracker at http://127.0.0.1:8000/
echo.
".\.venv\Scripts\python.exe" manage.py migrate
if errorlevel 1 goto failed
echo.
".\.venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
goto end

:failed
echo.
echo Startup failed. Leave this window open and share the message above.

:end
pause
