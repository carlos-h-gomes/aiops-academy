@echo off
setlocal
cd /d "%~dp0"
python scripts\prepare.py
if errorlevel 1 (
  echo Preparacao nao concluida. Leia o erro acima.
  pause
  exit /b 1
)
echo Pronto. Abra iniciar.cmd para estudar.
pause
