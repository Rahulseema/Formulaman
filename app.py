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
