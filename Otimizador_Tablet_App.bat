@echo off
chcp 65001 >nul
title Otimizador de Tablets Samsung (Interface Grafica Nativa Windows)
powershell.exe -NoProfile -STA -File "%~dp0OtimizadorGUI.ps1"
