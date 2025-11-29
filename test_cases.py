"""
Test Cases Module
Contains test cases for validation and demonstration
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

from data_processor import process_student_data, assign_risk_level
from gemini_ai import analyze_student_with_ai
from config import OUTPUT_DIR

def create_test_student_data():
    """Create synthetic test student data"""
    test_data = {
        'absences': [0, 5, 10, 15, 20],
        'G1': [15, 12, 10, 8, 5],
        'G2': [16, 13, 11, 9, 6],
        'G3': [17, 14, 10, 7, 4],
        'failures': [0, 0, 1, 2, 3],
        'studytime': [4, 3, 2, 1, 1]
    }
    return pd.DataFrame(test_data)


def test_case_1_low_risk_student():
    """
    Test Case 1: Low Risk Student
    - Perfect attendance (0 absences)
    - High grades (G3 = 17)
    - Positive trend (improving)
    - No missing assignments
    """
    print("\n" + "="*60)
    print("TEST CASE 1: Low Risk Student")
    print("="*60)
    
    student_data = {
        'absences': 0,
        'G1': 15,
        'G2': 16,
        'G3': 17,
        'failures': 0,
        'studytime': 4
    }
    
    df = pd.DataFrame([student_data])
    df = process_student_data(df)
    
    result = {
        'student_id': 1,
        'attendance_pct': float(df['attendance_pct'].iloc[0]),
        'final_grade': float(df['final_grade'].iloc[0]),
        'trend_recent': float(df['trend_recent'].iloc[0]),
        'missing_assignments': int(df['missing_assignments'].iloc[0]),
        'risk_score': float(df['risk_score'].iloc[0]),
        'risk_level': df['risk_level'].iloc[0]
    }
    
    print(f"Input Data: {student_data}")
    print(f"Computed Risk Score: {result['risk_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Expected: Low Risk (score < 40)")
    
    # AI Analysis
    try:
        ai_result = analyze_student_with_ai(
            result['attendance_pct'],
            result['final_grade'],
            result['trend_recent'],
            result['missing_assignments']
        )
        result['ai_analysis'] = ai_result
        print(f"\nAI Analysis:")
        print(f"  Risk Score: {ai_result.get('risk_score', 'N/A')}")
        print(f"  Risk Level: {ai_result.get('risk_level', 'N/A')}")
        print(f"  Key Reasons: {ai_result.get('key_risk_reasons', [])}")
    except Exception as e:
        print(f"\nAI Analysis Error: {str(e)}")
        result['ai_analysis'] = {"error": str(e)}
    
    return result


def test_case_2_medium_risk_student():
    """
    Test Case 2: Medium Risk Student
    - Moderate attendance (5 absences)
    - Average grades (G3 = 14)
    - Slight improvement trend
    - No failures but low study time
    """
    print("\n" + "="*60)
    print("TEST CASE 2: Medium Risk Student")
    print("="*60)
    
    student_data = {
        'absences': 5,
        'G1': 12,
        'G2': 13,
        'G3': 14,
        'failures': 0,
        'studytime': 2
    }
    
    df = pd.DataFrame([student_data])
    df = process_student_data(df)
    
    result = {
        'student_id': 2,
        'attendance_pct': float(df['attendance_pct'].iloc[0]),
        'final_grade': float(df['final_grade'].iloc[0]),
        'trend_recent': float(df['trend_recent'].iloc[0]),
        'missing_assignments': int(df['missing_assignments'].iloc[0]),
        'risk_score': float(df['risk_score'].iloc[0]),
        'risk_level': df['risk_level'].iloc[0]
    }
    
    print(f"Input Data: {student_data}")
    print(f"Computed Risk Score: {result['risk_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Expected: Medium Risk (score 40-69)")
    
    # AI Analysis
    try:
        ai_result = analyze_student_with_ai(
            result['attendance_pct'],
            result['final_grade'],
            result['trend_recent'],
            result['missing_assignments']
        )
        result['ai_analysis'] = ai_result
        print(f"\nAI Analysis:")
        print(f"  Risk Score: {ai_result.get('risk_score', 'N/A')}")
        print(f"  Risk Level: {ai_result.get('risk_level', 'N/A')}")
        print(f"  Key Reasons: {ai_result.get('key_risk_reasons', [])}")
    except Exception as e:
        print(f"\nAI Analysis Error: {str(e)}")
        result['ai_analysis'] = {"error": str(e)}
    
    return result


def test_case_3_high_risk_student():
    """
    Test Case 3: High Risk Student
    - Poor attendance (15 absences)
    - Low grades (G3 = 7)
    - Declining trend
    - Multiple failures
    """
    print("\n" + "="*60)
    print("TEST CASE 3: High Risk Student")
    print("="*60)
    
    student_data = {
        'absences': 15,
        'G1': 8,
        'G2': 9,
        'G3': 7,
        'failures': 2,
        'studytime': 1
    }
    
    df = pd.DataFrame([student_data])
    df = process_student_data(df)
    
    result = {
        'student_id': 3,
        'attendance_pct': float(df['attendance_pct'].iloc[0]),
        'final_grade': float(df['final_grade'].iloc[0]),
        'trend_recent': float(df['trend_recent'].iloc[0]),
        'missing_assignments': int(df['missing_assignments'].iloc[0]),
        'risk_score': float(df['risk_score'].iloc[0]),
        'risk_level': df['risk_level'].iloc[0]
    }
    
    print(f"Input Data: {student_data}")
    print(f"Computed Risk Score: {result['risk_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Expected: High Risk (score >= 70)")
    
    # AI Analysis
    try:
        ai_result = analyze_student_with_ai(
            result['attendance_pct'],
            result['final_grade'],
            result['trend_recent'],
            result['missing_assignments']
        )
        result['ai_analysis'] = ai_result
        print(f"\nAI Analysis:")
        print(f"  Risk Score: {ai_result.get('risk_score', 'N/A')}")
        print(f"  Risk Level: {ai_result.get('risk_level', 'N/A')}")
        print(f"  Key Reasons: {ai_result.get('key_risk_reasons', [])}")
        print(f"  Interventions: {ai_result.get('interventions', [])}")
    except Exception as e:
        print(f"\nAI Analysis Error: {str(e)}")
        result['ai_analysis'] = {"error": str(e)}
    
    return result


def test_case_4_edge_case_perfect_student():
    """
    Test Case 4: Edge Case - Perfect Student
    - Zero absences
    - Maximum grades
    - Positive trend
    - No issues
    """
    print("\n" + "="*60)
    print("TEST CASE 4: Edge Case - Perfect Student")
    print("="*60)
    
    student_data = {
        'absences': 0,
        'G1': 20,
        'G2': 20,
        'G3': 20,
        'failures': 0,
        'studytime': 4
    }
    
    df = pd.DataFrame([student_data])
    df = process_student_data(df)
    
    result = {
        'student_id': 4,
        'attendance_pct': float(df['attendance_pct'].iloc[0]),
        'final_grade': float(df['final_grade'].iloc[0]),
        'trend_recent': float(df['trend_recent'].iloc[0]),
        'missing_assignments': int(df['missing_assignments'].iloc[0]),
        'risk_score': float(df['risk_score'].iloc[0]),
        'risk_level': df['risk_level'].iloc[0]
    }
    
    print(f"Input Data: {student_data}")
    print(f"Computed Risk Score: {result['risk_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Expected: Low Risk (minimal risk score)")
    
    return result


def test_case_5_edge_case_critical_student():
    """
    Test Case 5: Edge Case - Critical Risk Student
    - Maximum absences
    - Minimum grades
    - Negative trend
    - Multiple failures
    """
    print("\n" + "="*60)
    print("TEST CASE 5: Edge Case - Critical Risk Student")
    print("="*60)
    
    student_data = {
        'absences': 20,
        'G1': 5,
        'G2': 6,
        'G3': 4,
        'failures': 3,
        'studytime': 1
    }
    
    df = pd.DataFrame([student_data])
    df = process_student_data(df)
    
    result = {
        'student_id': 5,
        'attendance_pct': float(df['attendance_pct'].iloc[0]),
        'final_grade': float(df['final_grade'].iloc[0]),
        'trend_recent': float(df['trend_recent'].iloc[0]),
        'missing_assignments': int(df['missing_assignments'].iloc[0]),
        'risk_score': float(df['risk_score'].iloc[0]),
        'risk_level': df['risk_level'].iloc[0]
    }
    
    print(f"Input Data: {student_data}")
    print(f"Computed Risk Score: {result['risk_score']:.2f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Expected: High Risk (maximum risk score)")
    
    # AI Analysis
    try:
        ai_result = analyze_student_with_ai(
            result['attendance_pct'],
            result['final_grade'],
            result['trend_recent'],
            result['missing_assignments']
        )
        result['ai_analysis'] = ai_result
        print(f"\nAI Analysis:")
        print(f"  Risk Score: {ai_result.get('risk_score', 'N/A')}")
        print(f"  Risk Level: {ai_result.get('risk_level', 'N/A')}")
        print(f"  Key Reasons: {ai_result.get('key_risk_reasons', [])}")
        print(f"  Interventions: {ai_result.get('interventions', [])}")
    except Exception as e:
        print(f"\nAI Analysis Error: {str(e)}")
        result['ai_analysis'] = {"error": str(e)}
    
    return result


def run_all_test_cases():
    """Run all test cases and save results"""
    print("\n" + "="*60)
    print("RUNNING ALL TEST CASES")
    print("="*60)
    
    results = []
    
    try:
        results.append(test_case_1_low_risk_student())
    except Exception as e:
        print(f"Test Case 1 failed: {str(e)}")
    
    try:
        results.append(test_case_2_medium_risk_student())
    except Exception as e:
        print(f"Test Case 2 failed: {str(e)}")
    
    try:
        results.append(test_case_3_high_risk_student())
    except Exception as e:
        print(f"Test Case 3 failed: {str(e)}")
    
    try:
        results.append(test_case_4_edge_case_perfect_student())
    except Exception as e:
        print(f"Test Case 4 failed: {str(e)}")
    
    try:
        results.append(test_case_5_edge_case_critical_student())
    except Exception as e:
        print(f"Test Case 5 failed: {str(e)}")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = OUTPUT_DIR / f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Test results saved to: {results_file}")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    run_all_test_cases()

