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
    st.session_state['master_gstr1_data'] = {} # Format: {'Flipkart': df, 'Meesho': df}

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

@st.cache_data(show_spinner="Processing Flipkart data...")
def process_flipkart_data(df):
    """Core logic to process Flipkart DataFrame"""
    # Convert numerics
    numeric_cols = [COL_TAXABLE_VALUE, COL_ITEM_QUANTITY, COL_IGST, COL_CGST, COL_SGST]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.fillna(0, inplace=True)
    
    # Negative Handling
    negative_tax_mask = df[COL_TAXABLE_VALUE] < 0
    df.loc[negative_tax_mask, COL_ITEM_QUANTITY] = df.loc[negative_tax_mask, COL_ITEM_QUANTITY].abs() * -1

    # State grouping
    df['Clean_Billing_State_Upper'] = df[COL_BILLING_STATE].astype(str).str.strip().str.upper()
    df['State_Group'] = df['Clean_Billing_State_Upper'].str[:4]
    
    state_mapping = df[df['Clean_Billing_State_Upper'] != 'NAN'].groupby('State_Group').agg(
        Representative_Name=(COL_BILLING_STATE, lambda x: str(x.iloc[0]).strip()[:5])
    ).reset_index().set_index('State_Group')['Representative_Name'].to_dict()
    
    return df, state_mapping

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
    
    df_merged = pd.concat([df_sales_raw, df_returns_raw], ignore_index=True)
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

# --- REPORTING (GSTR-1 Logic Updated) ---
if "Reporting" in menu:
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

                    if st.button("Process Flipkart Data", key='proc_fk', use_container_width=True):
                        if files_to_process:
                            try:
                                # 1. Consolidate Files (Monthly or Quarterly)
                                df_raw = consolidate_files(files_to_process)
                                
                                # 2. Process Data
                                df_processed, state_map = process_flipkart_data(df_raw)
                                
                                # 3. Generate Summary for Display
                                summary = df_processed.groupby('State_Group').agg(
                                    Taxable=(COL_TAXABLE_VALUE, 'sum'),
                                    IGST=(COL_IGST, 'sum'),
                                    CGST=(COL_CGST, 'sum'),
                                    SGST=(COL_SGST, 'sum')
                                ).reset_index()
                                summary['State'] = summary['State_Group'].map(state_map)
                                final_view = summary[['State', 'Taxable', 'IGST', 'CGST', 'SGST']]
                                
                                # 4. Store for Master Merge (Standardized Columns)
                                st.session_state['master_gstr1_data']['Flipkart'] = final_view
                                st.success("Flipkart Data Processed & Saved for Merge!")
                                st.dataframe(final_view, use_container_width=True)
                                
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.warning("Please upload at least one file.")

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
                            
                            # 3. Store for Master Merge
                            # Standardize Column Names: State, Taxable, IGST, CGST, SGST
                            std_meesho = meesho_final.rename(columns={'Taxable_Value': 'Taxable'})
                            st.session_state['master_gstr1_data']['Meesho'] = std_meesho[['State', 'Taxable', 'IGST', 'CGST', 'SGST']]
                            
                            st.success("Meesho Data Processed & Saved for Merge!")
                            st.dataframe(std_meesho, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Upload Sales and Return files.")

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

# --- OTHER MENUS (Listing, Picklist, etc. preserved) ---
elif "Listing" in menu:
    st.markdown('<div class="main-header">Product Listings</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("➕ Add New Product")
        c1, c2 = st.columns(2)
        c1.text_input("Name"); c2.number_input("Stock", step=1)
        st.button("Save Product")

elif "Picklist" in menu:
    st.markdown('<div class="main-header">Picklist Utility</div>', unsafe_allow_html=True)
    st.info("Please refer to previous code for full Picklist logic.")

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
