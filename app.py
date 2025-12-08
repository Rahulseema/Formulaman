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

# Menu Options (Updated with Picklist)
menu = st.sidebar.radio(
    "Go to:",
    [
        "📋 Listing",
        "📝 Picklist",   # <--- Added here
        "📈 Sales", 
        "📣 Marketing", 
        "💰 Financial", 
        "📦 Inventory", 
        "📑 Reporting", 
        "⚙️ Configuration"
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("v1.1.0 | E-Commerce Solutions")

# 3. Main Content Logic

# --- LISTING ---
if "Listing" in menu:
    st.title("📋 Product Listings")
    st.markdown("Manage your e-commerce catalog here.")
    
    with st.expander("Add New Product", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Product Name")
            st.number_input("Price ($)", min_value=0.0)
        with col2:
            st.selectbox("Category", ["Electronics", "Fashion", "Home", "Beauty"])
            st.number_input("Stock Quantity", min_value=0, step=1)
        st.button("Save Product")

# --- PICKLIST (NEW) ---
elif "Picklist" in menu:
    st.title("📝 Warehouse Picklist")
    st.markdown("View pending orders and mark items as picked.")

    # KPI Row for Pickers
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Orders to Pick", "12", "-2")
    kpi2.metric("Urgent Items", "5", "High Priority")
    kpi3.metric("Picker Efficiency", "94%", "+1%")

    st.divider()

    # Mock Data for Picking
    pick_data = pd.DataFrame({
        "Picked": [False, False, True, False, False],
        "Order ID": ["ORD-901", "ORD-902", "ORD-902", "ORD-903", "ORD-904"],
        "Item Name": ["Wireless Mouse", "Mech Keyboard", "USB-C Cable", "Gaming Monitor", "Laptop Stand"],
        "Location": ["Aisle 1-B", "Aisle 2-A", "Aisle 1-C", "Aisle 5-F", "Aisle 2-B"],
        "Qty": [1, 1, 2, 1, 3]
    })

    st.subheader("Current Batch")
    # This creates an interactive table where you can check boxes
    edited_data = st.data_editor(
        pick_data, 
        column_config={
            "Picked": st.column_config.CheckboxColumn(
                "Mark Picked",
                help="Check when item is secured",
                default=False,
            )
        },
        disabled=["Order ID", "Item Name", "Location", "Qty"], # Lock these columns
        hide_index=True,
        use_container_width=True
    )

    if st.button("Complete Batch"):
        st.success("Batch status updated successfully!")

# --- SALES ---
elif "Sales" in menu:
    st.title("📈 Sales Overview")
    data = pd.DataFrame({
        'Date': pd.date_range(start='1/1/2024', periods=10),
        'Revenue': [100, 150, 120, 200, 250, 220, 300, 280, 350, 400]
    })
    fig = px.line(data, x='Date', y='Revenue', title="Daily Revenue Trends")
    st.plotly_chart(fig, use_container_width=True)

# --- MARKETING ---
elif "Marketing" in menu:
    st.title("📣 Marketing Campaigns")
    st.info("No active campaigns running.")
    st.subheader("Create Campaign")
    st.text_input("Campaign Title")
    st.slider("Budget Allocation ($)", 100, 10000, 1000)
    st.button("Launch Campaign")

# --- FINANCIAL ---
elif "Financial" in menu:
    st.title("💰 Financials")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", "$52,000", "+12%")
    col2.metric("Net Profit", "$14,500", "-2%")
    col3.metric("Expenses", "$37,500", "+5%")

# --- INVENTORY ---
elif "Inventory" in menu:
    st.title("📦 Inventory Management")
    st.warning("⚠️ Low stock alert: 3 items below threshold.")
    inventory_data = pd.DataFrame({
        "Item ID": [101, 102, 103, 104],
        "Name": ["Wireless Mouse", "Keyboard", "Monitor", "HDMI Cable"],
        "Stock": [5, 120, 45, 2],
        "Status": ["Low", "Good", "Good", "Critical"]
    })
    st.dataframe(inventory_data, use_container_width=True)

# --- REPORTING ---
elif "Reporting" in menu:
    st.title("📑 Reports")
    st.write("Download your monthly performance reports.")
    st.download_button("Download CSV", data="Sample Data", file_name="report.csv")

# --- CONFIGURATION ---
elif "Configuration" in menu:
    st.title("⚙️ Configuration")
    st.toggle("Enable Dark Mode support")
    st.toggle("Receive Email Notifications")
    st.text_input("API Key")
    st.button("Save Settings")
