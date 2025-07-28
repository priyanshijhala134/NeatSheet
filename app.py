import streamlit as st
import pandas as pd
import numpy as np
import tempfile
import os
import io
import base64
import json
from datetime import datetime
import traceback
import sys

# Import modular components
from cleaning_functions import *
from transformations import *
from profiling import *
from reporting import *

# Enhanced error handling decorator
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
            with st.expander("Technical Details", expanded=False):
                st.code(traceback.format_exc())
            return None
    return wrapper

# Page configuration
st.set_page_config(
    page_title="NeatSheet - Data Cleaning Tool",
    page_icon="🧼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/neatsheet',
        'Report a bug': "https://github.com/yourusername/neatsheet/issues",
        'About': "### NeatSheet v1.0\nA comprehensive data cleaning tool!"
    }
)

# Theme customization options
THEMES = {
    "Light": {"bg": "#f0f2f6", "card": "#ffffff", "text": "#333333", "accent": "#4CAF50"},
    # "Dark": {"bg": "#0e1117", "card": "#1e2130", "text": "#f0f2f6", "accent": "#28a745"},
    "Ocean": {"bg": "#d4f1f9", "card": "#75e6da", "text": "#05445e", "accent": "#189AB4"},
    "Forest": {"bg": "#d4f3d0", "card": "#a7d7c5", "text": "#1e3d32", "accent": "#2E8B57"}
}

# Progress tracking class
class CleaningProgress:
    def __init__(self):
        self.steps = {
            "Upload": False,
            "Duplicates": False,
            "Missing Values": False,
            "Outliers": False,
            "Transformations": False,
            "Profiling": False
        }
        self.current_step = "Upload"
    
    def complete_step(self, step_name):
        if step_name in self.steps:
            self.steps[step_name] = True
            self.current_step = step_name
    
    def get_progress(self):
        completed = sum(self.steps.values())
        total = len(self.steps)
        return completed, total, self.current_step

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'progress' not in st.session_state:
    st.session_state.progress = CleaningProgress()
if 'theme' not in st.session_state:
    st.session_state.theme = "Light"
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Home"  
if 'cleaning_steps' not in st.session_state:
    st.session_state.cleaning_steps = []
if 'version' not in st.session_state:
    st.session_state.version = "1.0"

