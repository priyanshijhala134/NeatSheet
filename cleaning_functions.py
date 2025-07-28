import pandas as pd
import numpy as np
from scipy import stats
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

def remove_duplicates(df):
    initial = df.shape[0]
    df = df.drop_duplicates()
    final = df.shape[0]
    return df, f"Removed {initial - final} duplicates"

def handle_missing_values(df, num_strategy='mean', cat_strategy='mode'):
    report = []
    
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            if num_strategy == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
            elif num_strategy == 'median':
                df[col].fillna(df[col].median(), inplace=True)
            report.append(f"Imputed {df[col].isnull().sum()} missing values in {col} using {num_strategy}")
    
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].mode()[0], inplace=True)
            report.append(f"Imputed {df[col].isnull().sum()} missing values in {col} using mode")
    
    return df, "\n".join(report)

def detect_outliers(df, columns, method='zscore', threshold=3):
    report = []
    cleaned_df = df.copy()
    
    for col in columns:
        if col not in df.columns or not np.issubdtype(df[col].dtype, np.number):
            continue
            
        if method == 'zscore':
            z = np.abs(stats.zscore(df[col], nan_policy='omit'))
            mask = z < threshold
        elif method == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            mask = (df[col] >= Q1 - 1.5*IQR) & (df[col] <= Q3 + 1.5*IQR)
            
        initial = len(cleaned_df)
        cleaned_df = cleaned_df[mask]
        removed = initial - len(cleaned_df)
        report.append(f"Removed {removed} outliers from {col} ({method})")
    
    return cleaned_df.dropna(), "\n".join(report)

def knn_imputation(df, n_neighbors=5):
    report = ["KNN Imputation Report:"]
    try:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns for KNN imputation")
            
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[numeric_cols])
        imputer = KNNImputer(n_neighbors=n_neighbors)
        imputed_data = imputer.fit_transform(scaled_data)
        df[numeric_cols] = scaler.inverse_transform(imputed_data)
        report.append(f"Imputed missing values in numeric columns using KNN (k={n_neighbors})")
        
        cat_cols = df.select_dtypes(exclude=np.number).columns
        for col in cat_cols:
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].mode()[0])
                report.append(f"Imputed missing values in {col} using mode")
                
        return df, "\n".join(report)
    except Exception as e:
        return df, f"KNN imputation failed: {str(e)}"
