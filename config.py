"""
Configuration module for Student Performance Analytics AI
Handles environment variables and configuration settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets (if running in Streamlit)
try:
    import streamlit as st
    USE_STREAMLIT_SECRETS = True
except ImportError:
    USE_STREAMLIT_SECRETS = False
    st = None

# Project paths
BASE_DIR = Path(_file_).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Helper function to get config value (checks Streamlit secrets first, then env vars)
def get_config(key, default=""):
    """Get configuration value from Streamlit secrets or environment variables"""
    if USE_STREAMLIT_SECRETS and hasattr(st, 'secrets'):
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            return os.getenv(key, default)
    return os.getenv(key, default)

# Kaggle Configuration
KAGGLE_USERNAME = get_config("KAGGLE_USERNAME", "")
KAGGLE_KEY = get_config("KAGGLE_KEY", "")
KAGGLE_DATASET = "uciml/student-alcohol-consumption"
KAGGLE_FILE = "student-mat.csv"

# Gemini API Configuration
GEMINI_API_KEY = get_config("GEMINI_API_KEY", "")
GEMINI_MODEL = get_config("GEMINI_MODEL", "gemini-2.0-flash-exp")  # Use gemini-2.0-flash-exp or gemini-1.5-flash

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH = get_config("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
GOOGLE_SHEETS_SPREADSHEET_NAME = get_config("GOOGLE_SHEETS_SPREADSHEET_NAME", "Student_Risk_Report")

# Teacher Alert Configuration
TEACHER_EMAIL = get_config("TEACHER_EMAIL", "")

# Risk Scoring Weights
RISK_WEIGHTS = {
    "attendance": 0.35,
    "grade": 0.35,
    "trend": 0.20,
    "missing_assignments": 0.10
}

# Risk Level Thresholds
RISK_THRESHOLDS = {
    "low": 39,
    "medium": 69,
    "high": 100
}
