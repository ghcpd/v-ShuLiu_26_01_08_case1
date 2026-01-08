@echo off
REM One-command test runner for Windows
REM Runs the full test suite using Python's standard library

python run_tests
exit /b %errorlevel%
