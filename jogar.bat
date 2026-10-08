@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto preparar
".venv\Scripts\python.exe" -c "import pygame" >nul 2>nul
if errorlevel 1 goto preparar
goto jogar
:preparar
call preparar_windows.bat --sem-pausa
if errorlevel 1 goto erro
:jogar
".venv\Scripts\python.exe" main.py %*
if errorlevel 1 goto erro
exit /b 0
:erro
echo O jogo nao abriu. Confira a mensagem acima e os arquivos da pasta logs.
if defined CI exit /b 1
if /i "%~1"=="--smoke-test" exit /b 1
pause
exit /b 1
