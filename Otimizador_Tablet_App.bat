@echo off
chcp 65001 >nul
title Otimizador de Tablets Samsung (Interface Grafica Nativa Windows)
powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File "%~dp0OtimizadorGUI.ps1"
if %ERRORLEVEL% NEQ 0 pause
