import streamlit as st
import pandas as pd
import plotly.express as px
import io
import time

# ==========================================
# 1. CONFIG & STYLING (MUST BE FIRST)
# ==========================================
st.set_page_config(
    page_title="Formula Man Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "BEAUTIFICATION" ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Change Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }

    /* Custom Header Style */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A; /* Dark Blue */
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }

    /* Card Styling for Metrics */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Button Styling */
    div.stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION LOGIC (GATEKEEPER)
# ==========================================

# Initialize Session State for Auth
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Function to check password
def check_password():
    if st.session_state["username_input"] == "Rahul" and st.session_state["password_input"] == "Sparsh@2030":
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False
        st.error("❌ Invalid User ID or Password")

# If NOT authenticated, show Login Screen and STOP execution of the rest of the app
if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center;'>🏎️ Formula Man</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Login Required</h3>", unsafe_allow_html=True)
            
            st.text_input("User ID", key="username_input")
            st.text_input("Password", type="password", key="password_input")
            
            if st.button("Login", on_click=check_password, use_container_width=True):
                # The logic is handled in the on_click callback
                pass
                
    st.stop() # 🛑 THIS STOPS THE REST OF THE CODE FROM LOADING IF NOT LOGGED IN


# ==========================================
# 3. CONSTANTS & TEMPLATES (LOADS AFTER LOGIN)
# ==========================================
COL_GSTIN = 'Seller GSTIN'
COL_TAXABLE_VALUE = 'Taxable Value (Final Invoice Amount -Taxes)' 
COL_ITEM_QUANTITY = 'Item Quantity' 
COL_IGST = 'IGST Amount' 
COL_CGST = 'CGST Amount' 
COL_SGST = 'SGST Amount (Or UTGST as applicable)' 
COL_BILLING_STATE = "Customer's Billing State" 

FLIPKART_TEMPLATE_CONTENT = """Seller GSTIN,Order ID,Order Item ID,Product Title/Description,FSN,SKU,HSN Code,Event Type,Event Sub Type,Order Type,Fulfilment Type,Order Date,Order Approval Date,Item Quantity,Order Shipped From (State),Warehouse ID,Price before discount,Total Discount,Seller Share,Bank Offer Share,Price after discount (Price before discount-Total discount),Shipping Charges,Final Invoice Amount (Price after discount+Shipping Charges),Type of tax,Taxable Value (Final Invoice Amount -Taxes),CST Rate,CST Amount,VAT Rate,VAT Amount,Luxury Cess Rate,Luxury Cess Amount,IGST Rate,IGST Amount,CGST Rate,CGST Amount,SGST Rate (or UTGST as applicable),SGST Amount (Or UTGST as applicable),TCS IGST Rate,TCS IGST Amount,TCS CGST Rate,TCS CGST Amount,TCS SGST Rate,TCS SGST Amount,Total TCS Deducted,Buyer Invoice ID,Buyer Invoice Date,Buyer Invoice Amount,Customer's Billing Pincode,Customer's Billing State,Customer's Delivery Pincode,Customer's Delivery State,Usual Price,Is Shopsy Order?,TDS Rate,TDS Amount,IRN,Business Name,Business GST Number,Beneficiary Name,IMEI
Mandatory,,,,,,,,,,,,,Mandatory,,,,,,,,,,,Mandatory,,,,,,,Mandatory,Mandatory,Mandatory,Mandatory,Mandatory,Mandatory,,,,,,,,,,,,Mandatory,,,,,,,,,,,"""

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
@st.cache_data
def load_data(file):
    if file.name.endswith('.csv'):
        file.seek(0)
        return pd.read_csv(file, skiprows=[1])
    else:
        file.seek(0)
        return pd.read_excel(file, skiprows=[1])

@st.cache_data(show_spinner="Processing Flipkart sales data...")
def process_flipkart_data(df_raw):
    df = df_raw.copy()
    numeric_cols = [COL_TAXABLE_VALUE, COL_ITEM_QUANTITY, COL_IGST, COL_CGST, COL_SGST]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.fillna(0, inplace=True)
    
    negative_tax_mask = df[COL_TAXABLE_VALUE] < 0
    df.loc[negative_tax_mask, COL_ITEM_QUANTITY] = (
        df.loc[negative_tax_mask, COL_ITEM_QUANTITY].abs() * -1
    )

    df['Clean_Billing_State_Upper'] = df[COL_BILLING_STATE].astype(str).str.strip().str.upper()
    df['State_Group'] = df['Clean_Billing_State_Upper'].str[:4]
    
    state_mapping_df = df[df['Clean_Billing_State_Upper'] != 'NAN'].groupby('State_Group').agg(
        Representative_State_Name=(COL_BILLING_STATE, lambda x: str(x.iloc[0]).strip()[:5])
    ).reset_index()

    state_name_map = state_mapping_df.set_index('State_Group')['Representative_State_Name'].to_dict()
    return df, state_name_map

