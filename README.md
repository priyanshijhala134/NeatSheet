# 🧹 NeatSheet: A Streamlit-Based Data Cleaning Tool

**NeatSheet** is a web-based data cleaning assistant designed to streamline messy datasets into clean, analysis-ready formats — all through a beautiful and interactive Streamlit interface.

Whether you're a student, analyst, or developer, NeatSheet helps you clean, transform, and export data in minutes without writing a single line of code.

## ✨ Features

- Upload CSV/Excel files (up to 200MB)
- Handle missing values with basic or KNN imputation
- Detect and remove outliers using Z-score or IQR
- Drop unwanted columns or duplicates
- Apply advanced transformations and custom logic
- Auto-profile your dataset and generate a downloadable PDF report
- Export cleaned data to CSV, Excel, and JSON

## 🧾 File Structure

| File | Description |
|------|-------------|
| `app.py` | **Main executable Streamlit app** containing UI, logic, routing, and theme customization. |
| `cleaning_functions.py` | Functions for handling missing values, outliers, and KNN imputation. |
| `transformations.py` | Feature engineering utilities: normalization, encoding, datetime features, and custom transformations. |
| `profiling.py` | Dataset profiling logic with statistics, charts (matplotlib, seaborn, plotly), and correlation heatmaps. |
| `reporting.py` | Generates PDF quality reports using FPDF for numeric and categorical summary statistics. |


## 🚀 Live Demo

👉https://neatsheet-h9kbtj7fobwuukegzhx5vv.streamlit.app/  

## 🛠️ Installation (Run Locally)

### ✅ Prerequisites

- Python 3.8+
- pip package manager

### 💻 Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/neatsheet.git
cd neatsheet

# 2. (Optional) Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
