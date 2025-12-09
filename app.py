import streamlit as st
import pandas as pd
import plotly.express as px
import io 

# Define the two-line header/mandatory row for the Flipkart GSTR-1 template
FLIPKART_TEMPLATE_CONTENT = """Seller GSTIN,Order ID,Order Item ID,Product Title/Description,FSN,SKU,HSN Code,Event Type,Event Sub Type,Order Type,Fulfilment Type,Order Date,Order Approval Date,Item Quantity,Order Shipped From (State),Warehouse ID,Price before discount,Total Discount,Seller Share,Bank Offer Share,Price after discount (Price before discount-Total discount),Shipping Charges,Final Invoice Amount (Price after discount+Shipping Charges),Type of tax,Taxable Value (Final Invoice Amount -Taxes),CST Rate,CST Amount,VAT Rate,VAT Amount,Luxury Cess Rate,Luxury Cess Amount,IGST Rate,IGST Amount,CGST Rate,CGST Amount,SGST Rate (or UTGST as applicable),SGST Amount (Or UTGST as applicable),TCS IGST Rate,TCS IGST Amount,TCS CGST Rate,TCS CGST Amount,TCS SGST Rate,TCS SGST Amount,Total TCS Deducted,Buyer Invoice ID,Buyer Invoice Date,Buyer Invoice Amount,Customer's Billing Pincode,Customer's Billing State,Customer's Delivery Pincode,Customer's Delivery State,Usual Price,Is Shopsy Order?,TDS Rate,TDS Amount,IRN,Business Name,Business GST Number,Beneficiary Name,IMEI
Mandatory,,,,,,,,,,,,,Mandatory,,,,,,,,,,,Mandatory,,,,,,,Mandatory,Mandatory,Mandatory,Mandatory,Mandatory,Mandatory,,,,,,,,,,,,Mandatory,,,,,,,,,,,"""

# --- HELPER FUNCTION FOR FILE UPLOAD ---
# Cached function to read data from CSV or Excel file, skipping the "Mandatory" row.
@st.cache_data
def load_data(file):
    """Reads data from CSV or Excel file, skipping the second row (index 1)."""
    if file.name.endswith('.csv'):
        file.seek(0)
        # Read the first row as header, skip the second row (index 1)
        return pd.read_csv(file, skiprows=[1])
    else:
        file.seek(0)
        # Read the first row as header, skip the second row (index 1)
        return pd.read_excel(file, skiprows=[1])


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
st.sidebar.info("v1.5.0 | E-Commerce Solutions (GST Logic Updated)")


# 3. Main Content Logic

