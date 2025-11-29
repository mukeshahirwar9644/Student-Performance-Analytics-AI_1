"""
Alert System Module
Sends alerts for high-risk students
"""
import json
import logging
from datetime import datetime
from config import TEACHER_EMAIL, LOGS_DIR, OUTPUT_DIR
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_teacher_alert(high_risk_students):
    """
    Send alert for high-risk students
    Currently logs to file, can be extended to email/SMS
    """
    if high_risk_students is None or (hasattr(high_risk_students, 'empty') and high_risk_students.empty):
        logger.info("No high-risk students to alert")
        return
    
    alert_data = {
        "timestamp": datetime.now().isoformat(),
        "alert_type": "HIGH_RISK_STUDENTS",
        "count": len(high_risk_students),
        "students": high_risk_students.to_dict('records') if hasattr(high_risk_students, 'to_dict') else high_risk_students
    }
    
    # Log alert
    alert_file = LOGS_DIR / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(alert_file, 'w') as f:
        json.dump(alert_data, f, indent=2)
    
    logger.warning(f"ALERT: {len(high_risk_students)} high-risk students detected")
    logger.info(f"Alert logged to {alert_file}")
    
    # If email is configured, send email (requires email service setup)
    if TEACHER_EMAIL:
        logger.info(f"Email alert would be sent to {TEACHER_EMAIL}")
        # TODO: Implement email sending if needed
        # send_email_alert(TEACHER_EMAIL, alert_data)


def identify_high_risk_students(df):
    """
    Identify students with High risk level
    Returns: DataFrame with high-risk students
    """
    high_risk = df[df['risk_level'] == 'High'].copy()
    return high_risk

