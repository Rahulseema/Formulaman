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
        "📝 Picklist",   # New Picklist added here
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
    st.markdown("Manage your e-commerce catalog and choose your sales channels.")
    
    # UI: Add Product
    with st.expander("Add New Product", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Product Name")
            st.number_input("Price ($)", min_value=0.0)
        with col2:
            st.selectbox("Category", ["Electronics", "Fashion", "Home", "Beauty"])
            st.number_input("Stock Quantity", min_value=0, step=1)
        st.button("Save Product")

    st.subheader("Top Indian E-commerce Channels")
    st.markdown("---")

    # Top 7 Indian E-commerce Channels in Tab Format
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Amazon India", "Flipkart", "Myntra", "Meesho", "JioMart", "Nykaa", "Ajio"
    ])

    with tab1:
        st.header("🛒 Amazon India")
        st.write("**Reach:** Largest platform, nationwide reach.")
        st.markdown("**Key for Sellers:** High volume, trusted logistics (FBA). Requires competitive pricing and detailed listings (ASIN/GTIN).")
        st.link_button("Go to Seller Portal", "https://sell.amazon.in/")

    with tab2:
        st.header("🛍️ Flipkart")
        st.write("**Reach:** Strongest in electronics, fashion, and everyday essentials. Leading Indian player.")
        st.markdown("**Key for Sellers:** Popular mega-sale events (Big Billion Days). Strong local seller support and logistics.")
        st.link_button("Go to Seller Hub", "https://seller.flipkart.com/")

    with tab3:
        st.header("👗 Myntra")
        st.write("**Reach:** Focused on Fashion, Lifestyle, and Accessories.")
        st.markdown("**Key for Sellers:** Ideal for fashion brands and exclusive collections. Curated marketplace with a style-conscious audience.")
        st.link_button("Visit Myntra Partner Site", "https://partner.myntra.com/")

    with tab4:
        st.header("🤝 Meesho")
        st.write("**Reach:** Hyper-value and social commerce model, strong in Tier 2/3 cities.")
        st.markdown("**Key for Sellers:** Zero commission model. Excellent for small businesses and resellers focusing on budget-friendly products.")
        st.link_button("Visit Meesho Supplier Panel", "https://supplier.meesho.com/")
    
    with tab5:
        st.header("🍎 JioMart")
        st.write("**Reach:** Strong presence in Groceries, Household Essentials, and rapidly expanding general merchandise.")
        st.markdown("**Key for Sellers:** Leveraging Reliance's strong retail network. Growing quickly, especially for daily essentials.")
        st.link_button("Explore JioMart Partner", "https://partner.jiomart.com/")

    with tab6:
        st.header("💄 Nykaa")
        st.write("**Reach:** Leading platform for Beauty, Skincare, and Personal Care.")
        st.markdown("**Key for Sellers:** High-spending, loyal customer base for branded and luxury beauty products. Curated selection for quality assurance.")
        st.link_button("Nykaa Seller Enquiries", "https://www.nykaa.com/contactus")

    with tab7:
        st.header("👠 Ajio")
        st.write("**Reach:** Focus on trend-led fashion and accessories, backed by Reliance Retail.")
        st.markdown("**Key for Sellers:** Appeals to style-conscious youth. Good for trendy, fresh collections and fast-moving fashion inventory.")
        st.link_button("Ajio Supplier Information", "https://www.ajio.com/s/supplier")


# --- PICKLIST ---
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
    # Interactive table using st.data_editor
    edited_data = st.data_editor(
        pick_data, 
        column_config={
            "Picked": st.column_config.CheckboxColumn(
                "Mark Picked",
                help="Check when item is secured",
                default=False,
            )
        },
        disabled=["Order ID", "Item Name", "Location", "Qty"],
        hide_index=True,
        use_container_width=True
    )

    if st.button("Complete Batch"):
        st.success("Batch status updated successfully!")


# --- SALES ---
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
    
    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", "$52,000", "+12%")
    col2.metric("Net Profit", "$14,500", "-2%")
    col3.metric("Expenses", "$37,500", "+5%")


# --- INVENTORY ---
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
