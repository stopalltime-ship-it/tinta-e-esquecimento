@echo off
setlocal
cd /d "%~dp0"
if not exist "logs" mkdir "logs"
if not exist "logs" goto erro_pasta
> "logs\preparacao.txt" echo Preparacao do ambiente Python de Tinta e Esquecimento
if exist ".venv\Scripts\python.exe" goto instalar
echo Criando o ambiente Python 3.12. Aguarde...
py -3.12 -c "import sys; raise SystemExit(sys.version_info[:2] != (3,12))" >nul 2>nul
if errorlevel 1 goto tentar_python
py -3.12 -m venv .venv >> "logs\preparacao.txt" 2>&1
if errorlevel 1 goto erro
goto instalar
:tentar_python
python -c "import sys; raise SystemExit(sys.version_info[:2] != (3,12))" >nul 2>nul
if errorlevel 1 goto falta_python
python -m venv .venv >> "logs\preparacao.txt" 2>&1
if errorlevel 1 goto erro
:instalar
".venv\Scripts\python.exe" -c "import sys; print(sys.version); raise SystemExit(sys.version_info[:2] != (3,12))" >> "logs\preparacao.txt" 2>&1
if errorlevel 1 goto versao_errada
echo Instalando ou conferindo Pygame. A primeira preparacao precisa de internet...
".venv\Scripts\python.exe" -m pip --disable-pip-version-check install --only-binary=:all: -r requirements.txt >> "logs\preparacao.txt" 2>&1
if errorlevel 1 goto erro
type "logs\preparacao.txt"
echo.
echo Pronto. Abra jogar.bat ou abra ESTA PASTA no VS Code e pressione F5.
if /i not "%~1"=="--sem-pausa" pause
exit /b 0
:falta_python
echo Python 3.12 nao foi encontrado. Instale Python 3.12 de 64 bits em python.org.
echo Inclua o Python Launcher ou marque Add Python to PATH no instalador.
echo Depois execute este arquivo novamente.
goto fim_erro
:versao_errada
echo O ambiente .venv existente usa outra versao de Python.
echo Renomeie a pasta .venv, instale Python 3.12 e execute este arquivo novamente.
goto erro
:erro
type "logs\preparacao.txt"
echo Nao foi possivel preparar o ambiente. Consulte logs\preparacao.txt.
echo Se aparecer erro de conexao, confira a internet e tente novamente.
goto fim_erro
:erro_pasta
echo Nao foi possivel escrever nesta pasta. Extraia o ZIP em uma pasta sua, como Documentos.
:fim_erro
if /i not "%~1"=="--sem-pausa" pause
exit /b 1
