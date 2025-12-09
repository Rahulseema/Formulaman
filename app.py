import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import io # Used for handling in-memory file data

# --- GEMINI CLIENT INITIALIZATION (Placeholder for future use) ---

# IMPORTANT: Store your API key securely in .streamlit/secrets.toml
# [secrets]
# GEMINI_API_KEY="YOUR_API_KEY_HERE"

# Initialize the Gemini Client
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        GEMINI_AVAILABLE = True
    else:
        client = None
        GEMINI_AVAILABLE = False
except Exception:
    client = None
    GEMINI_AVAILABLE = False

# Function to generate content 
def generate_content_with_gemini(prompt):
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"
    return "Gemini client is not initialized or API key is missing."


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
        "📝 Picklist",
        "📈 Sales", 
        "📣 Marketing", 
        "💰 Financial", 
        "📦 Inventory", 
        "📑 Reporting", 
        "⚙️ Configuration"
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("v1.2.0 | E-Commerce Solutions")


# --- HELPER FUNCTION FOR FILE UPLOAD ---
@st.cache_data
def load_data(file):
    """Reads data from CSV or Excel file."""
    if file.name.endswith('.csv'):
        # Reset file pointer to beginning for reading
        file.seek(0)
        return pd.read_csv(file)
    else:
        file.seek(0)
        return pd.read_excel(file)


# 3. Main Content Logic

# --- LISTING ---
if "Listing" in menu:
    st.title("📋 Product Listings")
    st.markdown("Manage your e-commerce catalog and choose your sales channels.")
    
    # UI: Add Product & AI Generator
    with st.expander("Add New Product & Generate Description (AI)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
            st.number_input("Price ($)", min_value=0.0)
        with col2:
            st.selectbox("Category", ["Electronics", "Fashion", "Home", "Beauty"])
            stock_qty = st.number_input("Stock Quantity", min_value=0, step=1)
        
        features = st.text_area("Key Features (for AI description)", height=100)
        
        if st.button("Save Product"):
            st.success(f"Product '{product_name}' saved with {stock_qty} units.")

        if GEMINI_AVAILABLE and st.button("Generate Description using Gemini"):
            ai_prompt = (
                f"Generate a professional, concise product description for '{product_name}' "
                f"which is in the {col2.selectbox('Category', ['Electronics', 'Fashion', 'Home', 'Beauty'], key='ai_cat')}. "
                f"Key features are: {features}. Keep it under 200 words."
            )
            with st.spinner("Gemini is drafting the perfect description..."):
                generated_text = generate_content_with_gemini(ai_prompt)
            st.success("Description Generated!")
            st.code(generated_text)
        elif not GEMINI_AVAILABLE:
             st.warning("Connect your Gemini API Key in secrets.toml to enable AI features.")

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
    st.title("📝 Picklist & Mapping Utility")
    st.markdown("Upload up to **10 picklists** and one master mapping sheet to consolidate items by **Master SKU** and **Quantity**.")

    # KPI Metrics (Retained for visual)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Orders to Pick Today", "12", "-2")
    kpi2.metric("Mapping Accuracy", "99.8%", "+0.1%")
    kpi3.metric("Processed Batches", "55", "Monthly Total")

    st.subheader("1. Upload Files (CSV or Excel)")
    
    # --- File Upload Columns ---
    
    # Column for Picklists
    with st.container(border=True):
        st.subheader("📦 Picklists Upload (Up to 10 Files)")
        
        picklist_files = []
        
        # Use two columns for better layout
        cols = st.columns(2)
        for i in range(10):
            with cols[i % 2]:
                file = st.file_uploader(
                    f"Picklist File {i+1}", 
                    type=['csv', 'xlsx'], 
                    key=f"picklist_{i}"
                )
                if file:
                    picklist_files.append(file)
                    
        num_uploaded = len(picklist_files)
        st.info(f"**Total Picklist Files Uploaded: {num_uploaded}**")

    st.divider()

    # Column for Mapping Sheet
    with st.container(border=True):
        st.subheader("🗺️ Mapping Sheet Upload (Master)")
        mapping_file = st.file_uploader(
            "Mapping Sheet (Master SKU/Picklist SKU)",
            type=['csv', 'xlsx'],
            key="mapping_sheet"
        )
        st.caption("Ensure this file has columns 'Picklist SKU' and 'Master SKU'.")
        
    st.divider()

    # --- Merge Logic and Processing ---
    
    if num_uploaded > 0 and mapping_file:
        if st.button("🚀 Run Consolidation and Mapping"):
            with st.spinner("Processing files and merging SKUs..."):
                try:
                    # --- A. Read Mapping Sheet ---
                    MAP_PICK_SKU = 'Picklist SKU'
                    MASTER_SKU = 'Master SKU'
                    PICK_QTY = 'Quantity'
                    
                    mapping_df = load_data(mapping_file)
                    
                    # 1. Validate Mapping Sheet Columns
                    if MAP_PICK_SKU not in mapping_df.columns or MASTER_SKU not in mapping_df.columns:
                        st.error(f"Mapping sheet must contain columns: '{MAP_PICK_SKU}' and '{MASTER_SKU}'. Please check your header names.")
                        st.stop()
                    
                    # --- B. Process and Merge Picklists ---
                    all_picklists = []
                    for file in picklist_files:
                        df = load_data(file)
                        # 2. Validate Picklist Columns
                        if MAP_PICK_SKU not in df.columns or PICK_QTY not in df.columns:
                            st.warning(f"Skipping file {file.name}: Missing required columns '{MAP_PICK_SKU}' or '{PICK_QTY}'.")
                            continue
                        all_picklists.append(df)

                    if not all_picklists:
                        st.error("No valid picklist files found to process. Check column headers.")
                        st.stop()
                    
                    # Concatenate all valid picklists
                    merged_picklists = pd.concat(all_picklists, ignore_index=True)
                    
                    # --- C. Consolidate Quantities in Picklists ---
                    consolidated_picklists = merged_picklists.groupby([MAP_PICK_SKU])[PICK_QTY].sum().reset_index()
                    
                    # --- D. Final Merge and Aggregation ---
                    # Merge consolidated picklists with the master mapping sheet
                    final_merge = pd.merge(
                        consolidated_picklists,
                        mapping_df[[MAP_PICK_SKU, MASTER_SKU]], 
                        on=MAP_PICK_SKU,
                        how='left'
                    )
                    
                    # Aggregate by the Master SKU and sum the quantities
                    final_output = final_merge.groupby([MASTER_SKU])[PICK_QTY].sum().reset_index()
                    final_output.rename(columns={PICK_QTY: 'Total Required Quantity'}, inplace=True)

                    st.success("✅ Consolidation Complete! Final Master Picklist created.")
                    st.dataframe(final_output, use_container_width=True)

                    # --- E. Download Option ---
                    csv = final_output.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download Final Master Picklist (CSV)",
                        data=csv,
                        file_name='master_mapped_picklist_formula_man.csv',
                        mime='text/csv',
                    )

                except Exception as e:
                    st.error(f"An unexpected error occurred during processing: {e}")
                    st.info("Check if your files are properly formatted and columns are spelled correctly.")
    else:
        st.info("Please upload files above to run the consolidation utility.")

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
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
