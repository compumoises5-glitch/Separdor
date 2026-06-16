@echo off
title Sancor Web App Local
echo Iniciando sistema y verificando librerias...
pip install streamlit PyMuPDF pandas openpyxl --quiet
python -m streamlit run app.py
pause
