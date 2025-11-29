"""
Configuration module for Student Performance Analytics AI
Handles environment variables and configuration settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Kaggle Configuration
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")
KAGGLE_DATASET = "uciml/student-alcohol-consumption"
KAGGLE_FILE = "student-mat.csv"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")  # Use gemini-2.0-flash-exp or gemini-1.5-flash

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
GOOGLE_SHEETS_SPREADSHEET_NAME = os.getenv("GOOGLE_SHEETS_SPREADSHEET_NAME", "Student_Risk_Report")

# Teacher Alert Configuration
TEACHER_EMAIL = os.getenv("TEACHER_EMAIL", "")

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

