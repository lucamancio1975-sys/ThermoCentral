@echo off
chcp 65001 > nul
title Service Monitor Temperatura CFR Toscana 🌡️
echo =======================================================
echo     AVVIO SERVICE MONITOR TEMPERATURA CFR TOSCANA 🌡️
echo =======================================================
echo.
echo Avvio del server Streamlit in corso...
echo.
cd /d "%~dp0"

REM Avvio con apertura automatica del browser (headless false)
call python -m streamlit run app.py --server.headless false

if %errorlevel% neq 0 (
    echo.
    echo [ATTENZIONE] Avvio via Python non riuscito. Tentativo tramite comando globale 'streamlit'...
    echo.
    call streamlit run app.py --server.headless false
)

if %errorlevel% neq 0 (
    echo.
    echo [ERRORE CRITICO] Impossibile avviare l'applicazione ThermoCentral.
    echo Assicurati che Python e le dipendenze siano installati.
    echo.
    pause
)
