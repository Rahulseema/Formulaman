import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Formula Man",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sidebar Navigation
st.sidebar.title("Formula Man 🏎️")
st.sidebar.markdown("---")

# Menu Options with Icons
menu = st.sidebar.radio(
    "Go to:",
    [
        "📋 Listing", 
        "📈 Sales", 
        "📣 Marketing", 
        "💰 Financial", 
        "📦 Inventory", 
        "📑 Reporting", 
        "⚙️ Configuration"
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("v1.0.0 | E-Commerce Solutions")

# 3. Main Content Logic
if "Listing" in menu:
    st.title("📋 Product Listings")
    st.markdown("Manage your e-commerce catalog here.")
    
    # Example UI: Add Product
    with st.expander("Add New Product", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Product Name")
            st.number_input("Price ($)", min_value=0.0)
        with col2:
            st.selectbox("Category", ["Electronics", "Fashion", "Home", "Beauty"])
            st.number_input("Stock Quantity", min_value=0, step=1)
        st.button("Save Product")

elif "Sales" in menu:
    st.title("📈 Sales Overview")
    
    # Mock Data for Visualization
    data = pd.DataFrame({
        'Date': pd.date_range(start='1/1/2024', periods=10),
        'Revenue': [100, 150, 120, 200, 250, 220, 300, 280, 350, 400]
    })
    
    # Plotly Chart
    fig = px.line(data, x='Date', y='Revenue', title="Daily Revenue Trends")
    st.plotly_chart(fig, use_container_width=True)

elif "Marketing" in menu:
    st.title("📣 Marketing Campaigns")
    st.info("No active campaigns running.")
    
    st.subheader("Create Campaign")
    st.text_input("Campaign Title")
    st.slider("Budget Allocation ($)", 100, 10000, 1000)
    st.button("Launch Campaign")

elif "Financial" in menu:
    st.title("💰 Financials")
    
    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", "$52,000", "+12%")
    col2.metric("Net Profit", "$14,500", "-2%")
    col3.metric("Expenses", "$37,500", "+5%")

elif "Inventory" in menu:
    st.title("📦 Inventory Management")
    st.warning("⚠️ Low stock alert: 3 items below threshold.")
    
    # Mock Inventory Table
    inventory_data = pd.DataFrame({
        "Item ID": [101, 102, 103, 104],
        "Name": ["Wireless Mouse", "Keyboard", "Monitor", "HDMI Cable"],
        "Stock": [5, 120, 45, 2],
        "Status": ["Low", "Good", "Good", "Critical"]
    })
    st.dataframe(inventory_data, use_container_width=True)

elif "Reporting" in menu:
    st.title("📑 Reports")
    st.write("Download your monthly performance reports.")
    st.download_button("Download CSV", data="Sample Data", file_name="report.csv")

elif "Configuration" in menu:
    st.title("⚙️ Configuration")
    st.toggle("Enable Dark Mode support")
    st.toggle("Receive Email Notifications")
    st.text_input("API Key")
    st.button("Save Settings")