@st.cache_data(show_spinner="Processing Meesho GSTR-1 data...")
def process_meesho_data(tcs_sales_file, tcs_sales_return_file):
    COL_M_QTY = 'quantity'
    COL_M_TAX_VALUE = 'total_taxable_sale_value'
    COL_M_TAX_AMOUNT = 'tax_amount'
    COL_M_STATE = 'end_customer_state_new'
    COLS_TO_PROCESS = [COL_M_QTY, COL_M_TAX_VALUE, COL_M_TAX_AMOUNT]
    
    df_sales = load_data(tcs_sales_file)
    df_returns = load_data(tcs_sales_return_file)

    missing_cols_sales = [col for col in COLS_TO_PROCESS + [COL_M_STATE] if col not in df_sales.columns]
    missing_cols_returns = [col for col in COLS_TO_PROCESS + [COL_M_STATE] if col not in df_returns.columns]
    
    if missing_cols_sales or missing_cols_returns:
        raise KeyError(f"Missing columns.")

    for col in COLS_TO_PROCESS:
        df_sales[col] = pd.to_numeric(df_sales[col], errors='coerce').fillna(0)
    
    for col in COLS_TO_PROCESS:
        df_returns[col] = pd.to_numeric(df_returns[col], errors='coerce').fillna(0)
        df_returns[col] = df_returns[col] * -1
    
    df_merged = pd.concat([df_sales, df_returns], ignore_index=True)
    df_merged['State_Clean'] = df_merged[COL_M_STATE].astype(str).str.strip().str.upper()
    
    df_merged['IGST'] = 0.0
    df_merged['CGST'] = 0.0
    df_merged['SGST'] = 0.0
    
    haryana_mask = df_merged['State_Clean'] == 'HARYANA'
    df_merged.loc[haryana_mask, 'CGST'] = df_merged[COL_M_TAX_AMOUNT] / 2
    df_merged.loc[haryana_mask, 'SGST'] = df_merged[COL_M_TAX_AMOUNT] / 2
    
    other_states_mask = df_merged['State_Clean'] != 'HARYANA'
    df_merged.loc[other_states_mask, 'IGST'] = df_merged[COL_M_TAX_AMOUNT]
    
    final_summary = df_merged.groupby(COL_M_STATE, dropna=True).agg(
        Total_Qty=(COL_M_QTY, 'sum'),
        Taxable_Value=(COL_M_TAX_VALUE, 'sum'),
        IGST=('IGST', 'sum'),
        CGST=('CGST', 'sum'),
        SGST=('SGST', 'sum')
    ).reset_index()
    
    final_summary.rename(columns={
        COL_M_STATE: 'End State',
        'Total_Qty': 'Total Qty',
        'Taxable_Value': 'Taxable Value'
    }, inplace=True)
    
    final_summary = final_summary[['End State', 'Total Qty', 'Taxable Value', 'IGST', 'CGST', 'SGST']]
    
    for col in ['Taxable Value', 'IGST', 'CGST', 'SGST']:
        final_summary[col] = final_summary[col].round(2)
    
    return final_summary

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🏎️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Formula Man</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Navigate:",
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
    
    st.markdown("---")
    with st.container(border=True):
        st.caption("**System Status**")
        st.success("● Online")
        st.caption(f"Logged in as: {st.session_state['username_input']}")
        
        # Logout Button
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

# ==========================================
# 6. MAIN CONTENT LOGIC
# ==========================================

