"""
Streamlit Web App for Student Performance Analytics AI
Deploy this app with: streamlit run streamlit_app.py
"""
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from kaggle_loader import fetch_kaggle_dataset, validate_data
from data_processor import process_student_data
from gemini_ai import process_batch_with_ai
from export_manager import export_to_csv, log_run_metadata
from alert_system import identify_high_risk_students, send_teacher_alert
from config import OUTPUT_DIR, LOGS_DIR

# Page configuration
st.set_page_config(
    page_title="Student Performance Analytics AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a237e;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #3949ab;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = None
if 'workflow_run' not in st.session_state:
    st.session_state.workflow_run = False

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Student Performance Analytics AI</h1>', unsafe_allow_html=True)
    st.markdown("### Real-Time Risk Prediction System")
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙ Configuration")
        
        use_ai = st.checkbox("Enable AI Analysis (Gemini)", value=True, 
                            help="Enable Gemini AI for detailed risk analysis and recommendations")
        
        sample_size = st.slider("Sample Size (for AI)", min_value=5, max_value=50, value=10,
                               help="Number of students to process with AI (to manage API quotas)")
        
        export_sheets = st.checkbox("Export to Google Sheets", value=False,
                                   help="Requires Google Sheets credentials")
        
        st.markdown("---")
        st.markdown("### 📋 Requirements")
        st.info("""
        *Required Secrets:*
        - KAGGLE_USERNAME
        - KAGGLE_KEY
        - GEMINI_API_KEY (if AI enabled)
        """)
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.caption("""
        This system predicts academic risk for students using:
        - Multi-dimensional data analysis
        - Weighted risk scoring algorithm
        - AI-powered insights (Gemini 2.5 Flash)
        - Structured recommendations
        """)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Run Workflow", "📊 Results", "📈 Analytics", "📥 Downloads"])
    
    with tab1:
        st.header("Execute Workflow")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Workflow Steps:
            1. *Fetch Data* - Download from Kaggle (UCI Student Performance dataset)
            2. *Process Data* - Compute risk scores and derived features
            3. *AI Analysis* - Generate insights with Gemini AI (if enabled)
            4. *Export Results* - Generate CSV and logs
            5. *Alerts* - Identify high-risk students
            """)
        
        with col2:
            st.metric("Dataset", "UCI Student Performance")
            st.metric("Expected Records", "~395 students")
            st.metric("Processing Time", "2-5 minutes")
        
        st.markdown("---")
        
        # Run button
        if st.button("▶ Run Complete Workflow", type="primary", use_container_width=True):
            run_workflow(use_ai, sample_size, export_sheets)
    
    with tab2:
        st.header("Workflow Results")
        
        if st.session_state.workflow_data is not None:
            display_results(st.session_state.workflow_data)
        else:
            st.info("👆 Run the workflow first to see results")
    
    with tab3:
        st.header("Data Analytics & Visualizations")
        
        if st.session_state.workflow_data is not None:
            display_analytics(st.session_state.workflow_data)
        else:
            st.info("👆 Run the workflow first to see analytics")
    
    with tab4:
        st.header("Download Results")
        display_downloads()

def run_workflow(use_ai, sample_size, export_sheets):
    """Execute the complete workflow"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Fetch data
        status_text.text("Step 1/5: Fetching data from Kaggle...")
        progress_bar.progress(10)
        
        df = fetch_kaggle_dataset()
        validate_data(df)
        
        st.success(f"✅ Loaded {len(df)} student records")
        progress_bar.progress(20)
        
        # Step 2: Process data
        status_text.text("Step 2/5: Processing data and computing risk scores...")
        progress_bar.progress(40)
        
        df = process_student_data(df)
        
        risk_dist = df['risk_level'].value_counts().to_dict()
        st.success(f"✅ Risk scores computed: {risk_dist}")
        progress_bar.progress(60)
        
        # Step 3: AI Analysis
        if use_ai:
            status_text.text(f"Step 3/5: Running AI analysis on {sample_size} students...")
            progress_bar.progress(70)
            
            # Process sample with AI
            sample_df = df.head(sample_size).copy()
            sample_df = process_batch_with_ai(sample_df)
            
            # Merge AI results back
            for col in ['ai_risk_score', 'ai_risk_level', 'key_risk_reasons', 'interventions']:
                if col in sample_df.columns:
                    df[col] = df[col].fillna(sample_df[col])
            
            # Fill missing AI data with computed scores
            df['ai_risk_score'] = df['ai_risk_score'].fillna(df['risk_score'])
            df['ai_risk_level'] = df['ai_risk_level'].fillna(df['risk_level'])
            df['key_risk_reasons'] = df['key_risk_reasons'].fillna('[]')
            df['interventions'] = df['interventions'].fillna('[]')
            
            st.success(f"✅ AI analysis complete for {sample_size} students")
        else:
            status_text.text("Step 3/5: Skipping AI analysis...")
            df['ai_risk_score'] = df['risk_score']
            df['ai_risk_level'] = df['risk_level']
            df['key_risk_reasons'] = '[]'
            df['interventions'] = '[]'
            st.info("ℹ AI analysis skipped (using computed scores)")
        
        progress_bar.progress(80)
        
        # Step 4: Export
        status_text.text("Step 4/5: Exporting results...")
        csv_path = export_to_csv(df)
        st.success(f"✅ Results exported to CSV")
        progress_bar.progress(90)
        
        # Step 5: Alerts
        status_text.text("Step 5/5: Identifying high-risk students...")
        high_risk = identify_high_risk_students(df)
        if len(high_risk) > 0:
            st.warning(f"⚠ {len(high_risk)} high-risk students detected!")
        else:
            st.info("ℹ No high-risk students")
        
        progress_bar.progress(100)
        status_text.text("✅ Workflow complete!")
        
        # Store in session state
        st.session_state.workflow_data = df
        st.session_state.workflow_run = True
        
        # Log metadata
        log_run_metadata(df)
        
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)

