"""
Kaggle Data Loader Module
Fetches and processes UCI Student Performance dataset from Kaggle
"""
import os
import zipfile
import pandas as pd
from pathlib import Path
import kaggle
from config import DATA_DIR, KAGGLE_DATASET, KAGGLE_FILE, KAGGLE_USERNAME, KAGGLE_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# Patch requests library to ensure User-Agent is always set (applied at module level)
# This fixes the issue where Kaggle API receives None for User-Agent header
import requests
if not hasattr(requests.Session, '_original_prepare_headers'):
    original_prepare_headers = requests.Session.prepare_headers
    
    def patched_prepare_headers(self, headers):
        """Ensure User-Agent is always set and never None"""
        if headers is None:
            headers = {}
        # Ensure User-Agent is set and not None
        if 'User-Agent' not in headers or headers.get('User-Agent') is None:
            headers['User-Agent'] = os.environ.get('KAGGLE_USER_AGENT', 'student-performance-analytics/1.0')
        return original_prepare_headers(self, headers)
    
    requests.Session.prepare_headers = patched_prepare_headers
    logger.debug("Patched requests.Session.prepare_headers to ensure User-Agent is set")


def setup_kaggle_credentials():
    """Set up Kaggle API credentials and configure API client"""
    # Set environment variables for Kaggle API
    if KAGGLE_USERNAME:
        os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    if KAGGLE_KEY:
        os.environ['KAGGLE_KEY'] = KAGGLE_KEY
    
    # Set User-Agent to avoid header validation errors
    # The Kaggle SDK uses this environment variable if available
    if 'KAGGLE_USER_AGENT' not in os.environ:
        os.environ['KAGGLE_USER_AGENT'] = 'student-performance-analytics/1.0'
    
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists() and KAGGLE_USERNAME and KAGGLE_KEY:
        kaggle_json.write_text(f'{{"username":"{KAGGLE_USERNAME}","key":"{KAGGLE_KEY}"}}')
        kaggle_json.chmod(0o600)
        logger.info("Kaggle credentials configured")
    else:
        logger.info("Kaggle credentials already exist")
    
    # Authenticate the API client
    try:
        kaggle.api.authenticate()
        logger.info("Kaggle API authenticated successfully")
    except Exception as e:
        logger.warning(f"Kaggle API authentication warning: {str(e)}")
        # Continue anyway as credentials might be in environment


def fetch_kaggle_dataset():
    """
    Fetch dataset from Kaggle and extract CSV file
    Returns: DataFrame with student data
    """
    try:
        setup_kaggle_credentials()
        
        # Download dataset
        logger.info(f"Downloading dataset: {KAGGLE_DATASET}")
        kaggle.api.dataset_download_files(
            KAGGLE_DATASET,
            path=str(DATA_DIR),
            unzip=True
        )
        
        # Load the CSV file
        csv_path = DATA_DIR / KAGGLE_FILE
        
        if not csv_path.exists():
            # Try alternative paths
            for file in DATA_DIR.glob("*.csv"):
                if "student" in file.name.lower():
                    csv_path = file
                    break
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Could not find {KAGGLE_FILE} in {DATA_DIR}")
        
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        
        logger.info(f"Loaded {len(df)} student records")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching Kaggle dataset: {str(e)}")
        raise


def validate_data(df):
    """Validate that required columns exist in the dataset"""
    required_columns = ['absences', 'G1', 'G2', 'G3', 'failures', 'studytime']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    logger.info("Data validation passed")
    return True
