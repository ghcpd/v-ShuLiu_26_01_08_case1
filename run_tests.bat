@echo off
python -m unittest discover -s . -p "test_*.py"
if %errorlevel% neq 0 exit /b %errorlevel%