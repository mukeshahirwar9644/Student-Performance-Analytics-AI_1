"""
Main Workflow - Student Performance Analytics AI
Orchestrates the complete pipeline from data fetch to output
"""
import logging
import json
from datetime import datetime
from pathlib import Path

from kaggle_loader import fetch_kaggle_dataset, validate_data
from data_processor import process_student_data
from gemini_ai import process_batch_with_ai
from google_sheets import write_results_to_sheets
from export_manager import export_to_csv, log_run_metadata
from alert_system import identify_high_risk_students, send_teacher_alert
from config import OUTPUT_DIR, LOGS_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_complete_workflow(use_ai=True, export_sheets=True):
    """
    Execute the complete student analytics workflow
    
    Args:
        use_ai: Whether to use Gemini AI for analysis (default: True)
        export_sheets: Whether to export to Google Sheets (default: True)
    
    Returns:
        dict: Summary of the workflow execution
    """
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    logger.info(f"Starting workflow run: {run_id}")
    
    try:
        # Step 1: Fetch data from Kaggle
        logger.info("Step 1: Fetching data from Kaggle")
        df = fetch_kaggle_dataset()
        validate_data(df)
        
        # Step 2: Process data and compute risk scores
        logger.info("Step 2: Processing data and computing risk scores")
        df = process_student_data(df)
        
        # Step 3: AI Analysis (optional but recommended)
        if use_ai:
            logger.info("Step 3: Running AI analysis with Gemini")
            df = process_batch_with_ai(df)
        else:
            logger.info("Step 3: Skipping AI analysis")
            # Use computed risk scores as AI scores
            df['ai_risk_score'] = df['risk_score']
            df['ai_risk_level'] = df['risk_level']
            df['key_risk_reasons'] = json.dumps([])
            df['interventions'] = json.dumps([])
        
        # Step 4: Export to CSV
        logger.info("Step 4: Exporting to CSV")
        csv_path = export_to_csv(df, f"student_risk_report_{run_id}.csv")
        
        # Step 5: Export to Google Sheets
        if export_sheets:
            logger.info("Step 5: Exporting to Google Sheets")
            try:
                sheet_url = write_results_to_sheets(df)
                logger.info(f"Google Sheets URL: {sheet_url}")
            except Exception as e:
                logger.warning(f"Google Sheets export failed: {str(e)}")
                sheet_url = None
        else:
            sheet_url = None
        
        # Step 6: Identify and alert high-risk students
        logger.info("Step 6: Identifying high-risk students")
        high_risk_students = identify_high_risk_students(df)
        send_teacher_alert(high_risk_students)
        
        # Step 7: Log run metadata
        logger.info("Step 7: Logging run metadata")
        metadata_file = log_run_metadata(df, run_id)
        
        # Summary
        summary = {
            "run_id": run_id,
            "status": "success",
            "total_students": len(df),
            "high_risk_count": len(high_risk_students),
            "medium_risk_count": len(df[df['risk_level'] == 'Medium']),
            "low_risk_count": len(df[df['risk_level'] == 'Low']),
            "output_files": {
                "csv": str(csv_path),
                "metadata": str(metadata_file),
                "google_sheets": sheet_url
            }
        }
        
        logger.info(f"Workflow completed successfully: {summary}")
        return summary
        
    except Exception as e:
        logger.error(f"Workflow failed: {str(e)}", exc_info=True)
        return {
            "run_id": run_id,
            "status": "failed",
            "error": str(e)
        }


if __name__ == "__main__":
    # Run the complete workflow
    summary = run_complete_workflow(use_ai=True, export_sheets=True)
    print(json.dumps(summary, indent=2))


