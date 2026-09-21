@echo off
title Maple Connect - QR Photo Experience
echo ====================================================
echo Starting Maple Connect Mobile Web Experience...
echo ====================================================
cd /d "%~dp0"
start "" http://localhost:3001
node server.js
pause
