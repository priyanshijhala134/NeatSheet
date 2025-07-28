import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

def normalize_data(df, columns, method='standard'):
    report = []
    for col in columns:
        if method == 'standard':
            scaler = StandardScaler()
            df[col] = scaler.fit_transform(df[[col]])
            report.append(f"Standardized column '{col}' (mean=0, std=1)")
        elif method == 'minmax':
            scaler = MinMaxScaler()
            df[col] = scaler.fit_transform(df[[col]])
            report.append(f"Min-Max normalized column '{col}' (0-1 range)")
    return df, "\n".join(report)

def encode_categorical(df, columns, method='onehot'):
    report = []
    for col in columns:
        if method == 'onehot':
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df, dummies], axis=1)
            report.append(f"One-hot encoded '{col}' → {len(dummies.columns)} new columns")
        elif method == 'label':
            encoder = LabelEncoder()
            df[col] = encoder.fit_transform(df[col])
            report.append(f"Label encoded column '{col}'")
    return df, "\n".join(report)

def extract_datetime_features(df, column, features):
    if not pd.api.types.is_datetime64_any_dtype(df[column]):
        try:
            df[column] = pd.to_datetime(df[column])
        except:
            return df, "Conversion to datetime failed"
    
    extracted = []
    if 'year' in features:
        df[f'{column}_year'] = df[column].dt.year
        extracted.append('year')
    if 'month' in features:
        df[f'{column}_month'] = df[column].dt.month
        extracted.append('month')
    if 'day' in features:
        df[f'{column}_day'] = df[column].dt.day
        extracted.append('day')
    if 'hour' in features:
        df[f'{column}_hour'] = df[column].dt.hour
        extracted.append('hour')
    if 'weekday' in features:
        df[f'{column}_weekday'] = df[column].dt.weekday
        extracted.append('weekday')
    if 'quarter' in features:
        df[f'{column}_quarter'] = df[column].dt.quarter
        extracted.append('quarter')
    
    return df, f"Extracted features from '{column}': {', '.join(extracted)}"

def apply_custom_transformation(df, column, operation, new_column=None):
    try:
        safe_env = {'np': np, 'pd': pd}
        if new_column:
            df[new_column] = df[column].apply(lambda x: eval(operation, safe_env, {'x': x}))
            report = f"Created new column '{new_column}' = {operation}({column})"
        else:
            df[column] = df[column].apply(lambda x: eval(operation, safe_env, {'x': x}))
            report = f"Transformed '{column}' with operation: {operation}"
        return df, report
    except Exception as e:
        return df, f"Transformation failed: {str(e)}"