# Apply selected theme
def apply_theme(theme_name):
    theme = THEMES[theme_name]
    custom_css = f"""
        <style>
        :root {{
            --primary: {theme['accent']};
            --bg: #fdf0f3;   /* light pink */
            --card: #ffffff; /* white */
            --text: #000000;
        }}

        section.main > div.block-container {{
            background: linear-gradient(135deg, var(--bg), var(--card)) !important;
            padding: 2rem;
            border-radius: 10px;
        }}

        body, html {{
            background-color: var(--bg) !important;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }}
        
        .sidebar .sidebar-content {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--text);
            box-shadow: 5px 0 15px rgba(0, 0, 0, 0.1);
        }}
        
        .stButton>button {{
            background: var(--primary);
            color: white;
            border-radius: 12px;
            border: none;
            padding: 10px 20px;
            font-weight: 600;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}
        
        .stButton>button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 7px 14px rgba(0, 0, 0, 0.2);
            opacity: 0.9;
        }}
        
        .stDownloadButton>button {{
            background: var(--primary);
            border-radius: 12px;
            transition: all 0.3s ease;
        }}
        
        .profile-card {{
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .profile-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }}
        
        .profile-card h4 {{
            margin-top: 0;
            color: var(--text);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 12px;
            font-weight: 600;
        }}
        
        .report-section {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 16px;
            margin-top: 20px;
            backdrop-filter: blur(5px);
        }}
        
        .stExpander {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
        }}
        
        .step-indicator {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            gap: 8px;
        }}
        
        .step {{
            flex: 1;
            text-align: center;
            padding: 15px 5px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .step.active {{
            background: var(--primary);
            color: white;
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }}
        
        .step.completed {{
            background: #2E7D32;
            color: white;
        }}
        
        .tooltip-icon {{
            cursor: help;
            margin-left: 5px;
            font-size: 0.8em;
            color: #6c757d;
        }}
        
        .footer {{
            position: fixed;
            bottom: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            text-align: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            z-index: 100;
        }}
        
        h1, h2, h3, h4 {{
            color: var(--primary);
            font-weight: 700;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }}
        
        .stTextInput>div>div>input, .stSelectbox>div>div>select {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            color: var(--text);
            padding: 10px 15px;
        }}
        
        .stDataFrame {{
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }}
        
        .header-glow {{
            text-shadow: 0 0 10px var(--primary);
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.8s ease-in;
        }}
        
        @keyframes fadeIn {{
            0% {{ opacity: 0; transform: translateY(20px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .glass-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }}
        
        .feature-icon {{
            font-size: 2.5rem;
            margin-bottom: 15px;
            color: var(--primary);
        }}
        
        .feature-card {{
            transition: all 0.4s ease;
        }}
        
        .feature-card:hover {{
            transform: translateY(-10px) rotate(2deg);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Apply theme on every run
apply_theme(st.session_state.theme)

# ===== PAGE DEFINITIONS =====
@handle_errors
def home_page():
    st.markdown("<h1>🧹 <span class='header-glow'>Welcome to NeatSheet</span></h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='fade-in'>
        <p style='font-size: 1.2rem;'>NeatSheet is an intelligent data cleaning tool that transforms messy datasets 
        into analysis-ready assets in minutes. Experience the future of data preparation!</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", 
             caption="Data Cleaning Dashboard", use_container_width=True)
    
    
    with st.expander("✨ Features Showcase", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='feature-card glass-card'>
                <div class='feature-icon'>🧹</div>
                <h3>Cleaning Tools</h3>
                <ul>
                    <li>Remove duplicates</li>
                    <li>Handle missing values</li>
                    <li>Detect and remove outliers</li>
                    <li>Fix data types</li>
                    <li>Advanced KNN imputation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='feature-card glass-card'>
                <div class='feature-icon'>🔄</div>
                <h3>Transformations</h3>
                <ul>
                    <li>Normalization/scaling</li>
                    <li>Categorical encoding</li>
                    <li>DateTime feature extraction</li>
                    <li>Custom transformations</li>
                    <li>Dimensionality reduction</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class='feature-card glass-card'>
                <div class='feature-icon'>📊</div>
                <h3>Profiling & Export</h3>
                <ul>
                    <li>Interactive visualizations</li>
                    <li>Statistical summaries</li>
                    <li>Correlation analysis</li>
                    <li>PDF quality reports</li>
                    <li>Multiple export formats</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    

@handle_errors
def cleaning_page():
    st.markdown("<h1>🧹 <span class='header-glow'>Data Cleaning Tools</span></h1>", unsafe_allow_html=True)
    
    # Progress tracker
    completed, total, current = st.session_state.progress.get_progress()
    st.subheader(f"Cleaning Progress: {completed}/{total} steps completed")
    
    # Step indicators
    steps = ["Upload", "Duplicates", "Missing Values", "Outliers", "Transformations", "Profiling"]
    step_html = '<div class="step-indicator">'
    for step in steps:
        status = ""
        if step == current:
            status = "active pulse"
        elif st.session_state.progress.steps.get(step, False):
            status = "completed"
        step_html += f'<div class="step {status}">{step}</div>'
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)
    
    # File upload in sidebar
    with st.sidebar:
        st.header("1. Upload Data")
        uploaded_file = st.file_uploader("Choose CSV/Excel", type=["csv", "xlsx"], 
                                         help="Supports files up to 200MB")
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.df = df.copy()
                st.session_state.progress.complete_step("Upload")
                st.success("Data uploaded successfully!")
                st.session_state.cleaning_steps.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "step": f"Uploaded file: {uploaded_file.name} ({df.shape[0]} rows, {df.shape[1]} columns)"
                })
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                with st.expander("Technical Details", expanded=False):
                    st.code(traceback.format_exc())
    
    if st.session_state.df is None:
        st.warning("Please upload a file to begin cleaning")
        return
    
    df = st.session_state.df
    
    # Display initial stats
    st.subheader("Original Data")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Preview")
        st.dataframe(df.head(3))
    with col2:
        st.markdown("""
        <div class='glass-card'>
            <h4>Dataset Summary</h4>
            <p>Rows: {}</p>
            <p>Columns: {}</p>
            <h4>Missing Values</h4>
            {}
        </div>
        """.format(df.shape[0], df.shape[1], df.isnull().sum().rename('Count').to_frame().to_html()), 
        unsafe_allow_html=True)
    
    # Cleaning operations
    st.markdown("---")
    st.subheader("Cleaning Operations")
    
    # Record cleaning steps
    def record_step(step_description):
        st.session_state.cleaning_steps.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "step": step_description
        })
        st.success(step_description)
    
    # 1. Remove duplicates
    with st.expander("➗ Remove Duplicates", expanded=False):
        st.info("Removes identical rows from your dataset. Only the first occurrence is kept.")
        if st.button("Remove Duplicates", key="remove_dup"):
            df, dup_report = remove_duplicates(df)
            st.session_state.df = df
            st.session_state.progress.complete_step("Duplicates")
            record_step(dup_report)
    
    # 2. Drop Columns
    with st.expander("🗑️ Remove Columns", expanded=False):
        st.info("Select columns to permanently remove from your dataset.")
        cols_to_drop = st.multiselect("Select columns to remove", df.columns)
        if st.button("Remove Selected Columns", key="remove_cols") and cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            st.session_state.df = df
            record_step(f"Removed columns: {', '.join(cols_to_drop)}")
    
    # # 3. Handle Missing Values
    # with st.expander("❓ Missing Value Handling", expanded=False):
    #     st.info("Fill missing values using different strategies for numerical and categorical columns.")
    #     num_strategy = st.radio("Numerical columns strategy: ", ["mean", "median"], horizontal=True)
    #     cat_strategy = st.radio("Categorical columns strategy: ", ["mode", "drop"], horizontal=True)
    #     if st.button("Apply Imputation", key="impute"):
    #         df, missing_report = handle_missing_values(df, num_strategy, cat_strategy)
    #         st.session_state.df = df
    #         st.session_state.progress.complete_step("Missing Values")
    #         record_step(missing_report)
    
    # 4. Fix data types
    with st.expander("📅 Data Type Conversion", expanded=False):
        st.info("Convert columns to appropriate data types like datetime or numeric.")
        date_col = st.selectbox("Convert column to datetime", df.columns)
        if st.button("Convert to Datetime", key="convert_dt") and date_col:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                st.session_state.df = df
                record_step(f"Converted {date_col} to datetime")
            except Exception as e:
                st.error(f"Conversion failed: {str(e)}")
    
    # 5. Outlier Detection
    with st.expander("📊 Outlier Detection", expanded=False):
        st.info("Identify and remove statistical outliers using Z-score or IQR methods.")
        outlier_method = st.radio("Select method:", ['zscore', 'iqr'], horizontal=True)
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        selected_cols = st.multiselect("Select columns for outlier detection:", num_cols)
        if outlier_method == 'zscore':
            threshold = st.slider("Z-score threshold", 2.0, 5.0, 3.0)
        else:
            threshold = None
        if st.button("Detect and Remove Outliers", key="outliers") and selected_cols:
            df, outlier_report = detect_outliers(df, selected_cols, outlier_method, threshold)
            st.session_state.df = df
            st.session_state.progress.complete_step("Outliers")
            record_step(outlier_report)
    
    # 6. KNN Imputation
    with st.expander("🎯 Advanced Missing Value Handling", expanded=False):
        st.info("Use machine learning (KNN algorithm) to impute missing values based on similar rows.")
        imp_strategy = st.radio("Choose imputation method:", ['simple', 'knn'], horizontal=True)
        if imp_strategy == 'knn':
            knn_neighbors = st.slider("Number of KNN neighbors", 2, 10, 5)
            if st.button("Apply KNN Imputation", key="knn"):
                df, knn_report = knn_imputation(df, knn_neighbors)
                st.session_state.df = df
                record_step(knn_report)
        else:
            num_strategy = st.radio("Numerical strategy:", ["mean", "median"], horizontal=True)
            cat_strategy = st.radio("Categorical strategy:", ["mode", "drop"], horizontal=True)
            if st.button("Apply Basic Imputation", key="basic_impute"):
                df, missing_report = handle_missing_values(df, num_strategy, cat_strategy)
                st.session_state.df = df
                record_step(missing_report)
    
    # 7. Advanced Transformations
    with st.expander("✨ Advanced Transformations", expanded=False):
        st.info("Apply advanced data transformations and feature engineering techniques.")
        
        # Normalization
        st.markdown("**📏 Normalization/Scaling**")
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        norm_cols = st.multiselect("Select columns to normalize:", num_cols)
        norm_method = st.radio("Method:", ['standard', 'minmax'], horizontal=True)
        if st.button("Apply Normalization", key="normalize") and norm_cols:
            df, norm_report = normalize_data(df, norm_cols, norm_method)
            st.session_state.df = df
            st.session_state.progress.complete_step("Transformations")
            record_step(norm_report)
        
        # Encoding
        st.markdown("**🔤 Categorical Encoding**")
        cat_cols = df.select_dtypes(include='object').columns.tolist()
        encode_cols = st.multiselect("Select columns to encode:", cat_cols)
        encode_method = st.radio("Encoding method:", ['onehot', 'label'], horizontal=True)
        if st.button("Apply Encoding", key="encode") and encode_cols:
            df, encode_report = encode_categorical(df, encode_cols, encode_method)
            st.session_state.df = df
            record_step(encode_report)
        
        # DateTime Features
        st.markdown("**📅 DateTime Feature Extraction**")
        date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        if not date_cols:
            date_cols = df.select_dtypes(include='object').columns.tolist()
        date_col = st.selectbox("Select datetime column:", date_cols)
        features = st.multiselect("Select features to extract:", 
                                 ['year', 'month', 'day', 'hour', 'weekday', 'quarter'])
        if st.button("Extract Features", key="dt_features") and date_col and features:
            df, date_report = extract_datetime_features(df, date_col, features)
            st.session_state.df = df
            record_step(date_report)
        
        # Custom Transformations
        st.markdown("**🛠️ Custom Transformations**")
        transform_col = st.selectbox("Select column to transform:", df.columns)
        operation = st.text_input("Operation (Python expression using 'x'):", "x * 2")
        new_col = st.text_input("New column name (optional):")
        if st.button("Apply Custom Transformation", key="custom_transform"):
            df, custom_report = apply_custom_transformation(df, transform_col, operation, new_col)
            st.session_state.df = df
            record_step(custom_report)
    
    # Show cleaned data
    st.markdown("---")
    st.subheader("Cleaned Data Preview")
    st.dataframe(df.head(5))
    
    # Cleaning history
    with st.expander("📝 Cleaning History", expanded=False):
        if st.session_state.cleaning_steps:
            for step in st.session_state.cleaning_steps:
                st.markdown(f"<div class='glass-card'>⏱️ {step['timestamp']} - {step['step']}</div>", 
                           unsafe_allow_html=True)
            if st.button("Clear History", key="clear_history"):
                st.session_state.cleaning_steps = []
                st.rerun()
        else:
            st.info("No cleaning steps recorded yet")

@handle_errors
def profiling_page():
    # FIX: Use markdown for title instead of st.title
    st.markdown("<h1>📊 <span class='header-glow'>Data Profiling & Visualization</span></h1>", unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("Please upload a file and clean your data first")
        return
    
    df = st.session_state.df
    
    # Generate data profile
    with st.spinner("Generating data profile..."):
        profile = generate_data_profile(df)
    
    # Profile summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="profile-card"><h4>Dataset Shape</h4>'
                    f'<p>Rows: {profile["shape"][0]}</p>'
                    f'<p>Columns: {profile["shape"][1]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="profile-card"><h4>Missing Values</h4>'
                    f'<p>Total: {profile["missing_values"]}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="profile-card"><h4>Duplicate Rows</h4>'
                    f'<p>Total: {profile["duplicates"]}</p></div>', unsafe_allow_html=True)
    with col4:
        dtype_info = "<br>".join([f"{k}: {v}" for k, v in profile["dtypes"].items()])
        st.markdown(f'<div class="profile-card"><h4>Data Types</h4>'
                    f'<p>{dtype_info}</p></div>', unsafe_allow_html=True)
    
    # Column visualization
    st.subheader("Column Visualization")
    col_selected = st.selectbox("Select a column for visualization", df.columns)
    if col_selected:
        visualize_column(df, col_selected, profile)
    
    # Correlation matrix
    st.subheader("Correlation Analysis")
    show_correlation(df)
    
    # Data Quality Report
    st.markdown("---")
    st.subheader("📝 Data Quality Report")
    st.info("Generate a comprehensive PDF report of your data quality with detailed statistics.")
    if st.button("Generate PDF Report", key="pdf_report"):
        with st.spinner("Generating report..."):
            try:
                report_path = create_quality_report(profile)
                with open(report_path, "rb") as f:
                    pdf_bytes = f.read()
                st.session_state.progress.complete_step("Profiling")
                st.success("Report generated successfully!")
                st.download_button(
                    label="Download Data Quality Report (PDF)",
                    data=pdf_bytes,
                    file_name="data_quality_report.pdf",
                    mime="application/pdf"
                )
                os.unlink(report_path)
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
                with st.expander("Technical Details", expanded=False):
                    st.code(traceback.format_exc())

@handle_errors
def export_page():
    # FIX: Use markdown for title instead of st.title
    st.markdown("<h1>💾 <span class='header-glow'>Export Data</span></h1>", unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("No data to export. Please upload and clean your data first.")
        return
    
    df = st.session_state.df
    
    # Export formats
    st.subheader("Export Cleaned Data")
    st.info("Download your cleaned dataset in various formats for further analysis.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='glass-card feature-card'>
            <h3>CSV Format</h3>
            <p>Comma-separated values, suitable for most applications</p>
        </div>
        """, unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='cleaned_data.csv',
            mime='text/csv'
        )
    
    with col2:
        st.markdown("""
        <div class='glass-card feature-card'>
            <h3>Excel Format</h3>
            <p>Microsoft Excel format with multiple sheets support</p>
        </div>
        """, unsafe_allow_html=True)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Cleaned Data')
        excel_bytes = excel_buffer.getvalue()
        st.download_button(
            label="Download Excel",
            data=excel_bytes,
            file_name='cleaned_data.xlsx',
            mime='application/vnd.ms-excel'
        )
    
    with col3:
        st.markdown("""
        <div class='glass-card feature-card'>
            <h3>JSON Format</h3>
            <p>JavaScript Object Notation, ideal for web applications</p>
        </div>
        """, unsafe_allow_html=True)
        json_str = df.to_json(orient='records', indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name='cleaned_data.json',
            mime='application/json'
        )
    
    # Export cleaning history
    st.markdown("---")
    st.subheader("Export Cleaning History")
    st.info("Download a record of all cleaning steps performed for documentation.")
    
    if st.session_state.cleaning_steps:
        history_df = pd.DataFrame(st.session_state.cleaning_steps)
        history_csv = history_df.to_csv(index=False).encode('utf-8')
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download History (CSV)",
                data=history_csv,
                file_name='cleaning_history.csv',
                mime='text/csv'
            )
        with col2:
            st.download_button(
                label="Download History (JSON)",
                data=history_df.to_json(orient='records', indent=2),
                file_name='cleaning_history.json',
                mime='application/json'
            )
        
        st.dataframe(history_df)
    else:
        st.info("No cleaning steps recorded yet")