# --- LISTING ---
if "Listing" in menu:
    st.markdown('<div class="main-header">Product Listings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage your e-commerce catalog and choose your sales channels.</div>', unsafe_allow_html=True)
    
    # UI: Add Product Card
    with st.container(border=True):
        st.subheader("➕ Add New Product")
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
            st.number_input("Price ($)", min_value=0.0)
        with col2:
            st.selectbox("Category", ["Electronics", "Fashion", "Home", "Beauty"])
            stock_qty = st.number_input("Stock Quantity", min_value=0, step=1)
        
        if st.button("Save Product"):
            st.success(f"Product '{product_name}' saved with {stock_qty} units.")

    st.markdown("### Top Indian E-commerce Channels")
    
    # Custom CSS for Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Amazon India", "Flipkart", "Myntra", "Meesho", "JioMart", "Nykaa", "Ajio"
    ])

    def channel_card(title, reach, seller_key, link, emoji):
        st.markdown(f"## {emoji} {title}")
        with st.container(border=True):
            st.markdown(f"**🌐 Reach:** {reach}")
            st.markdown(f"**🔑 Key for Sellers:** {seller_key}")
            st.link_button(f"Go to {title} Seller Portal", link)

    with tab1: channel_card("Amazon India", "Largest platform, nationwide.", "High volume, FBA logistics.", "https://sell.amazon.in/", "🛒")
    with tab2: channel_card("Flipkart", "Strongest in electronics & fashion.", "Big Billion Days, local support.", "https://seller.flipkart.com/", "🛍️")
    with tab3: channel_card("Myntra", "Fashion, Lifestyle, Accessories.", "Brand conscious audience.", "https://partner.myntra.com/", "👗")
    with tab4: channel_card("Meesho", "Social commerce, Tier 2/3 cities.", "Zero commission model.", "https://supplier.meesho.com/", "🤝")
    with tab5: channel_card("JioMart", "Groceries, Essentials, General.", "Reliance retail network.", "https://partner.jiomart.com/", "🍎")
    with tab6: channel_card("Nykaa", "Beauty, Skincare, Personal Care.", "High-spending, loyal base.", "https://www.nykaa.com/contactus", "💄")
    with tab7: channel_card("Ajio", "Trend-led fashion.", "Style-conscious youth.", "https://www.ajio.com/s/supplier", "👠")

