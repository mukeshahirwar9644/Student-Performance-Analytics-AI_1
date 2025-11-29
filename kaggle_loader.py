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
logger = logging.getLogger(__name__)


def setup_kaggle_credentials():
    """Set up Kaggle API credentials"""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        kaggle_json.write_text(f'{{"username":"{KAGGLE_USERNAME}","key":"{KAGGLE_KEY}"}}')
        kaggle_json.chmod(0o600)
        logger.info("Kaggle credentials configured")
    else:
        logger.info("Kaggle credentials already exist")


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