# ===== DOCUMENTATION PAGE =====
@handle_errors
def documentation_page():
    # FIX: Use markdown for title instead of st.title
    st.markdown("<h1>📚 <span class='header-glow'>NeatSheet Documentation</span></h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card fade-in'>
        <h2>Comprehensive Guide to Using NeatSheet</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Table of Contents", expanded=True):
        st.markdown("""
        <div class='glass-card'>
            <ul>
                <li><a href='#getting-started'>Getting Started</a></li>
                <li><a href='#data-cleaning-tools'>Data Cleaning Tools</a></li>
                <li><a href='#transformations'>Transformations</a></li>
                <li><a href='#data-profiling'>Data Profiling</a></li>
                <li><a href='#export-options'>Export Options</a></li>
                <li><a href='#deployment'>Deployment</a></li>
                <li><a href='#troubleshooting'>Troubleshooting</a></li>
                <li><a href='#faq'>FAQ</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class='glass-card'>
        <h3 id='getting-started'>1. Getting Started</h3>
        <p><strong>NeatSheet</strong> is designed to make data cleaning accessible to everyone:</p>
        <ul>
            <li>Upload CSV or Excel files</li>
            <li>Navigate through the cleaning workflow</li>
            <li>Export your cleaned data</li>
        </ul>
        
        <h4>System Requirements:</h4>
        <ul>
            <li>Modern web browser (Chrome, Firefox, Edge)</li>
            <li>Python 3.8+ (for local execution)</li>
            <li>4GB+ RAM recommended for large datasets</li>
        </ul>
        
        <h4>First Steps:</h4>
        <ol>
            <li>Upload your dataset using the sidebar</li>
            <li>Use the Data Cleaning page to prepare your data</li>
            <li>Explore your data using the Profiling page</li>
            <li>Export your cleaned data in your preferred format</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # ... rest of documentation page remains similar with glass-card elements ...

# ===== SIDEBAR NAVIGATION =====
with st.sidebar:
    st.title("NeatSheet")
    st.caption(f"Version {st.session_state.version}")
    
    st.header("Navigation")
    page_options = {
        "🏠 Home": home_page,
        "🧹 Data Cleaning": cleaning_page,
        "📊 Data Profiling": profiling_page,
        "💾 Export Data": export_page,
        "📚 Documentation": documentation_page
    }
    selected_page = st.selectbox("Go to", list(page_options.keys()), 
                               index=list(page_options.keys()).index(st.session_state.page))
    
    st.session_state.page = selected_page
    
    st.markdown("---")
    st.header("Settings")
    
    # Theme selector
    new_theme = st.selectbox("Color Theme", list(THEMES.keys()), 
                           index=list(THEMES.keys()).index(st.session_state.theme))
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        # Theme will be applied in the next run via the top-level apply_theme call
    
    # Progress tracker
    st.markdown("---")
    st.header("Progress")
    completed, total, current = st.session_state.progress.get_progress()
    st.progress(completed/total if total > 0 else 0)
    st.caption(f"{completed}/{total} steps completed")
    st.caption(f"Current step: {current}")
    
    # Reset button
    if st.button("🔄 Reset Session"):
        st.session_state.clear()
        st.session_state.progress = CleaningProgress()
        st.session_state.theme = "Light"
        st.session_state.page = "🏠 Home"
        st.rerun()
    
    

# ===== MAIN APP RENDERING =====
page_options[selected_page]()