# --- PICKLIST ---
elif "Picklist" in menu:
    st.markdown('<div class="main-header">Picklist Utility</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Consolidate orders by Master SKU.</div>', unsafe_allow_html=True)

    # KPI Metrics
    with st.container():
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Orders to Pick Today", "12", "-2")
        kpi2.metric("Mapping Accuracy", "99.8%", "+0.1%")
        kpi3.metric("Processed Batches", "55", "Monthly Total")

    st.divider()
    
    col_main1, col_main2 = st.columns([1, 1])
    
    with col_main1:
        with st.container(border=True):
            st.subheader("1. Picklists Upload")
            st.info("Upload up to 10 CSV/Excel files")
            picklist_files = []
            for i in range(10):
                file = st.file_uploader(f"File {i+1}", type=['csv', 'xlsx'], key=f"picklist_{i}", label_visibility="collapsed")
                if file: picklist_files.append(file)
            st.write(f"**Files Uploaded:** {len(picklist_files)}")

    with col_main2:
        with st.container(border=True):
            st.subheader("2. Mapping Master")
            st.info("Upload Master SKU Sheet")
            mapping_file = st.file_uploader("Mapping Sheet", type=['csv', 'xlsx'], key="mapping_sheet")
            
        with st.container(border=True):
            st.subheader("3. Action")
            if len(picklist_files) > 0 and mapping_file:
                if st.button("🚀 Run Consolidation", use_container_width=True):
                    with st.spinner("Processing..."):
                        try:
                            MAP_PICK_SKU = 'Picklist SKU'
                            MASTER_SKU = 'Master SKU'
                            PICK_QTY = 'Quantity'
                            mapping_df = load_data(mapping_file)
                            
                            all_picklists = []
                            for file in picklist_files:
                                df = load_data(file)
                                if MAP_PICK_SKU in df.columns and PICK_QTY in df.columns:
                                    all_picklists.append(df)
                            
                            if not all_picklists:
                                st.error("No valid files found.")
                            else:
                                merged_picklists = pd.concat(all_picklists, ignore_index=True)
                                consolidated = merged_picklists.groupby([MAP_PICK_SKU])[PICK_QTY].sum().reset_index()
                                final_merge = pd.merge(consolidated, mapping_df[[MAP_PICK_SKU, MASTER_SKU]], on=MAP_PICK_SKU, how='left')
                                final_output = final_merge.groupby([MASTER_SKU])[PICK_QTY].sum().reset_index()
                                final_output.rename(columns={PICK_QTY: 'Total Required'}, inplace=True)
                                
                                st.success("Done!")
                                st.dataframe(final_output, use_container_width=True)
                                csv = final_output.to_csv(index=False).encode('utf-8')
                                st.download_button("⬇️ Download Result", csv, "master_picklist.csv", "text/csv", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                st.warning("Upload files to enable.")

# --- SALES ---
elif "Sales" in menu:
    st.markdown('<div class="main-header">Sales Overview</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("Daily Revenue Trends")
        data = pd.DataFrame({
            'Date': pd.date_range(start='1/1/2024', periods=10),
            'Revenue': [100, 150, 120, 200, 250, 220, 300, 280, 350, 400]
        })
        fig = px.line(data, x='Date', y='Revenue', markers=True)
        fig.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

# --- MARKETING ---
elif "Marketing" in menu:
    st.markdown('<div class="main-header">Marketing Hub</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2,1])
    with col1:
        with st.container(border=True):
            st.subheader("🚀 New Campaign")
            st.text_input("Campaign Title", placeholder="e.g. Diwali Sale 2024")
            st.slider("Budget Allocation ($)", 100, 10000, 1000)
            st.text_area("Campaign Description")
            st.button("Launch Campaign")
    
    with col2:
        with st.container(border=True):
            st.subheader("Status")
            st.info("No active campaigns running.")

# --- FINANCIAL ---
elif "Financial" in menu:
    st.markdown('<div class="main-header">Financial Health</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", "$52,000", "+12%")
    col2.metric("Net Profit", "$14,500", "-2%")
    col3.metric("Expenses", "$37,500", "+5%")

# --- INVENTORY ---
elif "Inventory" in menu:
    st.markdown('<div class="main-header">Inventory</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.warning("⚠️ Low stock alert: 3 items below threshold.")
        inventory_data = pd.DataFrame({
            "Item ID": [101, 102, 103, 104],
            "Name": ["Wireless Mouse", "Keyboard", "Monitor", "HDMI Cable"],
            "Stock": [5, 120, 45, 2],
            "Status": ["Low", "Good", "Good", "Critical"]
        })
        
        def highlight_status(val):
            color = 'red' if val in ['Low', 'Critical'] else 'green'
            return f'color: {color}; font-weight: bold'

        st.dataframe(inventory_data.style.map(highlight_status, subset=['Status']), use_container_width=True)

# --- REPORTING ---
elif "Reporting" in menu:
    st.markdown('<div class="main-header">GST & Reporting</div>', unsafe_allow_html=True)
    st.markdown("Generate and prepare your mandatory GST returns.")

    # Main Tabs
    gstr1_tab, gstr3b_tab, general_reports_tab = st.tabs(["📊 GSTR-1 Preparation", "📈 GSTR-3B Summary", "📄 General Reports"])

    # 1. GSTR-1 Preparation Tab
    with gstr1_tab:
        
        # Sub Tabs for Marketplaces
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
            "Amazon", "Flipkart", "Meesho", "Myntra", "JioMart", "Ajio"
        ])
        
        # --- Amazon Tab ---
        with sub_tab1:
            st.caption("Amazon GSTR-1")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                with st.container(border=True):
                    st.write("**B2C MTR Upload**")
                    st.file_uploader("B2C CSV/Excel", key='amazon_b2c')
            with col_a2:
                with st.container(border=True):
                    st.write("**B2B MTR Upload**")
                    st.file_uploader("B2B CSV/Excel", key='amazon_b2b')
            if st.button("Generate Amazon Report", key='gen_amazon'):
                st.success("Processing...")
        
        # --- Flipkart Tab ---
        with sub_tab2:
            st.caption("Flipkart GSTR-1")
            col_f1, col_f2 = st.columns([1,2])
            
            with col_f1:
                with st.container(border=True):
                    st.write("1. Get Template")
                    st.download_button("⬇️ Template", FLIPKART_TEMPLATE_CONTENT, "Flipkart_Template.csv", "text/csv", use_container_width=True)
            
            with col_f2:
                with st.container(border=True):
                    st.write("2. Upload & Process")
                    flipkart_sales_file = st.file_uploader("Upload Data", type=['csv', 'xlsx'], key='flipkart_sales')
                    if st.button("Process Flipkart Data", key='gen_flipkart', use_container_width=True):
                        if flipkart_sales_file:
                            try:
                                df_raw = load_data(flipkart_sales_file)
                                df_processed, state_name_map = process_flipkart_data(df_raw)
                                st.session_state['flipkart_gstr1_df'] = df_processed
                                st.session_state['state_name_map'] = state_name_map
                                st.success("Processed!")
                            except Exception as e:
                                st.error(f"Error: {e}")

            # --- SESSION STATE & DISPLAY ---
            if 'flipkart_gstr1_df' not in st.session_state:
                st.session_state['flipkart_gstr1_df'] = None
            if 'state_name_map' not in st.session_state:
                st.session_state['state_name_map'] = {}

            if st.session_state['flipkart_gstr1_df'] is not None:
                df_processed = st.session_state['flipkart_gstr1_df']
                state_name_map = st.session_state['state_name_map']
                
                st.markdown("---")
                st.subheader("Summary View")
                
                unique_gstins = df_processed[COL_GSTIN].astype(str).unique()
                valid_gstins = sorted([g for g in unique_gstins if g not in ('0.0', 'nan', '0')])
                selected_gstin = st.selectbox("Select GSTIN:", ['ALL'] + valid_gstins)
                
                if selected_gstin == 'ALL':
                    filtered_df = df_processed.copy()
                else:
                    filtered_df = df_processed[df_processed[COL_GSTIN].astype(str) == selected_gstin].copy()
                    
                final_gstr1_summary = filtered_df.groupby('State_Group').agg(
                    Taxable_Value_Total=(COL_TAXABLE_VALUE, 'sum'),
                    IGST_Total=(COL_IGST, 'sum'),
                    CGST_Total=(COL_CGST, 'sum'),
                    SGST_UTGST_Total=(COL_SGST, 'sum'),
                    Total_Net_Quantity=(COL_ITEM_QUANTITY, 'sum')
                ).reset_index()
                
                final_gstr1_summary['Customer Billing State Code'] = final_gstr1_summary['State_Group'].map(state_name_map)
                final_gstr1_summary.drop(columns=['State_Group'], inplace=True)
                
                # Metrics Row
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Taxable Value", f"₹{final_gstr1_summary['Taxable_Value_Total'].sum():,.0f}")
                kpi2.metric("IGST", f"₹{final_gstr1_summary['IGST_Total'].sum():,.0f}")
                kpi3.metric("CGST", f"₹{final_gstr1_summary['CGST_Total'].sum():,.0f}")
                kpi4.metric("SGST", f"₹{final_gstr1_summary['SGST_UTGST_Total'].sum():,.0f}")

                st.dataframe(final_gstr1_summary, use_container_width=True)

        # --- Meesho Tab ---
        with sub_tab3:
            st.caption("Meesho GSTR-1")
            
            with st.container(border=True):
                col_m1, col_m2 = st.columns(2)
                tcs_sales_file = col_m1.file_uploader("1. TCS Sales", type=['csv', 'xlsx'], key='m_sales')
                tcs_sales_return_file = col_m2.file_uploader("2. TCS Returns", type=['csv', 'xlsx'], key='m_returns')
                
                if st.button("Generate Meesho Data", key='gen_meesho'):
                    if tcs_sales_file and tcs_sales_return_file:
                        try:
                            meesho_df = process_meesho_data(tcs_sales_file, tcs_sales_return_file)
                            st.session_state['meesho_gstr1_df'] = meesho_df
                            st.success("Calculated!")
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            if 'meesho_gstr1_df' in st.session_state and st.session_state['meesho_gstr1_df'] is not None:
                m_df = st.session_state['meesho_gstr1_df']
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Taxable Value", f"₹{m_df['Taxable Value'].sum():,.0f}")
                kpi2.metric("IGST", f"₹{m_df['IGST'].sum():,.0f}")
                kpi3.metric("CGST", f"₹{m_df['CGST'].sum():,.0f}")
                kpi4.metric("SGST", f"₹{m_df['SGST'].sum():,.0f}")
                
                st.dataframe(m_df, use_container_width=True)

        # Other tabs placeholders
        for tab, name in zip([sub_tab4, sub_tab5, sub_tab6], ["Myntra", "JioMart", "Ajio"]):
            with tab: st.info(f"{name} integration coming soon.")

    with gstr3b_tab:
        st.info("GSTR-3B Module currently under development.")
        
    with general_reports_tab:
        st.write("Download monthly performance reports.")
        st.download_button("Download Report (CSV)", "Sample Data", "report.csv")

# --- CONFIGURATION ---
elif "Configuration" in menu:
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    
    with st.container(border=True):
        st.subheader("Preferences")
        st.toggle("Enable Dark Mode support", value=True)
        st.toggle("Receive Email Notifications")
        st.text_input("System API Key", type="password")
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