def display_results(df):
    """Display workflow results"""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(df))
    with col2:
        high_risk = len(df[df['risk_level'] == 'High'])
        st.metric("High Risk", high_risk, delta=None)
    with col3:
        medium_risk = len(df[df['risk_level'] == 'Medium'])
        st.metric("Medium Risk", medium_risk)
    with col4:
        low_risk = len(df[df['risk_level'] == 'Low'])
        st.metric("Low Risk", low_risk)
    
    st.markdown("---")
    
    # Risk distribution chart
    risk_counts = df['risk_level'].value_counts()
    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Risk Level Distribution",
        color_discrete_map={'High': '#c62828', 'Medium': '#f57c00', 'Low': '#2e7d32'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("Student Risk Analysis Data")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        risk_filter = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])
    with col2:
        search_term = st.text_input("Search", "")
    
    # Apply filters
    filtered_df = df.copy()
    if risk_filter != "All":
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_filter]
    if search_term:
        # Search in numeric columns
        try:
            search_val = float(search_term)
            filtered_df = filtered_df[
                (filtered_df['risk_score'] == search_val) |
                (filtered_df['final_grade'] == search_val)
            ]
        except:
            pass
    
    # Display table
    display_cols = ['attendance_pct', 'final_grade', 'trend_recent', 'risk_score', 'risk_level']
    if 'ai_risk_level' in filtered_df.columns:
        display_cols.append('ai_risk_level')
    
    st.dataframe(
        filtered_df[display_cols].head(100),
        use_container_width=True,
        height=400
    )
    
    st.caption(f"Showing {len(filtered_df)} of {len(df)} students")

def display_analytics(df):
    """Display analytics and visualizations"""
    
    # Risk score distribution
    st.subheader("Risk Score Distribution")
    fig = px.histogram(
        df,
        x='risk_score',
        nbins=30,
        title="Distribution of Risk Scores",
        labels={'risk_score': 'Risk Score', 'count': 'Number of Students'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Attendance vs Grade scatter
    st.subheader("Attendance vs Final Grade")
    fig = px.scatter(
        df,
        x='attendance_pct',
        y='final_grade',
        color='risk_level',
        size='risk_score',
        hover_data=['trend_recent'],
        title="Attendance vs Final Grade by Risk Level",
        color_discrete_map={'High': '#c62828', 'Medium': '#f57c00', 'Low': '#2e7d32'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend analysis
    st.subheader("Performance Trend Analysis")
    trend_counts = df['trend_recent'].value_counts().sort_index()
    fig = px.bar(
        x=trend_counts.index,
        y=trend_counts.values,
        title="Performance Trend Distribution",
        labels={'x': 'Trend (G3 - G2)', 'y': 'Number of Students'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Score Statistics")
        st.dataframe(df['risk_score'].describe())
    
    with col2:
        st.subheader("Grade Statistics")
        st.dataframe(df['final_grade'].describe())

def display_downloads():
    """Display download options"""
    
    st.subheader("Download Results")
    
    # List available CSV files
    csv_files = sorted(OUTPUT_DIR.glob("student_risk_report_*.csv"), reverse=True)
    
    if csv_files:
        st.success(f"Found {len(csv_files)} result files")
        
        for csv_file in csv_files[:5]:  # Show latest 5
            with open(csv_file, 'rb') as f:
                st.download_button(
                    label=f"📥 Download {csv_file.name}",
                    data=f.read(),
                    file_name=csv_file.name,
                    mime="text/csv",
                    key=f"download_{csv_file.name}"
                )
    else:
        st.info("No CSV files available. Run the workflow first.")
    
    # Download current session data
    if st.session_state.workflow_data is not None:
        st.markdown("---")
        st.subheader("Download Current Session Data")
        
        csv = st.session_state.workflow_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Current Results",
            data=csv,
            file_name=f"student_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
