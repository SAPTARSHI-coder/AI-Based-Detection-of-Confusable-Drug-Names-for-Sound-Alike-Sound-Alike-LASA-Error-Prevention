@echo off
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install pandas pdfplumber
python modules\01_data_preprocessing.py
