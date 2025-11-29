"""
Google Sheets Integration Module
Writes student risk analysis results to Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import logging
from config import GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_SPREADSHEET_NAME
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_google_sheets():
    """
    Set up Google Sheets API client
    Returns: gspread client
    """
    creds_path = Path(GOOGLE_SHEETS_CREDENTIALS_PATH)
    
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google Sheets credentials not found at {creds_path}. "
            "Please download credentials.json from Google Cloud Console."
        )
    
    # Define the scope
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Authenticate
    creds = Credentials.from_service_account_file(
        str(creds_path),
        scopes=scope
    )
    
    client = gspread.authorize(creds)
    logger.info("Google Sheets API authenticated")
    
    return client


def create_or_get_spreadsheet(client, spreadsheet_name):
    """
    Create a new spreadsheet or get existing one
    Returns: gspread Spreadsheet object
    """
    try:
        # Try to open existing spreadsheet
        spreadsheet = client.open(spreadsheet_name)
        logger.info(f"Opened existing spreadsheet: {spreadsheet_name}")
    except gspread.SpreadsheetNotFound:
        # Create new spreadsheet
        spreadsheet = client.create(spreadsheet_name)
        logger.info(f"Created new spreadsheet: {spreadsheet_name}")
    
    return spreadsheet


def write_results_to_sheets(df, spreadsheet_name=None):
    """
    Write student risk analysis results to Google Sheets
    """
    try:
        client = setup_google_sheets()
        
        sheet_name = spreadsheet_name or GOOGLE_SHEETS_SPREADSHEET_NAME
        spreadsheet = create_or_get_spreadsheet(client, sheet_name)
        
        # Select or create worksheet
        try:
            worksheet = spreadsheet.worksheet("Risk_Report")
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="Risk_Report", rows=1000, cols=20)
        
        # Prepare data for export
        export_columns = [
            'student_id', 'attendance_pct', 'final_grade', 'trend_recent',
            'missing_assignments', 'risk_score', 'risk_level',
            'ai_risk_score', 'ai_risk_level', 'key_risk_reasons', 'interventions'
        ]
        
        # Filter to available columns
        available_columns = [col for col in export_columns if col in df.columns]
        export_df = df[available_columns].copy()
        
        # Convert JSON strings to readable format
        if 'key_risk_reasons' in export_df.columns:
            export_df['key_risk_reasons'] = export_df['key_risk_reasons'].apply(
                lambda x: '; '.join(eval(x)) if isinstance(x, str) else ''
            )
        
        if 'interventions' in export_df.columns:
            export_df['interventions'] = export_df['interventions'].apply(
                lambda x: format_interventions(x) if isinstance(x, str) else ''
            )
        
        # Clear existing data
        worksheet.clear()
        
        # Write headers
        headers = list(export_df.columns)
        worksheet.append_row(headers)
        
        # Write data
        values = export_df.values.tolist()
        if values:
            worksheet.append_rows(values)
        
        logger.info(f"Successfully wrote {len(export_df)} student records to Google Sheets")
        
        # Make spreadsheet publicly viewable (optional)
        try:
            spreadsheet.share('', perm_type='anyone', role='reader')
        except:
            pass
        
        return spreadsheet.url
        
    except Exception as e:
        logger.error(f"Error writing to Google Sheets: {str(e)}")
        raise


def format_interventions(interventions_json_str):
    """Format interventions JSON string to readable text"""
    try:
        import json
        interventions = json.loads(interventions_json_str)
        formatted = []
        for interv in interventions:
            formatted.append(f"{interv.get('type', 'Unknown')}: {interv.get('action', '')}")
        return ' | '.join(formatted)
    except:
        return interventions_json_str


