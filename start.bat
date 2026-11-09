@echo off
title Nilgiris Frame - QR Photo Experience
echo ====================================================
echo Starting Nilgiris Frame (Flask + analytics + auth)...
echo ====================================================
cd /d "%~dp0"
start "" http://localhost:3001
python server.py
pause
