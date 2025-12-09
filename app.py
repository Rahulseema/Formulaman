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

# --- CUSTOM CSS FOR "BEAUTIFICATION" & COLOR FIXES ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* --- SIDEBAR STYLING --- */
    section[data-testid="stSidebar"] {
        background-color: #172554; /* Dark Navy Blue */
    }
    
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important; /* White Text */
    }

    /* Fix Radio Button Selection in Sidebar */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
        background-color: #F8FAFC !important;
    }

    /* --- MAIN CONTENT STYLING --- */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A; 
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }

    /* --- CONTAINER STYLING --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] * {
        color: #0F172A !important; 
    }

    /* --- METRIC CARD STYLING --- */
    div[data-testid="stMetric"] {
        background-color: #F1F5F9 !important; 
        border: 1px solid #CBD5E1;
        padding: 15px;
        border-radius: 10px;
        color: #0F172A !important;
    }
    
    div[data-testid="stMetric"] label { color: #475569 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #1E3A8A !important; }

    /* --- BUTTON STYLING --- */
    div.stButton > button {
        background-color: #2563EB !important; 
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8 !important; 
        color: white !important;
    }
    
    input { color: #0F172A !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTICATION LOGIC
# ==========================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

def check_password():
    user = st.session_state.get("username_input", "")
    pwd = st.session_state.get("password_input", "")

    if user == "Rahul" and pwd == "Sparsh@2030":
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = user 
    else:
        st.session_state["authenticated"] = False
        st.error("❌ Invalid User ID or Password")

# LOGIN SCREEN
if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
            <h1 style="color: #1E3A8A; margin-bottom: 0;">🏎️ Formula Man</h1>
            <h3 style="color: #64748B; margin-top: 10px;">Login Required</h3>
        </div>
        <br>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.text_input("User ID", key="username_input")
            st.text_input("Password", type="password", key="password_input")
            st.button("Login", on_click=check_password, use_container_width=True)      
    st.stop()


# ==========================================
# 3. CONSTANTS & INITIALIZATION
# ==========================================
# Initialize Global Data Storage for Merging
if 'master_gstr1_data' not in st.session_state:
    st.session_state['master_gstr1_data'] = {} 

# Initialize Channel Specific Session States
if 'flipkart_raw_df' not in st.session_state:
    st.session_state['flipkart_raw_df'] = None
if 'flipkart_state_map' not in st.session_state:
    st.session_state['flipkart_state_map'] = {}
if 'meesho_df' not in st.session_state:
    st.session_state['meesho_df'] = None

COL_GSTIN = 'Seller GSTIN'
COL_TAXABLE_VALUE = 'Taxable Value (Final Invoice Amount -Taxes)' 
COL_ITEM_QUANTITY = 'Item Quantity' 
COL_IGST = 'IGST Amount' 
COL_CGST = 'CGST Amount' 
COL_SGST = 'SGST Amount (Or UTGST as applicable)' 
COL_BILLING_STATE = "Customer's Billing State" 

FLIPKART_TEMPLATE_CONTENT = """Seller GSTIN,Order ID,Order Item ID,Product Title/Description,FSN,SKU,HSN Code,Event Type,Event Sub Type,Order Type,Fulfilment Type,Order Date,Order Approval Date,Item Quantity,Order Shipped From (State),Warehouse ID,Price before discount,Total Discount,Seller Share,Bank Offer Share,Price after discount (Price before discount-Total discount),Shipping Charges,Final Invoice Amount (Price after discount+Shipping Charges),Type of tax,Taxable Value (Final Invoice Amount -Taxes),CST Rate,CST Amount,VAT Rate,VAT Amount,Luxury Cess Rate,Luxury Cess Amount,IGST Rate,IGST Amount,CGST Rate,CGST Amount,SGST Rate (or UTGST as applicable),SGST Amount (Or UTGST as applicable),TCS IGST Rate,TCS IGST Amount,TCS CGST Rate,TCS CGST Amount,TCS SGST Rate,TCS SGST Amount,Total TCS Deducted,Buyer Invoice ID,Buyer Invoice Date,Buyer Invoice Amount,Customer's Billing Pincode,Customer's Billing State,Customer's Delivery Pincode,Customer's Delivery State,Usual Price,Is Shopsy Order?,TDS Rate,TDS Amount,IRN,Business Name,Business GST Number,Beneficiary Name,IMEI
Mandatory,,,,,,,,,,,,,Mandatory,,,,,,,,,,,Mandatory,,,,,,,Mandatory,Mandatory,Mandatory,Mandatory,Mandatory,Mandatory,,,,,,,,,,,,Mandatory,,,,,,,,,,,"""

# --- STANDARD STATE MAPPING DICTIONARY ---
INDIAN_STATE_MAPPING = {
    "ANDHRA PRADESH": "Andhra Pradesh",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "ASSAM": "Assam",
    "BIHAR": "Bihar",
    "CHHATTISGARH": "Chhattisgarh",
    "GOA": "Goa",
    "GUJARAT": "Gujarat",
    "HARYANA": "Haryana",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "JAMMU & KASHMIR": "Jammu & Kashmir",
    "JAMMU AND KASHMIR": "Jammu & Kashmir",
    "JHARKHAND": "Jharkhand",
    "KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "MADHYA PRADESH": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra",
    "MANIPUR": "Manipur",
    "MEGHALAYA": "Meghalaya",
    "MIZORAM": "Mizoram",
    "NAGALAND": "Nagaland",
    "ODISHA": "Odisha",
    "ORISSA": "Odisha",
    "PUNJAB": "Punjab",
    "RAJASTHAN": "Rajasthan",
    "SIKKIM": "Sikkim",
    "TAMIL NADU": "Tamil Nadu",
    "TAMILNADU": "Tamil Nadu",
    "TELANGANA": "Telangana",
    "TRIPURA": "Tripura",
    "UTTAR PRADESH": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "WEST BENGAL": "West Bengal",
    "ANDAMAN & NICOBAR ISLANDS": "Andaman & Nicobar Islands",
    "ANDAMAN AND NICOBAR ISLANDS": "Andaman & Nicobar Islands",
    "CHANDIGARH": "Chandigarh",
    "DADRA & NAGAR HAVELI": "Dadra & Nagar Haveli",
    "DAMAN & DIU": "Daman & Diu",
    "DELHI": "Delhi",
    "NEW DELHI": "Delhi",
    "LADAKH": "Ladakh",
    "LAKSHADWEEP": "Lakshadweep",
    "PUDUCHERRY": "Puducherry",
    "PONDICHERRY": "Puducherry"
}

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
@st.cache_data
def load_data(file):
    """Loads CSV/Excel. If file is None, returns empty DF."""
    if file is None: return None
    file.seek(0)
    if file.name.endswith('.csv'):
        return pd.read_csv(file, skiprows=[1])
    else:
        return pd.read_excel(file, skiprows=[1])

def consolidate_files(file_list):
    """Combines multiple raw files (Monthly/Quarterly) into one DataFrame."""
    dfs = []
    for f in file_list:
        if f is not None:
            df = load_data(f)
            dfs.append(df)
    if not dfs:
        return None
    return pd.concat(dfs, ignore_index=True)

@st.cache_data(show_spinner="Processing Flipkart sales data...")
def process_flipkart_data(df_raw):
    """
    Cleans data and maps state names to their FULL Standard Names.
    """
    df = df_raw.copy()
    
    # 1. Convert numeric columns
    numeric_cols = [COL_TAXABLE_VALUE, COL_ITEM_QUANTITY, COL_IGST, COL_CGST, COL_SGST]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.fillna(0, inplace=True)
    
    # 2. Handle Negative Quantities for Returns
    negative_tax_mask = df[COL_TAXABLE_VALUE] < 0
    df.loc[negative_tax_mask, COL_ITEM_QUANTITY] = (
        df.loc[negative_tax_mask, COL_ITEM_QUANTITY].abs() * -1
    )

    # 3. Standardize State Names
    # Clean the input: uppercase, strip spaces
    df['Clean_Billing_State'] = df[COL_BILLING_STATE].astype(str).str.strip().str.upper()
    
    # Map to Full Name using the Dictionary
    # If a state isn't in the dict, it defaults to Title Case (e.g., "MYSORE" -> "Mysore")
    df['State_Full_Name'] = df['Clean_Billing_State'].map(INDIAN_STATE_MAPPING).fillna(
        df['Clean_Billing_State'].str.title()
    )
    
    # Create the map dictionary needed for the display function later
    state_name_map = df.set_index('Clean_Billing_State')['State_Full_Name'].to_dict()
    
    # We use 'Clean_Billing_State' as the Grouping Key to ensure uniqueness,
    # but the Display Name will be the mapped 'State_Full_Name'
    df['State_Group'] = df['Clean_Billing_State']
    
    return df, state_name_map

@st.cache_data(show_spinner="Processing Meesho data...")
def process_meesho_data(df_sales_raw, df_returns_raw):
    """Core logic to process Meesho DataFrame"""
    COL_M_QTY = 'quantity'
    COL_M_TAX_VALUE = 'total_taxable_sale_value'
    COL_M_TAX_AMOUNT = 'tax_amount'
    COL_M_STATE = 'end_customer_state_new'
    COLS = [COL_M_QTY, COL_M_TAX_VALUE, COL_M_TAX_AMOUNT]

    # Validate Columns
    for df in [df_sales_raw, df_returns_raw]:
        missing = [c for c in COLS + [COL_M_STATE] if c not in df.columns]
        if missing: raise KeyError(f"Missing columns: {missing}")

    # Process Sales
    for col in COLS: df_sales_raw[col] = pd.to_numeric(df_sales_raw[col], errors='coerce').fillna(0)
    
    # Process Returns (Negative)
    for col in COLS: 
        df_returns_raw[col] = pd.to_numeric(df_returns_raw[col], errors='coerce').fillna(0)
        df_returns_raw[col] = df_returns_raw[col] * -1
    
    df_merged = pd.concat([df_sales, df_returns_raw], ignore_index=True)
    df_merged['State_Clean'] = df_merged[COL_M_STATE].astype(str).str.strip().str.upper()
    
    # Tax Logic
    df_merged['IGST'] = 0.0; df_merged['CGST'] = 0.0; df_merged['SGST'] = 0.0
    
    haryana = df_merged['State_Clean'] == 'HARYANA'
    df_merged.loc[haryana, 'CGST'] = df_merged[COL_M_TAX_AMOUNT] / 2
    df_merged.loc[haryana, 'SGST'] = df_merged[COL_M_TAX_AMOUNT] / 2
    df_merged.loc[~haryana, 'IGST'] = df_merged[COL_M_TAX_AMOUNT]
    
    # Aggregate
    final = df_merged.groupby(COL_M_STATE, dropna=True).agg(
        Total_Qty=(COL_M_QTY, 'sum'),
        Taxable_Value=(COL_M_TAX_VALUE, 'sum'),
        IGST=('IGST', 'sum'),
        CGST=('CGST', 'sum'),
        SGST=('SGST', 'sum')
    ).reset_index()
    
    final.rename(columns={COL_M_STATE: 'State'}, inplace=True)
    return final

# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>🏎️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Formula Man</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Navigate:",
        ["📋 Listing", "📝 Picklist", "📈 Sales", "📣 Marketing", "💰 Financial", "📦 Inventory", "📑 Reporting", "⚙️ Configuration"],
    )
    
    st.markdown("---")
    st.markdown(f"""
    <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
        <small style="color: #94a3b8;">System Status</small><br>
        <strong style="color: #4ade80;">● Online</strong><br>
        <small style="color: #e2e8f0;">User: {st.session_state['user_id']}</small>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = ""
        st.rerun()

# ==========================================
# 6. MAIN CONTENT
# ==========================================

# --- PICKLIST UTILITY (UPDATED LOGIC) ---
if "Picklist" in menu:
    st.markdown('<div class="main-header">Picklist Utility</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Consolidate orders and map them to Master SKUs.</div>', unsafe_allow_html=True)

    # --- KPI METRICS ---
    with st.container():
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Avg. Processing Time", "2 sec", "-0.5s")
        kpi2.metric("Mapping Accuracy", "100%", "Target")
        kpi3.metric("System Status", "Ready", "Online")

    st.divider()
    
    # --- LAYOUT: LEFT (UPLOADS) | RIGHT (MAPPING) ---
    col_main1, col_main2 = st.columns([1, 1])
    
    picklist_files = []
    
    with col_main1:
        with st.container(border=True):
            st.subheader("1. Upload Picklists (Max 10)")
            st.caption("Required Headers: **SKU | Color | Size | Total Quantity**")
            
            # 10 Upload Slots
            for i in range(10):
                label = f"Picklist File {i+1}"
                if i == 0: label += " (Mandatory)"
                file = st.file_uploader(label, type=['csv', 'xlsx'], key=f"picklist_{i}")
                if file: picklist_files.append(file)
                
            st.write(f"**Total Picklists Uploaded:** {len(picklist_files)}")

    with col_main2:
        with st.container(border=True):
            st.subheader("2. Upload Mapping Sheet")
            st.caption("Required Headers: **SKU | Size | Color | Master SKU**")
            mapping_file = st.file_uploader("Mapping Master File (Mandatory)", type=['csv', 'xlsx'], key="mapping_sheet")
            
        with st.container(border=True):
            st.subheader("3. Action")
            
            # --- PROCESS BUTTON LOGIC ---
            if st.button("🚀 Run Consolidation & Mapping", use_container_width=True):
                
                # VALIDATION: Check if files exist
                if not picklist_files:
                    st.error("❌ Please upload at least one Picklist file.")
                elif not mapping_file:
                    st.error("❌ Please upload the Mapping Sheet.")
                else:
                    with st.spinner("Processing files..."):
                        try:
                            # --- CONSTANTS FOR EXPECTED HEADERS ---
                            PL_COLS = ['SKU', 'Color', 'Size', 'Total Quantity']
                            MAP_COLS = ['SKU', 'Size', 'Color', 'Master SKU']
                            
                            # --- 1. PROCESS MAPPING SHEET ---
                            mapping_df = load_data(mapping_file)
                            
                            # Standardize column names (strip spaces, title case)
                            mapping_df.columns = mapping_df.columns.str.strip()
                            
                            # Validate Mapping Headers
                            missing_map = [c for c in MAP_COLS if c not in mapping_df.columns]
                            if missing_map:
                                st.error(f"❌ Mapping Sheet Missing Columns: {missing_map}")
                                st.stop()
                            
                            # Clean Mapping Data for Merge Keys (Strip and Upper)
                            mapping_df['SKU'] = mapping_df['SKU'].astype(str).str.strip()
                            mapping_df['Color'] = mapping_df['Color'].astype(str).str.strip().str.upper()
                            mapping_df['Size'] = mapping_df['Size'].astype(str).str.strip().str.upper()
                            
                            # --- 2. PROCESS PICKLIST FILES ---
                            all_picklist_dfs = []
                            
                            for idx, f in enumerate(picklist_files):
                                df = load_data(f)
                                df.columns = df.columns.str.strip() # Clean headers
                                
                                # Validate Picklist Headers
                                missing_pl = [c for c in PL_COLS if c not in df.columns]
                                if missing_pl:
                                    st.warning(f"⚠️ Skipping File {idx+1} ({f.name}): Missing columns {missing_pl}")
                                    continue
                                
                                # Clean Data for Merge Keys
                                df['SKU'] = df['SKU'].astype(str).str.strip()
                                df['Color'] = df['Color'].astype(str).str.strip().str.upper()
                                df['Size'] = df['Size'].astype(str).str.strip().str.upper()
                                df['Total Quantity'] = pd.to_numeric(df['Total Quantity'], errors='coerce').fillna(0)
                                
                                all_picklist_dfs.append(df)
                                
                            if not all_picklist_dfs:
                                st.error("❌ No valid picklist files to process.")
                                st.stop()
                                
                            # --- 3. MERGE ALL PICKLISTS ---
                            merged_picklist = pd.concat(all_picklist_dfs, ignore_index=True)
                            
                            # Consolidate duplicate rows in raw data first (Group by Keys)
                            consolidated_raw = merged_picklist.groupby(['SKU', 'Color', 'Size'])['Total Quantity'].sum().reset_index()
                            
                            # --- 4. MAP TO MASTER SKU ---
                            # Merge on 3 Keys: SKU + Color + Size
                            final_df = pd.merge(
                                consolidated_raw,
                                mapping_df,
                                on=['SKU', 'Color', 'Size'],
                                how='left'
                            )
                            
                            # Fill unmapped items with "Unknown" or keep original SKU
                            final_df['Master SKU'] = final_df['Master SKU'].fillna('UNMAPPED_ITEM')
                            
                            # --- 5. FINAL GROUP BY MASTER SKU ---
                            final_output = final_df.groupby('Master SKU')['Total Quantity'].sum().reset_index()
                            final_output = final_output.sort_values(by='Total Quantity', ascending=False)

                            # --- 6. DISPLAY RESULTS ---
                            st.success("✅ Consolidation Complete!")
                            
                            col_r1, col_r2 = st.columns([2, 1])
                            
                            with col_r1:
                                st.subheader("Final Consolidated Master Picklist")
                                st.dataframe(final_output, use_container_width=True)
                            
                            with col_r2:
                                st.info("Summary")
                                st.write(f"**Total Items:** {final_output['Total Quantity'].sum():,.0f}")
                                st.write(f"**Unique SKUs:** {len(final_output)}")
                                
                                # Check for Unmapped
                                unmapped_count = final_output[final_output['Master SKU'] == 'UNMAPPED_ITEM']['Total Quantity'].sum()
                                if unmapped_count > 0:
                                    st.error(f"⚠️ **Unmapped Qty:** {unmapped_count}")
                                    st.caption("Check 'UNMAPPED_ITEM' in the list. Update mapping sheet.")
                                else:
                                    st.success("All items mapped successfully!")

                            # --- 7. DOWNLOAD BUTTON ---
                            csv = final_output.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="⬇️ Download Final Master Picklist (CSV)",
                                data=csv,
                                file_name="Master_Consolidated_Picklist.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                                
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")

# --- REPORTING (GSTR-1 Logic) ---
elif "Reporting" in menu:
    st.markdown('<div class="main-header">GST & Reporting</div>', unsafe_allow_html=True)
    st.markdown("Generate and prepare your mandatory GST returns.")

    # Main Tabs
    gstr1_tab, gstr3b_tab, general_reports_tab = st.tabs(["📊 GSTR-1 Preparation", "📈 GSTR-3B Summary", "📄 General Reports"])

    # 1. GSTR-1 Preparation Tab
    with gstr1_tab:
        
        # --- FREQUENCY SELECTOR ---
        st.markdown("### 1. Select Filing Frequency")
        freq_col1, freq_col2 = st.columns([1, 3])
        with freq_col1:
            filing_frequency = st.radio("Frequency:", ["Monthly", "Quarterly"], horizontal=True)
        
        st.divider()
        st.markdown("### 2. Marketplace Uploads")

        # Sub Tabs for Marketplaces
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
            "Amazon", "Flipkart", "Meesho", "Myntra", "JioMart", "Ajio"
        ])
        
        # --- FLIPKART LOGIC ---
        with sub_tab2:
            st.caption(f"Flipkart GSTR-1 ({filing_frequency} Mode)")
            col_f1, col_f2 = st.columns([1,2])
            
            with col_f1:
                with st.container(border=True):
                    st.write("Template")
                    st.download_button("⬇️ Download Template", FLIPKART_TEMPLATE_CONTENT, "Flipkart_Template.csv", "text/csv", use_container_width=True)
            
            with col_f2:
                with st.container(border=True):
                    st.write(f"Upload Data ({filing_frequency})")
                    
                    files_to_process = []
                    if filing_frequency == "Monthly":
                        f = st.file_uploader("Upload Monthly Sales File", type=['csv', 'xlsx'], key='fk_month')
                        if f: files_to_process.append(f)
                    else: # Quarterly
                        c1, c2, c3 = st.columns(3)
                        f1 = c1.file_uploader("Month 1 File", type=['csv', 'xlsx'], key='fk_q1')
                        f2 = c2.file_uploader("Month 2 File", type=['csv', 'xlsx'], key='fk_q2')
                        f3 = c3.file_uploader("Month 3 File", type=['csv', 'xlsx'], key='fk_q3')
                        if f1: files_to_process.append(f1)
                        if f2: files_to_process.append(f2)
                        if f3: files_to_process.append(f3)

                    # PROCESSING BUTTON
                    if st.button("Process Flipkart Data", key='proc_fk', use_container_width=True):
                        if files_to_process:
                            try:
                                # 1. Consolidate Files
                                df_raw = consolidate_files(files_to_process)
                                
                                # 2. Process Data
                                df_processed, state_map = process_flipkart_data(df_raw)
                                
                                # 3. Save to Session State (So we can filter below without re-uploading)
                                st.session_state['flipkart_raw_df'] = df_processed
                                st.session_state['flipkart_state_map'] = state_map
                                
                                st.success("Data processed successfully! Scroll down for reports.")
                                
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.warning("Please upload at least one file.")

            # --- FLIPKART REPORT VIEW (FILTERING RESTORED) ---
            # This runs if data exists in Session State, independent of the button click
            if st.session_state['flipkart_raw_df'] is not None:
                st.divider()
                st.subheader("Flipkart Summary & Cards")
                
                df_flipkart = st.session_state['flipkart_raw_df']
                state_map = st.session_state['flipkart_state_map']

                # 1. GSTIN FILTER
                unique_gstins = df_flipkart[COL_GSTIN].astype(str).unique()
                valid_gstins = sorted([g for g in unique_gstins if g not in ('0.0', 'nan', '0')])
                gstin_options = ['ALL'] + valid_gstins
                
                selected_gstin = st.selectbox("Select Seller GSTIN:", gstin_options)

                # 2. FILTER DATA
                if selected_gstin == 'ALL':
                    filtered_df = df_flipkart.copy()
                else:
                    filtered_df = df_flipkart[df_flipkart[COL_GSTIN].astype(str) == selected_gstin].copy()

                # 3. CALCULATE METRICS
                total_taxable = filtered_df[COL_TAXABLE_VALUE].sum()
                total_igst = filtered_df[COL_IGST].sum()
                total_cgst = filtered_df[COL_CGST].sum()
                total_sgst = filtered_df[COL_SGST].sum()
                total_qty = filtered_df[COL_ITEM_QUANTITY].sum()

                # 4. DISPLAY CARDS
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Taxable Value", f"₹ {total_taxable:,.0f}")
                m2.metric("IGST", f"₹ {total_igst:,.0f}")
                m3.metric("CGST", f"₹ {total_cgst:,.0f}")
                m4.metric("SGST", f"₹ {total_sgst:,.0f}")
                m5.metric("Total Qty", f"{total_qty:,.0f}")

                # 5. PREPARE AGGREGATED TABLE FOR DISPLAY
                summary_view = filtered_df.groupby('State_Group').agg(
                    Taxable=(COL_TAXABLE_VALUE, 'sum'),
                    IGST=(COL_IGST, 'sum'),
                    CGST=(COL_CGST, 'sum'),
                    SGST=(COL_SGST, 'sum'),
                    Qty=(COL_ITEM_QUANTITY, 'sum')
                ).reset_index()
                
                # Map to Full Name
                summary_view['State'] = summary_view['State_Group'].map(state_map)
                
                # Reorder cols
                summary_view = summary_view[['State', 'Taxable', 'IGST', 'CGST', 'SGST', 'Qty']]
                
                st.dataframe(summary_view, use_container_width=True)

                # 6. SAVE TO MASTER MERGE
                st.session_state['master_gstr1_data']['Flipkart'] = summary_view[['State', 'Taxable', 'IGST', 'CGST', 'SGST']]
                
                # Download Button
                csv = summary_view.to_csv(index=False).encode('utf-8')
                st.download_button(f"⬇️ Download Summary ({selected_gstin})", csv, "flipkart_summary.csv", "text/csv")


        # --- MEESHO LOGIC ---
        with sub_tab3:
            st.caption(f"Meesho GSTR-1 ({filing_frequency} Mode)")
            
            with st.container(border=True):
                files_sales = []
                files_returns = []
                
                if filing_frequency == "Monthly":
                    c1, c2 = st.columns(2)
                    fs = c1.file_uploader("Sales File", type=['csv', 'xlsx'], key='m_sales_m')
                    fr = c2.file_uploader("Returns File", type=['csv', 'xlsx'], key='m_ret_m')
                    if fs: files_sales.append(fs)
                    if fr: files_returns.append(fr)
                else: # Quarterly
                    st.write("**Month 1**")
                    c1, c2 = st.columns(2)
                    fs1 = c1.file_uploader("Sales M1", key='m_s1'); fr1 = c2.file_uploader("Ret M1", key='m_r1')
                    
                    st.write("**Month 2**")
                    c3, c4 = st.columns(2)
                    fs2 = c3.file_uploader("Sales M2", key='m_s2'); fr2 = c4.file_uploader("Ret M2", key='m_r2')
                    
                    st.write("**Month 3**")
                    c5, c6 = st.columns(2)
                    fs3 = c5.file_uploader("Sales M3", key='m_s3'); fr3 = c6.file_uploader("Ret M3", key='m_r3')

                    if fs1: files_sales.append(fs1)
                    if fr1: files_returns.append(fr1)
                    if fs2: files_sales.append(fs2)
                    if fr2: files_returns.append(fr2)
                    if fs3: files_sales.append(fs3)
                    if fr3: files_returns.append(fr3)
                
                if st.button("Process Meesho Data", key='proc_meesho', use_container_width=True):
                    if files_sales and files_returns:
                        try:
                            # 1. Consolidate Raw Files
                            df_sales_all = consolidate_files(files_sales)
                            df_returns_all = consolidate_files(files_returns)
                            
                            # 2. Process
                            meesho_final = process_meesho_data(df_sales_all, df_returns_all)
                            
                            # 3. Store in Session State
                            st.session_state['meesho_df'] = meesho_final

                            # 4. Store for Master Merge
                            std_meesho = meesho_final.rename(columns={'Taxable_Value': 'Taxable'})
                            st.session_state['master_gstr1_data']['Meesho'] = std_meesho[['State', 'Taxable', 'IGST', 'CGST', 'SGST']]
                            
                            st.success("Meesho Data Processed & Saved for Merge!")
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Upload Sales and Return files.")

            # --- MEESHO REPORT VIEW (VALUE CARDS ADDED) ---
            if st.session_state['meesho_df'] is not None:
                st.divider()
                st.subheader("Meesho Summary & Cards")
                
                m_df = st.session_state['meesho_df']

                # 1. CALCULATE METRICS
                total_taxable = m_df['Taxable_Value'].sum()
                total_igst = m_df['IGST'].sum()
                total_cgst = m_df['CGST'].sum()
                total_sgst = m_df['SGST'].sum()
                total_qty = m_df['Total_Qty'].sum()

                # 2. DISPLAY CARDS
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Taxable Value", f"₹ {total_taxable:,.0f}")
                m2.metric("IGST", f"₹ {total_igst:,.0f}")
                m3.metric("CGST", f"₹ {total_cgst:,.0f}")
                m4.metric("SGST", f"₹ {total_sgst:,.0f}")
                m5.metric("Total Qty", f"{total_qty:,.0f}")

                # 3. SHOW DATAFRAME
                st.dataframe(m_df, use_container_width=True)

                # 4. DOWNLOAD BUTTON
                csv = m_df.to_csv(index=False).encode('utf-8')
                st.download_button(f"⬇️ Download Meesho Summary", csv, "meesho_summary.csv", "text/csv")


        # --- Placeholders for Others ---
        for t, n in zip([sub_tab1, sub_tab4, sub_tab5, sub_tab6], ["Amazon", "Myntra", "JioMart", "Ajio"]):
            with t: st.info(f"{n} integration coming soon.")

        st.divider()
        
        # --- 3. MASTER MERGE SECTION ---
        st.markdown("### 3. Consolidated Report (Master Merge)")
        with st.container(border=True):
            st.write("Merge processed data from all channels into a single GSTR-1 CSV.")
            
            # Show what data is ready
            ready_channels = list(st.session_state['master_gstr1_data'].keys())
            if ready_channels:
                st.success(f"Ready to merge: {', '.join(ready_channels)}")
                
                if st.button("🚀 Generate Consolidated GSTR-1 Report", use_container_width=True):
                    # Combine all dataframes
                    all_dfs = []
                    for channel, df in st.session_state['master_gstr1_data'].items():
                        df['Channel'] = channel # Add source column
                        all_dfs.append(df)
                    
                    if all_dfs:
                        master_df = pd.concat(all_dfs, ignore_index=True)
                        
                        # Group by State to get final totals
                        final_master = master_df.groupby('State').agg(
                            Taxable=('Taxable', 'sum'),
                            IGST=('IGST', 'sum'),
                            CGST=('CGST', 'sum'),
                            SGST=('SGST', 'sum')
                        ).reset_index()
                        
                        # Rounding
                        for c in ['Taxable', 'IGST', 'CGST', 'SGST']:
                            final_master[c] = final_master[c].round(2)

                        st.subheader("Final Consolidated Summary")
                        st.dataframe(final_master, use_container_width=True)
                        
                        # Download Button
                        csv = final_master.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Download Master GSTR-1 CSV",
                            data=csv,
                            file_name=f"Master_GSTR1_{filing_frequency}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
            else:
                st.info("No data processed yet. Process individual channels above first.")

    with gstr3b_tab:
        st.info("GSTR-3B Module currently under development.")
        
    with general_reports_tab:
        st.write("Download monthly performance reports.")
        st.download_button("Download Report (CSV)", "Sample Data", "report.csv")

# --- OTHER MENUS (Listing, Sales, etc.) ---
elif "Listing" in menu:
    st.markdown('<div class="main-header">Product Listings</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("➕ Add New Product")
        c1, c2 = st.columns(2)
        c1.text_input("Name"); c2.number_input("Stock", step=1)
        st.button("Save Product")

elif "Sales" in menu:
    st.markdown('<div class="main-header">Sales Overview</div>', unsafe_allow_html=True)
    data = pd.DataFrame({'Date': pd.date_range('1/1/2024', periods=10), 'Revenue': [100, 150, 120, 200, 250, 220, 300, 280, 350, 400]})
    st.plotly_chart(px.line(data, x='Date', y='Revenue'), use_container_width=True)

elif "Marketing" in menu:
    st.markdown('<div class="main-header">Marketing</div>', unsafe_allow_html=True)
    st.info("No active campaigns.")

elif "Financial" in menu:
    st.markdown('<div class="main-header">Financials</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Revenue", "$52k"); c2.metric("Profit", "$14k")

elif "Inventory" in menu:
    st.markdown('<div class="main-header">Inventory</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({"Item": ["A", "B"], "Stock": [10, 5]}), use_container_width=True)

elif "Configuration" in menu:
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    st.button("Save Settings")
