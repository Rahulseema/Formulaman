# --- STANDARD STATE MAPPING DICTIONARY ---
# Maps common variations/codes to the official Full State Name
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
    # (This replaces the old logic that truncated names)
    state_name_map = df.set_index('Clean_Billing_State')['State_Full_Name'].to_dict()
    
    # We use 'Clean_Billing_State' as the Grouping Key to ensure uniqueness,
    # but the Display Name will be the mapped 'State_Full_Name'
    df['State_Group'] = df['Clean_Billing_State']
    
    return df, state_name_map
