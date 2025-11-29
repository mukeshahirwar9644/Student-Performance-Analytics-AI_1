"""
Gemini AI Reasoning Node
Uses Gemini 2.5 Flash to generate structured risk analysis and recommendations
"""
import google.generativeai as genai
import json
import logging
import pandas as pd
import time
from config import GEMINI_API_KEY, GEMINI_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_gemini():
    """Configure Gemini API"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured")


def create_ai_prompt(attendance_pct, final_grade, trend_recent, missing_assignments):
    """
    Create structured prompt for Gemini AI
    """
    prompt = f"""You are Gemini 2.5 Flash, an expert in student performance analytics.

INPUT:
{{
 "attendance_pct": {attendance_pct},
 "final_grade": {final_grade},
 "trend_recent": {trend_recent},
 "missing_assignments": {missing_assignments}
}}

REQUIREMENTS:
- Compute risk_score 0–100
- Determine risk_level: Low/Medium/High
- Give 3 key_risk reasons
- Provide max 4 interventions (teacher+parent)
- Output strictly in JSON format

If missing input → {{"error": "missing field"}}

OUTPUT FORMAT (strict JSON):
{{
  "risk_score": <number 0-100>,
  "risk_level": "<Low|Medium|High>",
  "key_risk_reasons": [
    "<reason 1>",
    "<reason 2>",
    "<reason 3>"
  ],
  "interventions": [
    {{
      "type": "<teacher|parent>",
      "action": "<specific intervention>"
    }},
    ...
  ]
}}
"""
    return prompt


def analyze_student_with_ai(attendance_pct, final_grade, trend_recent, missing_assignments):
    """
    Analyze student using Gemini AI and return structured JSON
    """
    try:
        setup_gemini()
        
        # Validate inputs
        if any(v is None or (isinstance(v, float) and pd.isna(v)) 
               for v in [attendance_pct, final_grade, trend_recent, missing_assignments]):
            return {"error": "missing field"}
        
        # Create prompt
        prompt = create_ai_prompt(
            float(attendance_pct),
            float(final_grade),
            float(trend_recent),
            int(missing_assignments)
        )
        
        # Initialize model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        logger.info(f"AI analysis completed for student")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response text: {response_text}")
        return {"error": "JSON parsing failed", "raw_response": response_text}
        
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        return {"error": str(e)}


def process_batch_with_ai(df):
    """
    Process all students through AI analysis
    Returns: DataFrame with AI-generated insights
    """
    import pandas as pd
    
    logger.info("Starting batch AI processing")
    
    ai_results = []
    
    for idx, row in df.iterrows():
        result = analyze_student_with_ai(
            row['attendance_pct'],
            row['final_grade'],
            row['trend_recent'],
            row['missing_assignments']
        )
        
        # Merge AI results with row data
        student_result = {
            'student_id': idx,
            'ai_risk_score': result.get('risk_score', row.get('risk_score', 0)),
            'ai_risk_level': result.get('risk_level', row.get('risk_level', 'Low')),
            'key_risk_reasons': json.dumps(result.get('key_risk_reasons', [])),
            'interventions': json.dumps(result.get('interventions', []))
        }
        
        ai_results.append(student_result)
        
        # Rate limiting: Add delay to respect API quotas (free tier: ~15 requests/minute)
        # Wait 4 seconds between requests to stay under limit
        if (idx + 1) < len(df):
            time.sleep(4)
        
        # Log progress
        if (idx + 1) % 10 == 0:
            logger.info(f"Processed {idx + 1}/{len(df)} students")
    
    # Convert to DataFrame and merge
    ai_df = pd.DataFrame(ai_results)
    df = df.reset_index().merge(ai_df, left_on='index', right_on='student_id', how='left')
    
    logger.info("Batch AI processing complete")
    return df

