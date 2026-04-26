@echo off
REM Script para rodar a API no Windows
cd /d "C:\Users\..."

REM Ativar venv
call venv\Scripts\activate.bat

REM Entrar na pasta api
cd api

REM Rodar API
python -m uvicorn main:app --reload --port 8000

pause
