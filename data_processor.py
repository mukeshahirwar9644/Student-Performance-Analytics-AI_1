"""
Data Processing Module
Creates derived features and computes risk components
"""
import pandas as pd
import numpy as np
import logging
from config import RISK_WEIGHTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_derived_features(df):
    """
    Compute derived features from raw student data
    
    Features:
    - attendance_pct: (1 - absences/max) * 100
    - final_grade: G3
    - trend_recent: G3 - G2
    - missing_assignments: binary (failures > 0 OR studytime <= 1)
    """
    df = df.copy()
    
    # Calculate attendance percentage
    max_absences = df['absences'].max()
    if max_absences > 0:
        df['attendance_pct'] = (1 - df['absences'] / max_absences) * 100
    else:
        df['attendance_pct'] = 100.0
    
    # Final grade (G3)
    df['final_grade'] = df['G3']
    
    # Trend (recent performance change)
    df['trend_recent'] = df['G3'] - df['G2']
    
    # Missing assignments indicator
    df['missing_assignments'] = ((df['failures'] > 0) | (df['studytime'] <= 1)).astype(int)
    
    logger.info("Derived features computed successfully")
    return df


def normalize_risk_component(value, min_val, max_val, inverse=False):
    """
    Normalize a risk component to 0-100 scale
    If inverse=True, higher values = lower risk
    """
    if max_val == min_val:
        return 50.0  # Neutral score
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    
    if inverse:
        normalized = 100 - normalized
    
    return max(0, min(100, normalized))


def compute_risk_components(df):
    """
    Compute individual risk components (0-100 scale)
    Higher score = higher risk
    """
    df = df.copy()
    
    # Attendance Risk (inverse: lower attendance = higher risk)
    max_attendance = df['attendance_pct'].max()
    min_attendance = df['attendance_pct'].min()
    df['attendance_risk'] = df['attendance_pct'].apply(
        lambda x: normalize_risk_component(x, min_attendance, max_attendance, inverse=True)
    )
    
    # Grade Risk (inverse: lower grade = higher risk)
    max_grade = df['final_grade'].max()
    min_grade = df['final_grade'].min()
    df['grade_risk'] = df['final_grade'].apply(
        lambda x: normalize_risk_component(x, min_grade, max_grade, inverse=True)
    )
    
    # Trend Risk (negative trend = higher risk)
    max_trend = df['trend_recent'].max()
    min_trend = df['trend_recent'].min()
    df['trend_risk'] = df['trend_recent'].apply(
        lambda x: normalize_risk_component(x, min_trend, max_trend, inverse=True)
    )
    
    # Missing Assignments Risk (binary, already 0 or 1, scale to 0-100)
    df['missing_assignments_risk'] = df['missing_assignments'] * 100
    
    logger.info("Risk components computed successfully")
    return df


def compute_weighted_risk_score(df):
    """
    Compute weighted risk score using component weights
    Risk Score = (attendance_risk * 0.35) + (grade_risk * 0.35) + 
                 (trend_risk * 0.20) + (missing_assignments_risk * 0.10)
    """
    df = df.copy()
    
    df['risk_score'] = (
        df['attendance_risk'] * RISK_WEIGHTS['attendance'] +
        df['grade_risk'] * RISK_WEIGHTS['grade'] +
        df['trend_risk'] * RISK_WEIGHTS['trend'] +
        df['missing_assignments_risk'] * RISK_WEIGHTS['missing_assignments']
    )
    
    logger.info("Weighted risk scores computed successfully")
    return df


def assign_risk_level(risk_score):
    """
    Assign risk level based on risk score
    0-39: Low
    40-69: Medium
    70-100: High
    """
    if risk_score <= 39:
        return "Low"
    elif risk_score <= 69:
        return "Medium"
    else:
        return "High"


def process_student_data(df):
    """
    Complete data processing pipeline
    Returns: DataFrame with all derived features and risk scores
    """
    logger.info("Starting data processing pipeline")
    
    # Compute derived features
    df = compute_derived_features(df)
    
    # Compute risk components
    df = compute_risk_components(df)
    
    # Compute weighted risk score
    df = compute_weighted_risk_score(df)
    
    # Assign risk levels
    df['risk_level'] = df['risk_score'].apply(assign_risk_level)
    
    logger.info(f"Processing complete. Risk distribution: {df['risk_level'].value_counts().to_dict()}")
    
    return df


