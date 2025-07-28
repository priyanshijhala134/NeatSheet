import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import io  # For Excel export

def generate_data_profile(df):
    profile = {}
    profile['shape'] = df.shape
    profile['missing_values'] = df.isnull().sum().sum()
    profile['duplicates'] = df.duplicated().sum()
    profile['dtypes'] = df.dtypes.value_counts().to_dict()
    
    numeric_cols = df.select_dtypes(include=np.number).columns
    numeric_stats = {}
    for col in numeric_cols:
        numeric_stats[col] = {
            'min': df[col].min(),
            'max': df[col].max(),
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'skew': df[col].skew(),
            'kurtosis': df[col].kurtosis(),
            'zeros': (df[col] == 0).sum(),
            'missing': df[col].isnull().sum()
        }
    profile['numeric_stats'] = numeric_stats
    
    cat_cols = df.select_dtypes(include='object').columns
    cat_stats = {}
    for col in cat_cols:
        cat_stats[col] = {
            'unique': df[col].nunique(),
            'top_values': df[col].value_counts().head(5).to_dict(),
            'missing': df[col].isnull().sum()
        }
    profile['categorical_stats'] = cat_stats
    
    return profile

def visualize_column(df, col_selected, profile):
    if pd.api.types.is_numeric_dtype(df[col_selected]):
        tab1, tab2, tab3 = st.tabs(["Histogram", "Box Plot", "Distribution"])
        with tab1:
            fig, ax = plt.subplots()
            sns.histplot(df[col_selected], kde=True, ax=ax)
            ax.set_title(f'Distribution of {col_selected}')
            st.pyplot(fig)
        with tab2:
            fig, ax = plt.subplots()
            sns.boxplot(x=df[col_selected], ax=ax)
            ax.set_title(f'Box Plot of {col_selected}')
            st.pyplot(fig)
        with tab3:
            fig = px.violin(df, y=col_selected, box=True, points="all")
            st.plotly_chart(fig, use_container_width=True)
        
        stats = profile['numeric_stats'].get(col_selected, {})
        if stats:
            st.markdown(f'<div class="profile-card"><h4>{col_selected} Statistics</h4>'
                       f'<p>Min: {stats.get("min", "N/A"):.2f}</p>'
                       f'<p>Max: {stats.get("max", "N/A"):.2f}</p>'
                       f'<p>Mean: {stats.get("mean", "N/A"):.2f}</p>'
                       f'<p>Std Dev: {stats.get("std", "N/A"):.2f}</p>'
                       f'<p>Missing: {stats.get("missing", "N/A")}</p></div>', 
                       unsafe_allow_html=True)
    else:
        tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
        value_counts = df[col_selected].value_counts().head(10)
        with tab1:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=value_counts.values, y=value_counts.index, ax=ax, palette="viridis")
            ax.set_title(f'Top Values in {col_selected}')
            st.pyplot(fig)
        with tab2:
            fig = px.pie(names=value_counts.index, values=value_counts.values, 
                         title=f'Value Distribution for {col_selected}')
            st.plotly_chart(fig, use_container_width=True)
        
        stats = profile['categorical_stats'].get(col_selected, {})
        if stats:
            st.markdown(f'<div class="profile-card"><h4>{col_selected} Statistics</h4>'
                       f'<p>Unique Values: {stats.get("unique", "N/A")}</p>'
                       f'<p>Missing: {stats.get("missing", "N/A")}</p>'
                       f'<p>Top Value: {list(stats.get("top_values", {}).keys())[0] if stats.get("top_values") else "N/A"}</p></div>', 
                       unsafe_allow_html=True)

def show_correlation(df):
    numeric_cols = df.select_dtypes(include=np.number).columns
    if len(numeric_cols) > 1:
        st.subheader("Correlation Matrix")
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)
