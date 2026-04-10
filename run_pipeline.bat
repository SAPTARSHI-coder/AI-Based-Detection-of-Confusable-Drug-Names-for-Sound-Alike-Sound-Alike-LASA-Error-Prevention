@echo off
setlocal

echo ============================================================
echo  LASA Drug Detector — Full Pipeline Setup
echo ============================================================

:: Step 0: venv
if not exist venv (
    echo [1/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/5] Virtual environment already exists.
)

call venv\Scripts\activate.bat

:: Step 1: dependencies
echo [2/5] Installing dependencies...
pip install --quiet pdfplumber pandas numpy rapidfuzz jellyfish scikit-learn xgboost joblib fastapi uvicorn python-multipart jinja2 matplotlib seaborn tqdm

:: Step 2: data preprocessing
echo [3/5] Running data preprocessing (PDF extraction + negative sampling)...
python modules\01_data_preprocessing.py
if errorlevel 1 ( echo ERROR in data preprocessing & pause & exit /b 1 )

:: Step 3: feature engineering
echo [4/5] Running feature engineering...
python modules\02_feature_engineering.py
if errorlevel 1 ( echo ERROR in feature engineering & pause & exit /b 1 )

:: Step 4: model training
echo [5/5] Training ML model...
python modules\03_model_training.py
if errorlevel 1 ( echo ERROR in model training & pause & exit /b 1 )

echo.
echo ============================================================
echo  Pipeline complete! Starting web server on http://localhost:8000
echo  Press Ctrl+C to stop.
echo ============================================================
echo.
cd app
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
