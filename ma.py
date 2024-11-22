import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# ---- Data Preparation ----
# Base data
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

# Derived metrics
df["TV Ad Spend"] = df["Advertising Budget"] * (df["TV Ads (%)"] / 100)
df["Digital Ad Spend"] = df["Advertising Budget"] * (df["Digital Ads (%)"] / 100)
df["Print Ad Spend"] = df["Advertising Budget"] * (df["Print Ads (%)"] / 100)
df["Other Ad Spend"] = df["Advertising Budget"] * (df["Other Ads (%)"] / 100)
df["Revenue per Ad Dollar"] = df["Revenue"] / df["Advertising Budget"]
df["Sales per Retail Outlet"] = df["Sales Volume"] / df["Retail Outlets"]
df["Revenue per Product Line"] = df["Revenue"] / df["Product Lines"]

# ---- Streamlit Dashboard ----
st.title("GreenGrow Organic Foods Marketing Mix Analysis")
st.sidebar.header("Dashboard Navigation")
page = st.sidebar.selectbox("Choose Analysis Section", ["Summary Tables", "Correlation Analysis", "Visualizations"])

# ---- Summary Tables ----
if page == "Summary Tables":
    st.header("Summary of Data")
    st.write("### Raw Data")
    st.dataframe(df)
    
    st.write("### Key Calculations")
    key_metrics = df[
        ["Quarter", "TV Ad Spend", "Digital Ad Spend", "Print Ad Spend", 
         "Other Ad Spend", "Revenue per Ad Dollar", "Sales per Retail Outlet", 
         "Revenue per Product Line"]
    ]
    st.dataframe(key_metrics)

# ---- Correlation Analysis ----
elif page == "Correlation Analysis":
    st.header("Correlation Analysis")
    corr_data = df[
        ["Advertising Budget", "Sales Volume", "Revenue", "Market Share (%)", 
         "TV Ad Spend", "Digital Ad Spend", "Revenue per Ad Dollar", 
         "Sales per Retail Outlet", "Revenue per Product Line"]
    ]
    st.write("### Correlation Matrix")
    corr_matrix = corr_data.corr()
    st.dataframe(corr_matrix)
    
    st.write("### Heatmap")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    st.pyplot(fig)

# ---- Visualizations ----
elif page == "Visualizations":
    st.header("Key Visualizations")
    # Sales Volume and Revenue Trends
    st.write("### Sales Volume and Revenue by Quarter")
    fig, ax = plt.subplots()
    ax.plot(df["Quarter"], df["Sales Volume"], label="Sales Volume", marker="o")
    ax.plot(df["Quarter"], df["Revenue"], label="Revenue", marker="o", linestyle="--")
    ax.set_ylabel("Value")
    ax.set_title("Sales and Revenue Trends")
    ax.legend()
    st.pyplot(fig)
    
    # Advertising Spend Distribution
    st.write("### Advertising Spend Breakdown by Quarter")
    ad_spend = df[["Quarter", "TV Ad Spend", "Digital Ad Spend", 
                   "Print Ad Spend", "Other Ad Spend"]]
    ad_spend.set_index("Quarter").plot(kind="bar", stacked=True, figsize=(10, 6))
    plt.title("Advertising Spend Distribution")
    plt.ylabel("Ad Spend")
    plt.xlabel("Quarter")
    st.pyplot(plt)