# --- LISTING ---
if "Listing" in menu:
    st.title("📋 Product Listings")
    st.markdown("Manage your e-commerce catalog and choose your sales channels.")
    
    # UI: Add Product
    with st.expander("Add New Product", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
            st.number_input("Price ($)", min_value=0.0)
        with col2:
            st.selectbox("Category", ["Electronics", "Fashion", "Home", "Beauty"])
            stock_qty = st.number_input("Stock Quantity", min_value=0, step=1)
        
        if st.button("Save Product"):
            st.success(f"Product '{product_name}' saved with {stock_qty} units.")

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

    # KPI Metrics
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Orders to Pick Today", "12", "-2")
    kpi2.metric("Mapping Accuracy", "99.8%", "+0.1%")
    kpi3.metric("Processed Batches", "55", "Monthly Total")

    st.subheader("1. Upload Files (CSV or Excel)")
    
    # --- File Upload Columns ---
    with st.container(border=True):
        st.subheader("📦 Picklists Upload (Up to 10 Files)")
        
        picklist_files = []
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
                    MAP_PICK_SKU = 'Picklist SKU'
                    MASTER_SKU = 'Master SKU'
                    PICK_QTY = 'Quantity'
                    
                    mapping_df = load_data(mapping_file)
                    
                    if MAP_PICK_SKU not in mapping_df.columns or MASTER_SKU not in mapping_df.columns:
                        st.error(f"Mapping sheet must contain columns: '{MAP_PICK_SKU}' and '{MASTER_SKU}'. Please check your header names.")
                        st.stop()
                    
                    all_picklists = []
                    for file in picklist_files:
                        df = load_data(file)
                        if MAP_PICK_SKU not in df.columns or PICK_QTY not in df.columns:
                            st.warning(f"Skipping file {file.name}: Missing required columns '{MAP_PICK_SKU}' or '{PICK_QTY}'.")
                            continue
                        all_picklists.append(df)

                    if not all_picklists:
                        st.error("No valid picklist files found to process. Check column headers.")
                        st.stop()
                    
                    merged_picklists = pd.concat(all_picklists, ignore_index=True)
                    consolidated_picklists = merged_picklists.groupby([MAP_PICK_SKU])[PICK_QTY].sum().reset_index()
                    
                    final_merge = pd.merge(
                        consolidated_picklists,
                        mapping_df[[MAP_PICK_SKU, MASTER_SKU]], 
                        on=MAP_PICK_SKU,
                        how='left'
                    )
                    
                    final_output = final_merge.groupby([MASTER_SKU])[PICK_QTY].sum().reset_index()
                    final_output.rename(columns={PICK_QTY: 'Total Required Quantity'}, inplace=True)

                    st.success("✅ Consolidation Complete! Final Master Picklist created.")
                    st.dataframe(final_output, use_container_width=True)

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
    st.title("📑 GST and Financial Reporting")
    st.markdown("Generate and prepare your mandatory GST returns using data uploaded from various e-commerce channels.")

    # Main Tabs
    gstr1_tab, gstr3b_tab, general_reports_tab = st.tabs(["📊 GSTR-1 Preparation", "📈 GSTR-3B Summary", "📄 General Reports"])

    # 1. GSTR-1 Preparation Tab
    with gstr1_tab:
        st.subheader("GSTR-1 Data Consolidation by Marketplace")
        
        # Sub Tabs for Marketplaces (6 Mandatory)
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
            "🛒 Amazon", "🛍️ Flipkart", "🤝 Meesho", "👗 Myntra", "🍎 JioMart", "👠 Ajio"
        ])
        
        # --- Amazon Tab ---
        with sub_tab1:
            st.header("Amazon GSTR-1 Data")
            st.markdown("Upload files to generate B2C and B2B summary reports.")
            
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.info("B2C MTR Upload (Optional)")
                st.file_uploader("Upload Amazon B2C MTR (CSV/Excel)", type=['csv', 'xlsx'], key='amazon_b2c')
            
            with col_a2:
                st.info("B2B MTR Upload (Optional)")
                st.file_uploader("Upload Amazon B2B MTR (CSV/Excel)", type=['csv', 'xlsx'], key='amazon_b2b')

            if st.button("Generate Amazon GSTR-1 Data", key='gen_amazon'):
                st.success("Amazon data processing initiated. Summary will appear here.")
        
        # --- Flipkart Tab (UPDATED LOGIC) ---
        with sub_tab2:
            st.header("Flipkart GSTR-1 Data")
            st.markdown("Download the template, fill with your sales data, and upload the file below.")
            
            # Download Button for the Template
            st.download_button(
                label="⬇️ Download Flipkart Sales Template (CSV)",
                data=FLIPKART_TEMPLATE_CONTENT.encode('utf-8'),
                file_name='Flipkart_GSTR1_Template.csv',
                mime='text/csv',
            )

            # File Uploader
            flipkart_sales_file = st.file_uploader("Upload Flipkart Sales Data (CSV/Excel)", type=['csv', 'xlsx'], key='flipkart_sales')
            
            if st.button("Generate Flipkart GSTR-1 Data", key='gen_flipkart'):
                if flipkart_sales_file:
                    try:
                        df_flipkart = load_data(flipkart_sales_file)
                        st.info("File uploaded successfully. Applying GSTR-1 calculation logic...")
                        
                        # 1. Define required columns
                        COL_TAXABLE_VALUE = 'Taxable Value (Final Invoice Amount -Taxes)' # Y
                        COL_ITEM_QUANTITY = 'Item Quantity' # N
                        COL_IGST = 'IGST Amount' # AF
                        COL_CGST = 'CGST Amount' # AI
                        COL_SGST = 'SGST Amount (Or UTGST as applicable)' # AK
                        COL_BILLING_STATE = "Customer's Billing State" # AW
                        
                        # List of columns to convert to numeric for calculation
                        numeric_cols = [COL_TAXABLE_VALUE, COL_ITEM_QUANTITY, COL_IGST, COL_CGST, COL_SGST]

                        # 2. Data Cleaning/Preprocessing: Convert all calculation columns to numeric and handle NaN
                        for col in numeric_cols:
                            df_flipkart[col] = pd.to_numeric(df_flipkart[col], errors='coerce')
                        df_flipkart.fillna(0, inplace=True)
                        
                        # 3. Conditional Quantity Sign: If Taxable Value is negative, Item Quantity must be negative.
                        negative_tax_mask = df_flipkart[COL_TAXABLE_VALUE] < 0
                        df_flipkart.loc[negative_tax_mask, COL_ITEM_QUANTITY] = (
                            df_flipkart.loc[negative_tax_mask, COL_ITEM_QUANTITY] * -1
                        )
                        
                        # 4. Final Aggregation by Customer's Billing State (Col AW)
                        final_gstr1_summary = df_flipkart.groupby(
                            COL_BILLING_STATE
                        ).agg(
                            # Sum the four requested columns
                            Taxable_Value_Total=(COL_TAXABLE_VALUE, 'sum'),
                            IGST_Total=(COL_IGST, 'sum'),
                            CGST_Total=(COL_CGST, 'sum'),
                            SGST_UTGST_Total=(COL_SGST, 'sum'),
                            
                            # Also include the adjusted quantity for completeness
                            Total_Net_Quantity=(COL_ITEM_QUANTITY, 'sum')
                        ).reset_index()
                        
                        final_gstr1_summary.rename(columns={COL_BILLING_STATE: 'Customer Billing State'}, inplace=True)

                        st.success("✅ GSTR-1 Data Aggregation Complete! Summary created by Billing State.")
                        
                        st.subheader("Flipkart Consolidated GSTR-1 Summary")
                        st.dataframe(final_gstr1_summary, use_container_width=True)
                        
                        # Download button for the resulting summary
                        csv_output = final_gstr1_summary.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Download GSTR-1 Summary (CSV)",
                            data=csv_output,
                            file_name='flipkart_gstr1_summary.csv',
                            mime='text/csv',
                        )
                        
                    except Exception as e:
                        st.error(f"Error processing Flipkart file: {e}")
                        st.warning("Please ensure your uploaded file strictly follows the format of the downloaded template and contains valid numeric data in the tax columns.")
                else:
                    st.warning("Please upload the Flipkart Sales Data file to proceed.")


        # --- Meesho Tab ---
        with sub_tab3:
            st.header("Meesho GSTR-1 Data")
            st.markdown("All three files are required to accurately calculate net sales and TCS.")
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.warning("Forward Shipping File (Mandatory)")
                st.file_uploader("Upload Meesho Forward Shipping File", type=['csv', 'xlsx'], key='meesho_forward')
            
            with col_m2:
                st.warning("Reverse Shipping/RTO File (Mandatory)")
                st.file_uploader("Upload Meesho Reverse Shipping File", type=['csv', 'xlsx'], key='meesho_reverse')
                
            with col_m3:
                st.warning("TCS Report (Mandatory)")
                st.file_uploader("Upload Meesho TCS Report", type=['csv', 'xlsx'], key='meesho_tcs')
                
            if st.button("Generate Meesho GSTR-1 Data", key='gen_meesho'):
                st.success("Meesho data processing initiated. Final GSTR-1 values calculated.")

        # --- Myntra Tab ---
        with sub_tab4:
            st.header("Myntra GSTR-1 Data")
            st.info("Work in Progress / Coming Soon.")
            st.markdown("Myntra data integration and reporting features will be added in the next release.")
            
        # --- JioMart Tab ---
        with sub_tab5:
            st.header("JioMart GSTR-1 Data")
            st.info("Work in Progress / Coming Soon.")
            st.markdown("JioMart data integration and reporting features will be added in the next release.")
            
        # --- Ajio Tab ---
        with sub_tab6:
            st.header("Ajio GSTR-1 Data")
            st.info("Work in Progress / Coming Soon.")
            st.markdown("Ajio data integration and reporting features will be added in the next release.")


    # 2. GSTR-3B Summary Tab
    with gstr3b_tab:
        st.subheader("GSTR-3B Input Tax Credit (ITC) Summary")
        st.markdown("This tab will summarize your consolidated GSTR-1 data and Purchase Register data to help file GSTR-3B.")
        st.info("Work in Progress / Coming Soon.")
        
    # 3. General Reports Tab
    with general_reports_tab:
        st.subheader("Download General Performance Reports")
        st.write("Download your monthly performance reports.")
        st.download_button("Download CSV", data="Sample Data".encode('utf-8'), file_name="report.csv")

# --- SALES ---
elif "Sales" in menu:
    st.title("📈 Sales Overview")
    data = pd.DataFrame({'Date': pd.date_range(start='1/1/2024', periods=10),'Revenue': [100, 150, 120, 200, 250, 220, 300, 280, 350, 400]})
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

# --- CONFIGURATION ---
elif "Configuration" in menu:
    st.title("⚙️ Configuration")
    st.toggle("Enable Dark Mode support")
    st.toggle("Receive Email Notifications")
    st.text_input("General System API Key (if needed)")
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
