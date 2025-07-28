# NeatSheet
# 🧹 Data Cleaning Tool

A web-based application that allows users to clean and export datasets effortlessly. Built using **Streamlit**, this tool is designed to simplify the data preprocessing phase — one of the most time-consuming steps in any data project.

Whether you're a beginner working with messy CSVs or a professional who needs to clean data quickly without writing code, this app is made for you.

## ✨ Features

- 📤 **Upload CSV files** via drag-and-drop or file picker
- 🧼 **Clean data** by handling:
  - Missing values
  - Duplicates
  - Unnecessary columns
- 📊 **Preview cleaned data** in an interactive table
- 📥 **Export** cleaned dataset to Excel (`.xlsx`)
- 💡 User-friendly interface built with **Streamlit**

## 🚀 Live Demo

👉 Try the app here: [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)  
*(Replace with your actual deployment URL)*

## 🛠️ How to Use the App

1. Launch the web app
2. Upload a CSV file
3. Choose from data cleaning options
4. Preview the processed data
5. Export the cleaned dataset as an Excel file

## 🧰 Tech Stack

- **Frontend & Backend**: [Streamlit](https://streamlit.io/)
- **Data Handling**: Pandas, NumPy
- **Excel Export**: XlsxWriter, OpenPyXL
- **Deployment**: Streamlit Cloud
- 
## 💻 Local Setup Instructions

### ✅ Prerequisites
- Python 3.8 or higher
- Pip package manager

### 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/datacleaning-tool.git
cd datacleaning-tool

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
