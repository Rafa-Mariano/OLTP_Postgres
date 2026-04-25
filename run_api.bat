@echo off
REM Script para rodar a API no Windows
cd /d "C:\Users\Ana Clara\Downloads\Projeto_OLTP\OLTP_Postgres"

REM Ativar venv_novo
call venv_novo\Scripts\activate.bat

REM Entrar na pasta api
cd api

REM Rodar API
python -m uvicorn main:app --reload --port 8000

pause
