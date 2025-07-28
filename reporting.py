from fpdf import FPDF
import tempfile
import os

def create_quality_report(profile):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Data Quality Report", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Dataset Overview", 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Rows: {profile['shape'][0]}", 0, 1)
    pdf.cell(0, 6, f"Columns: {profile['shape'][1]}", 0, 1)
    pdf.cell(0, 6, f"Missing Values: {profile['missing_values']}", 0, 1)
    pdf.cell(0, 6, f"Duplicate Rows: {profile['duplicates']}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Data Types", 0, 1)
    for dtype, count in profile['dtypes'].items():
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"{dtype}: {count} columns", 0, 1)
    pdf.ln(5)
    
    if profile['numeric_stats']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Numeric Columns Analysis", 0, 1)
        for col, stats in profile['numeric_stats'].items():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, f"Column: {col}", 0, 1)
            pdf.set_font("Arial", '', 9)
            pdf.cell(0, 5, f"Min: {stats['min']:.2f}, Max: {stats['max']:.2f}, Mean: {stats['mean']:.2f}, Median: {stats['median']:.2f}", 0, 1)
            pdf.cell(0, 5, f"Std Dev: {stats['std']:.2f}, Skew: {stats['skew']:.2f}, Kurtosis: {stats['kurtosis']:.2f}", 0, 1)
            pdf.cell(0, 5, f"Zeros: {stats['zeros']}, Missing: {stats['missing']}", 0, 1)
            pdf.ln(3)
    
    if profile['categorical_stats']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Categorical Columns Analysis", 0, 1)
        for col, stats in profile['categorical_stats'].items():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, f"Column: {col}", 0, 1)
            pdf.set_font("Arial", '', 9)
            pdf.cell(0, 5, f"Unique Values: {stats['unique']}, Missing: {stats['missing']}", 0, 1)
            pdf.cell(0, 5, "Top Values:", 0, 1)
            for value, count in stats['top_values'].items():
                pdf.cell(20)
                pdf.cell(0, 5, f"{value}: {count}", 0, 1)
            pdf.ln(3)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name
