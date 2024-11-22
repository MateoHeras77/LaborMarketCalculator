import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats

# ---- Enhanced Data Preparation ----
def prepare_data():
    data = {
        "Quarter": ["Q1", "Q2", "Q3", "Q4"],
        "Product Lines": [3, 3, 4, 5],
        "Average Price ($)": [4.99, 4.99, 5.49, 5.49],
        "Retail Outlets": [500, 550, 600, 650],
        "Advertising Budget": [200, 250, 300, 350],
        "TV Ads (%)": [40, 35, 30, 25],
        "Digital Ads (%)": [30, 35, 40, 45],
        "Print Ads (%)": [20, 20, 20, 20],
        "Other Ads (%)": [10, 10, 10, 10],
        "Sales Volume": [400, 480, 580, 700],
        "Revenue": [1996, 2395, 3184, 3843],
        "Market Share (%)": [8, 9, 10, 11],
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Enhanced Derived Metrics
    df["TV Ad Spend"] = df["Advertising Budget"] * (df["TV Ads (%)"] / 100)
    df["Digital Ad Spend"] = df["Advertising Budget"] * (df["Digital Ads (%)"] / 100)
    df["Print Ad Spend"] = df["Advertising Budget"] * (df["Print Ads (%)"] / 100)
    df["Other Ad Spend"] = df["Advertising Budget"] * (df["Other Ads (%)"] / 100)
    
    # Advanced Financial Metrics
    df["Revenue per Ad Dollar"] = df["Revenue"] / df["Advertising Budget"]
    df["Sales per Retail Outlet"] = df["Sales Volume"] / df["Retail Outlets"]
    df["Revenue per Product Line"] = df["Revenue"] / df["Product Lines"]
    df["Profit Margin (%)"] = ((df["Revenue"] - df["Advertising Budget"]) / df["Revenue"]) * 100
    df["Ad Efficiency Ratio"] = df["Sales Volume"] / df["Advertising Budget"]
    
    # Cumulative and Growth Metrics
    df["Cumulative Revenue"] = df["Revenue"].cumsum()
    df["Revenue Growth (%)"] = df["Revenue"].pct_change() * 100
    df["Sales Volume Growth (%)"] = df["Sales Volume"].pct_change() * 100
    
    return df

# Statistical Analysis Functions
def perform_statistical_analysis(df):
    # Regression Analysis
    from sklearn.linear_model import LinearRegression
    X = df[['Advertising Budget']]
    y_revenue = df['Revenue']
    y_sales = df['Sales Volume']
    
    reg_revenue = LinearRegression().fit(X, y_revenue)
    reg_sales = LinearRegression().fit(X, y_sales)
    
    # Hypothesis Testing
    ad_budget_revenue_correlation = stats.pearsonr(df['Advertising Budget'], df['Revenue'])
    ad_budget_sales_correlation = stats.pearsonr(df['Advertising Budget'], df['Sales Volume'])
    
    return {
        'Revenue Regression Coefficient': reg_revenue.coef_[0],
        'Sales Volume Regression Coefficient': reg_sales.coef_[0],
        'Revenue-Ad Budget Correlation': ad_budget_revenue_correlation[0],
        'Sales-Ad Budget Correlation': ad_budget_sales_correlation[0],
        'Correlation P-Value': ad_budget_revenue_correlation[1]
    }

# Streamlit Dashboard
def main():
    st.set_page_config(page_title="Marketing Analytics Dashboard", layout="wide")
    
    # Data Preparation
    df = prepare_data()
    stats_results = perform_statistical_analysis(df)
    
    # Dashboard Title and Navigation
    st.title("🌿 GreenGrow Organic Foods: Marketing Performance Dashboard")
    
    # Sidebar Navigation
    analysis_options = [
        "Executive Summary", 
        "Performance Metrics", 
        "Statistical Insights", 
        "Advertising Analysis", 
        "Detailed Visualizations"
    ]
    selected_analysis = st.sidebar.radio("Navigate Dashboard", analysis_options)
    
    # Dynamic Content Sections
    if selected_analysis == "Executive Summary":
        st.header("📊 Quarterly Performance Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Revenue", f"${df['Revenue'].sum():,}", 
                      f"{df['Revenue Growth (%)'].iloc[-1]:.2f}% QoQ Growth")
        
        with col2:
            st.metric("Total Sales Volume", f"{df['Sales Volume'].sum():,}", 
                      f"{df['Sales Volume Growth (%)'].iloc[-1]:.2f}% QoQ Growth")
        
        with col3:
            st.metric("Ad Spend Efficiency", 
                      f"{df['Ad Efficiency Ratio'].mean():.2f} Sales/$", 
                      "Higher is Better")
    
    elif selected_analysis == "Performance Metrics":
        st.header("🔍 Detailed Performance Metrics")
        performance_metrics = df[['Quarter', 'Revenue', 'Sales Volume', 
                                  'Market Share (%)', 'Profit Margin (%)']].set_index('Quarter')
        st.dataframe(performance_metrics.style.highlight_max(axis=0))
    
    elif selected_analysis == "Statistical Insights":
        st.header("📈 Advanced Statistical Analysis")
        st.write("### Key Statistical Findings")
        for metric, value in stats_results.items():
            st.metric(metric, f"{value:.4f}")
    
    elif selected_analysis == "Advertising Analysis":
        st.header("📣 Advertising Channel Performance")
        
        # Ad Spend Breakdown
        ad_spend_breakdown = df[['Quarter', 'TV Ad Spend', 'Digital Ad Spend', 
                                 'Print Ad Spend', 'Other Ad Spend']]
        st.subheader("Advertising Spend Distribution")
        st.bar_chart(ad_spend_breakdown.set_index('Quarter'))
    
    elif selected_analysis == "Detailed Visualizations":
        st.header("🖼️ Comprehensive Visualizations")
        
        # Correlation Heatmap
        st.subheader("Performance Correlation Heatmap")
        corr_columns = ['Advertising Budget', 'Sales Volume', 'Revenue', 
                        'Market Share (%)', 'Ad Efficiency Ratio']
        corr_matrix = df[corr_columns].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt=".2f", square=True, ax=ax)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
