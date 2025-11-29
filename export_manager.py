"""
Export Manager Module
Handles CSV export and JSON logging
"""
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path
from config import OUTPUT_DIR, LOGS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_to_csv(df, filename=None):
    """
    Export results to CSV file
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"student_risk_report_{timestamp}.csv"
    
    filepath = OUTPUT_DIR / filename
    
    # Select export columns
    export_columns = [
        'student_id', 'attendance_pct', 'final_grade', 'trend_recent',
        'missing_assignments', 'risk_score', 'risk_level',
        'ai_risk_score', 'ai_risk_level', 'key_risk_reasons', 'interventions'
    ]
    
    # Filter to available columns
    available_columns = [col for col in export_columns if col in df.columns]
    export_df = df[available_columns].copy()
    
    # Export to CSV
    export_df.to_csv(filepath, index=False)
    
    logger.info(f"Results exported to CSV: {filepath}")
    return filepath


def log_run_metadata(df, run_id=None):
    """
    Log run metadata to JSON file
    """
    if run_id is None:
        run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    metadata = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "total_students": len(df),
        "risk_distribution": df['risk_level'].value_counts().to_dict() if 'risk_level' in df.columns else {},
        "high_risk_count": len(df[df['risk_level'] == 'High']) if 'risk_level' in df.columns else 0,
        "medium_risk_count": len(df[df['risk_level'] == 'Medium']) if 'risk_level' in df.columns else 0,
        "low_risk_count": len(df[df['risk_level'] == 'Low']) if 'risk_level' in df.columns else 0,
        "average_risk_score": float(df['risk_score'].mean()) if 'risk_score' in df.columns else 0,
        "output_files": {
            "csv": f"student_risk_report_{run_id}.csv"
        }
    }
    
    log_file = LOGS_DIR / f"run_metadata_{run_id}.json"
    with open(log_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Run metadata logged to {log_file}")
    return log_file


