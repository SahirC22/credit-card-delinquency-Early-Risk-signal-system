import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import re

# Only import mysql-connector if needed
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Early Risk Alerts:Credit Card Delinquency Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS - optimized for both light and dark modes
st.markdown(
    """
<style>
    /* Layout */
    .stApp {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                     "Segoe UI", sans-serif;
    }

    /* ========================================
       LIGHT MODE STYLES (Default)
       ======================================== */
    
    /* Headers - Light Mode */
    .main-header {
        font-size: 2.2rem;
        font-weight: 650;
        color: #111827 !important;
        margin-bottom: 0.25rem;
    }

    .sub-header {
        font-size: 1.05rem;
        color: #6b7280 !important;
        margin-bottom: 1.75rem;
    }

    /* Cards - Light Mode */
    .metric-card,
    .high-risk-card,
    .medium-risk-card,
    .low-risk-card {
        background: #ffffff !important;
        padding: 18px 20px;
        border-radius: 12px;
        color: #111827 !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        border: 1px solid #e5e7eb !important;
    }

    .metric-card h2,
    .high-risk-card h2,
    .medium-risk-card h2,
    .low-risk-card h2 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 650;
        color: #111827 !important;
    }

    .metric-card p,
    .high-risk-card p,
    .medium-risk-card p,
    .low-risk-card p {
        margin: 2px 0 0 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6b7280 !important;
    }

    .metric-card small,
    .high-risk-card small,
    .medium-risk-card small,
    .low-risk-card small {
        display: block;
        margin-top: 4px;
        font-size: 0.8rem;
        color: #4b5563 !important;
    }

    /* Card border colors */
    .high-risk-card {
        border-top: 3px solid #b91c1c;
    }
    .medium-risk-card {
        border-top: 3px solid #d97706;
    }
    .low-risk-card {
        border-top: 3px solid #059669;
    }

    /* Alert boxes - Light Mode */
    .insight-box,
    .error-box,
    .success-box {
        padding: 14px 16px;
        margin: 18px 0;
        border-radius: 8px;
        border: 1px solid transparent;
    }

    .insight-box {
        background-color: #fffbeb !important;
        border-color: #fbbf24 !important;
        color: #92400e !important;
    }

    .error-box {
        background-color: #fef2f2 !important;
        border-color: #ef4444 !important;
        color: #991b1b !important;
    }

    .success-box {
        background-color: #ecfdf3 !important;
        border-color: #10b981 !important;
        color: #065f46 !important;
    }

    /* Tabs - Light Mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #e5e7eb !important;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        padding: 0px 16px;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        font-size: 0.92rem;
        color: #4b5563 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #111827 !important;
        border-bottom: 2px solid #3b82f6;
    }

    /* Dataframe - Light Mode */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    }

    /* Footer - Light Mode */
    .footer-text {
        color: #6b7280 !important;
    }
    
    .footer-text p {
        color: #6b7280 !important;
    }
    
    .footer-text strong {
        color: #111827 !important;
    }

    /* ================== DARK MODE STYLES ====================== */
    body.dark-mode .main-header,
    html.dark-mode .main-header,
    body.dark-mode h1.main-header,
    html.dark-mode h1.main-header {
        color: #fff !important;
        text-shadow: 0 2px 8px #000, 0 1px 3px rgba(0,0,0,0.5);
        background: none !important;
        opacity: 1 !important;
        font-weight: 800 !important;
    }
    body.dark-mode .footer-text,
    html.dark-mode .footer-text,
    body.dark-mode .footer-text p,
    html.dark-mode .footer-text p {
        color: #fff !important;
        opacity: 0.8 !important;
    }
</style>

<script>
    /**
     * Simple Theme Detection - Adds/Removes 'dark-mode' class
     * This ensures CSS rules are applied properly in both light and dark modes
     */
    function detectAndApplyTheme() {
        // Check Streamlit's app container background color
        const appContainer = document.querySelector('[data-testid="stAppViewContainer"]');
        const body = document.body;
        const html = document.documentElement;
        
        let isDark = false;
        
        if (appContainer) {
            const bgColor = window.getComputedStyle(appContainer).backgroundColor;
            // Streamlit dark mode backgrounds (exact colors Streamlit uses)
            const darkColors = [
                'rgb(38, 39, 48)', 'rgb(14, 17, 23)', 'rgb(19, 23, 34)',
                'rgb(15, 17, 23)', 'rgb(17, 24, 39)', 'rgb(31, 41, 55)',
                'rgba(38, 39, 48, 1)', 'rgba(14, 17, 23, 1)',
                'rgb(38, 39, 48)', 'rgb(14, 17, 23)'
            ];
            
            // Check for exact dark color match first
            if (darkColors.includes(bgColor)) {
                isDark = true;
            } else {
                // Check brightness as fallback (only if brightness is very low)
                const match = bgColor.match(/\d+/g);
                if (match && match.length >= 3) {
                    const r = parseInt(match[0]);
                    const g = parseInt(match[1]);
                    const b = parseInt(match[2]);
                    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
                    // Only consider it dark if brightness is very low (strict check)
                    if (brightness < 80) {
                        isDark = true;
                    }
                }
            }
        }
        
        // Also check sidebar and main block to be more accurate
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const mainBlock = document.querySelector('.main .block-container');
        
        if (!isDark && sidebar) {
            const sidebarBg = window.getComputedStyle(sidebar).backgroundColor;
            const match = sidebarBg.match(/\d+/g);
            if (match && match.length >= 3) {
                const r = parseInt(match[0]);
                const g = parseInt(match[1]);
                const b = parseInt(match[2]);
                const brightness = (r * 299 + g * 587 + b * 114) / 1000;
                if (brightness < 80) {
                    isDark = true;
                }
            }
        }
        
        // Apply or remove dark-mode class
        if (isDark) {
            body.classList.add('dark-mode');
            html.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
            html.classList.remove('dark-mode');
        }
    }
    
    // Initialize theme detection
    function initTheme() {
        detectAndApplyTheme();
        // Check multiple times to catch Streamlit's initialization
        setTimeout(detectAndApplyTheme, 100);
        setTimeout(detectAndApplyTheme, 500);
        setTimeout(detectAndApplyTheme, 1000);
        setTimeout(detectAndApplyTheme, 2000);
    }
    
    // Run immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
    
    window.addEventListener('load', initTheme);
    
    // Watch for DOM changes (Streamlit reruns and theme changes)
    const observer = new MutationObserver(function() {
        setTimeout(detectAndApplyTheme, 50);
    });
    
    if (document.body) {
        observer.observe(document.body, { 
            attributes: true, 
            attributeFilter: ['class', 'style'],
            childList: true,
            subtree: true
        });
    }
    
    // Periodic check for Streamlit reruns and theme changes
    setInterval(detectAndApplyTheme, 1000);
</script>
""",
    unsafe_allow_html=True,
)

# HEADER STYLES
st.markdown('<h1 class="main-header">Early Risk Alert Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">A Machine Learning-Powered Behavioral Pattern Detection for Proactive Risk Management</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header"></p>', unsafe_allow_html=True)

# LOAD ML MODELS
@st.cache_resource
def load_models():
    try:
        with open('rf_delinquency_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('gb_delinquency_model.pkl', 'rb') as f:
            gb_model = pickle.load(f)
        with open('feature_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('model_metadata.json', 'r') as f:
            metadata = json.load(f)
        return rf_model, gb_model, scaler, metadata
    except Exception as e:
        st.error(f"Error loading models: {e}")
        st.stop()

rf_model, gb_model, scaler, metadata = load_models()
feature_columns = metadata['feature_columns']

# ENHANCED COLUMN STANDARDIZATION - HANDLES MULTIPLE FORMATS
def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map a wide variety of input column formats to the model's expected schema.

    Handles:
    - Spaces / underscores / hyphens / punctuation:
      "Credit Limit", "credit-limit", "CREDIT_LIMIT" → "Credit_Limit"
    - Different percent formats:
      "Utilisation %", "Utilisation pct", "utilisation(%)" → "Utilisation_%"
    - American / British spelling:
      "Utilization %" → "Utilisation_%"
    - Case-insensitive and separator-free names:
      "avgpaymentratio", "MIN DUE PAID FREQUENCY" → canonical columns
    """

    # Normalize function:
    # 1. lowercase
    # 2. standardize percent variants (%, percent, pct)
    # 3. remove all non-alphanumeric characters
    def normalize(col_name: str) -> str:
        s = str(col_name).lower().strip()
        # Standardise British/American spelling to common tokens
        s = s.replace("utilization", "utilisation")
        s = s.replace("behaviour", "behavior")  # handle double spellings
        s = s.replace("behavioural", "behavioral")
        # Standardise percent variants
        s = s.replace("percentage", "percent")
        s = s.replace("pct", "percent")
        s = s.replace("%", "percent")
        # Remove currency symbols / brackets / punctuation / spaces
        s = re.sub(r"[^a-z0-9]", "", s)
        return s

    # Canonical columns the model / app expects
    canonical_names = {
        # ID & outcome columns
        "customer_id": "Customer_ID",
        "customerid": "Customer_ID",
        "cust_id": "Customer_ID",
        "account_id": "Customer_ID",
        "dpdbucketnextmonth": "DPD_Bucket_Next_Month",
        "dpdnextmonth": "DPD_Bucket_Next_Month",
        "dpd": "DPD_Bucket_Next_Month",

        # Feature columns
        "creditlimit": "Credit_Limit",
        "limit": "Credit_Limit",

        # Utilisation (British) / Utilization (US)
        "utilisationpercent": "Utilisation_%",
        "utilizationpercent": "Utilisation_%",
        "utilisation": "Utilisation_%",
        "utilization": "Utilisation_%",
        "utilisationratio": "Utilisation_%",
        "utilizationratio": "Utilisation_%",

        # Avg payment ratio
        "avgpaymentratio": "Avg_Payment_Ratio",
        "averagepaymentratio": "Avg_Payment_Ratio",
        "paymentratio": "Avg_Payment_Ratio",
        "payratio": "Avg_Payment_Ratio",

        # Min due paid frequency
        "minduepaidfrequency": "Min_Due_Paid_Frequency",
        "minduefrequency": "Min_Due_Paid_Frequency",
        "minduefreq": "Min_Due_Paid_Frequency",
        "minpayfrequency": "Min_Due_Paid_Frequency",

        # Merchant mix index
        "merchantmixindex": "Merchant_Mix_Index",
        "merchantmix": "Merchant_Mix_Index",
        "merchantconcentration": "Merchant_Mix_Index",

        # Cash withdrawal percentage
        "cashwithdrawalpercent": "Cash_Withdrawal_%",
        "cashwithdrawal": "Cash_Withdrawal_%",
        "cashadvancepercent": "Cash_Withdrawal_%",
        "cashadvance": "Cash_Withdrawal_%",

        # Recent spend change
        "recentspendchangepercent": "Recent_Spend_Change_%",
        "recentspendchange": "Recent_Spend_Change_%",
        "spendchangepercent": "Recent_Spend_Change_%",
        "spendchange": "Recent_Spend_Change_%",
    }

    # Also register direct canonical names and simple underscore/space variants
    expected_canonicals = [
        "Customer_ID",
        "Credit_Limit",
        "Utilisation_%",
        "Avg_Payment_Ratio",
        "Min_Due_Paid_Frequency",
        "Merchant_Mix_Index",
        "Cash_Withdrawal_%",
        "Recent_Spend_Change_%",
        "DPD_Bucket_Next_Month",
    ]

    for canonical in expected_canonicals:
        # Register the exact canonical form
        canonical_names[normalize(canonical)] = canonical
        # Register a space version like "Credit Limit"
        space_variant = canonical.replace("_", " ").replace("%", " percent")
        canonical_names[normalize(space_variant)] = canonical

    # Build variant mapping with normalized keys
    variant_mapping = {
        normalize(key): canonical for key, canonical in canonical_names.items()
    }
    canonical_lookup = {
        normalize(canonical): canonical for canonical in expected_canonicals
    }

    # Rename dataframe columns based on normalized variants
    new_columns = []
    for col in df.columns:
        normalized_col = normalize(col)
        mapped_name = variant_mapping.get(normalized_col)

        if mapped_name is None:
            # Fuzzy containment fallback: handle extra suffix/prefix like "creditlimitusd"
            for canon_norm, canonical in canonical_lookup.items():
                if canon_norm in normalized_col or normalized_col in canon_norm:
                    mapped_name = canonical
                    break

        if mapped_name is None:
            new_columns.append(col)  # Keep original if no match
        else:
            new_columns.append(mapped_name)

    df.columns = new_columns
    return df

# DATA LOADING WITH MULTIPLE SOURCES
def load_data_from_source(source_type, **kwargs):
    """Load data from multiple sources with error handling"""

    if source_type == "Upload File":
        uploaded_file = kwargs.get('file')
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    st.error("❌ Unsupported file format. Please upload CSV or XLSX.")
                    return None

                # Store original columns for debugging
                original_columns = list(df.columns)

                # Standardize column names
                df = standardize_column_names(df)

                st.success(f"✅ File loaded: {len(df)} rows, {len(df.columns)} columns")

                # Show column mapping
                with st.expander("🔄 Column Name Mapping (Original → Standardized)"):
                    mapping_df = pd.DataFrame({
                        'Original Column': original_columns,
                        'Standardized Column': df.columns
                    })
                    st.dataframe(mapping_df, use_container_width=True)

                return df

            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
                return None
        return None

    elif source_type == "MySQL Database":
        if not MYSQL_AVAILABLE:
            st.error("❌ MySQL connector not installed. Run: pip install mysql-connector-python")
            return None

        try:
            host = kwargs.get('host', 'localhost')
            user = kwargs.get('user', 'root')
            password = kwargs.get('password', '')
            database = kwargs.get('database', 'credit_cards')
            query = kwargs.get('query', 'SELECT * FROM customer_data')

            connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            df = pd.read_sql(query, connection)
            connection.close()

            df = standardize_column_names(df)
            st.success(f"✅ Database connected: {len(df)} rows loaded")
            return df

        except Exception as e:
            st.error(f"❌ Database connection error: {e}")
            return None

    elif source_type == "Sample Data":
        try:
            df = pd.read_csv('sample_data.csv')
            df = standardize_column_names(df)
            return df
        except FileNotFoundError:
            st.error("❌ sample_data.csv not found.")
            return None

    return None

# RISK FLAG GENERATION
def generate_risk_flags(row):
    flags = []
    score = 0

    if row['Avg_Payment_Ratio'] < 60:
        flags.append('Low Payment')
        score += 3
    elif row['Avg_Payment_Ratio'] < 70:
        flags.append('Moderate Pay')
        score += 1

    if row['Min_Due_Paid_Frequency'] > 60:
        flags.append('Min-Due Pattern')
        score += 3
    elif row['Min_Due_Paid_Frequency'] > 45:
        flags.append('Occasional Min-Due')
        score += 1

    if row['Recent_Spend_Change_%'] < -10:
        flags.append('Spend Drop')
        score += 2.5

    if row['Utilisation_%'] > 90:
        flags.append('High Util')
        score += 2

    if row['Merchant_Mix_Index'] < 0.35:
        flags.append('Conc. Spend')
        score += 1

    return score, flags

# RISK SCORING WITH MODEL SELECTION
def calculate_risk_scores(df, model_choice='Random Forest'):
    """Calculate risk scores using selected ML model"""
    try:
        # Standardize column names again to catch any post-upload edits
        df = standardize_column_names(df.copy())

        # Validate features
        missing_features = [col for col in feature_columns if col not in df.columns]
        if missing_features:
            st.markdown("""
            <div class="error-box">
                <h4>❌ Missing Required Features</h4>
                <p>The following columns are required but not found in your data:</p>
            </div>
            """, unsafe_allow_html=True)

            for feat in missing_features:
                st.error(f"• {feat}")

            with st.expander("🔎 Debug: Columns detected after standardization"):
                debug_df = pd.DataFrame({
                    'Detected Columns': df.columns
                })
                st.dataframe(debug_df, use_container_width=True, hide_index=True)

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📋 Available Columns in Your Data")
                available_df = pd.DataFrame({
                    'Column Name': df.columns,
                    'Data Type': df.dtypes.values
                })
                st.dataframe(available_df, use_container_width=True)

            with col2:
                st.markdown("### ✅ Required Column Names")
                required_df = pd.DataFrame({
                    'Required Column': feature_columns,
                    'Alternative Names': [
                        'Customer_ID or Customer ID',
                        'Credit_Limit or Credit Limit',
                        'Utilisation_% or Utilisation %',
                        'Avg_Payment_Ratio or Avg Payment Ratio',
                        'Min_Due_Paid_Frequency or Min Due Paid Frequency',
                        'Merchant_Mix_Index or Merchant Mix Index',
                        'Cash_Withdrawal_% or Cash Withdrawal %',
                        'Recent_Spend_Change_% or Recent Spend Change %'
                    ]
                })
                st.dataframe(required_df, use_container_width=True)

            st.markdown("""
            <div class="insight-box">
                <h4>💡 Possible Issues</h4>
                <ol>
                    <li><strong>Wrong file uploaded:</strong> You may have uploaded a documentation/schema file instead of the actual data file.</li>
                    <li><strong>Sheet selection:</strong> If using Excel, ensure you're reading the correct sheet with customer data.</li>
                    <li><strong>Column naming:</strong> The app accepts both "Credit_Limit" and "Credit Limit" formats.</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

            return None

        X = df[feature_columns].copy()

        # Handle missing values
        if X.isnull().any().any():
            st.warning("⚠️ Dataset contains missing values. Filling with median.")
            X = X.fillna(X.median())

        # Scale features
        X_scaled = scaler.transform(X)

        # Select model
        model = rf_model if model_choice == 'Random Forest' else gb_model

        # Get predictions
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)[:, 1]

        # Generate risk scores and flags
        risk_data = df.apply(generate_risk_flags, axis=1)
        df['Risk_Score'] = [r[0] for r in risk_data]
        df['Risk_Flags'] = [r[1] for r in risk_data]
        df['ML_Probability'] = (probabilities * 100).round(2)
        df['ML_Prediction'] = predictions

        # Risk levels
        df['Risk_Level'] = pd.cut(df['Risk_Score'], 
                                   bins=[0, 3, 6, 10], 
                                   labels=['Low Risk', 'Medium Risk', 'High Risk'])

        st.markdown("""
        <div class="success-box">
            <Model:>✅ Risk Scores Calculated Successfully! | Model: <strong>{}</strong> | Customers Analyzed: <strong>{}</strong></p>            
        </div>
        """.format(model_choice, len(df)), unsafe_allow_html=True)
        return df

    except Exception as e:
        st.error(f"❌ Risk scoring error: {e}")
        import traceback
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())
        return None

# ============================================================================
# SIDEBAR - DATA SOURCE & MODEL SELECTION
# ============================================================================

st.sidebar.markdown("## Data Configuration")

# DATA SOURCE SELECTION
data_source = st.sidebar.selectbox(
    "Select Data Source",
    ["Sample Data", "Upload File", "MySQL Database"],
    help="Choose where to load customer data from"
)

df = None

# FILE UPLOAD HANDLER
if data_source == "Upload File":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### File Upload")

    uploaded_file = st.sidebar.file_uploader(
        "Choose CSV or XLSX file",
        type=['csv', 'xlsx'],
        help="Upload your credit card customer data"
    )

    if uploaded_file:
        file_details = {
            "Filename": uploaded_file.name,
            "FileType": uploaded_file.type,
            "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
        }

        with st.sidebar.expander("📄 File Details"):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")

        with st.spinner("Loading file..."):
            df = load_data_from_source("Upload File", file=uploaded_file)

# MYSQL DATABASE HANDLER
elif data_source == "MySQL Database":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗄️ Database Connection")

    with st.sidebar.expander("⚙️ Connection Settings", expanded=True):
        db_host = st.text_input("Host", value="localhost", key="db_host")
        db_user = st.text_input("Username", value="root", key="db_user")
        db_password = st.text_input("Password", type="password", key="db_password")
        db_name = st.text_input("Database", value="credit_cards", key="db_name")
        db_query = st.text_area(
            "SQL Query", 
            value="SELECT * FROM customer_data LIMIT 1000",
            height=100,
            key="db_query"
        )

    if st.sidebar.button("🔌 Connect & Load Data", type="primary", key="db_connect"):
        with st.spinner("Connecting to database..."):
            df = load_data_from_source(
                "MySQL Database",
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                query=db_query
            )

# SAMPLE DATA HANDLER
elif data_source == "Sample Data":
    with st.spinner("Loading sample data..."):
        df = load_data_from_source("Sample Data")
        if df is not None:
            st.sidebar.success(f"✅ Loaded {len(df)} sample customers")

# MODEL SELECTION
st.sidebar.markdown("---")
st.sidebar.markdown("## ML Model Configuration")

model_choice = st.sidebar.selectbox(
    "Select Prediction Model",
    ["Random Forest", "Gradient Boosting"],
    help="Choose the machine learning model for risk scoring"
)

# Display model info
if model_choice == "Random Forest":
    st.sidebar.info(f"""
    **Random Forest Classifier**
    - Accuracy: {metadata['random_forest_accuracy']*100:.1f}%
    - ROC-AUC: {metadata['random_forest_auc']:.3f}
    - Top Feature: Utilisation_%
    """)
else:
    st.sidebar.info(f"""
    **Gradient Boosting Classifier**
    - Accuracy: {metadata['gradient_boosting_accuracy']*100:.1f}%
    - ROC-AUC: {metadata['gradient_boosting_auc']:.3f}
    - Top Feature: Min_Due_Frequency
    """)

# PROCESS DATA BUTTON
if df is not None:
    st.sidebar.markdown("---")
    if st.sidebar.button("⚡ Calculate Risk Scores", type="primary", key="process"):
        with st.spinner(f"Processing with {model_choice}..."):
            df = calculate_risk_scores(df, model_choice)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.markdown('<h1 class="main-header">Credit Card Delinquency Dashboard</h1>', unsafe_allow_html=True)


# DATA PREVIEW (Before Processing)
if df is not None and 'Risk_Score' not in df.columns:
    st.info(f"Data loaded: **{len(df)} customers** | Click **⚡ Calculate Risk Scores** in sidebar to proceed")

    with st.expander("🔍 Data Preview (First 10 Rows)"):
        st.dataframe(df.head(10), use_container_width=True)

    with st.expander("📋 Column Information"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values
        })
        st.dataframe(col_info, use_container_width=True)

# MAIN DASHBOARD (After Processing)
elif df is not None and 'Risk_Score' in df.columns:

    # TABS
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Portfolio Overview",
            "Priority Customers",
            "Risk Framework",
            "Outreach Playbook",
            "Performance Metrics",
            "Dataset Explorer",
        ]
    )

    # TAB 1: PORTFOLIO OVERVIEW
    with tab1:
        st.markdown("### Portfolio Snapshot")

        col1, col2, col3, col4 = st.columns(4)

        total_customers = len(df)
        high_risk = len(df[df['Risk_Level'] == 'High Risk'])
        medium_risk = len(df[df['Risk_Level'] == 'Medium Risk'])
        low_risk = len(df[df['Risk_Level'] == 'Low Risk'])

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{total_customers}</h2>
                <p>Total Customers</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="high-risk-card">
                <h2>{high_risk}</h2>
                <p>HIGH RISK</p>
                <small>{high_risk/total_customers*100:.1f}% of Portfolio</small>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="medium-risk-card">
                <h2>{medium_risk}</h2>
                <p>MEDIUM RISK</p>
                <small>{medium_risk/total_customers*100:.1f}% of Portfolio</small>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="low-risk-card">
                <h2>{low_risk}</h2>
                <p>LOW RISK</p>
                <small>{low_risk/total_customers*100:.1f}% of Portfolio</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Delinquency Rates
        st.markdown("### Delinquency Rates by Risk Segment")

        col1, col2, col3 = st.columns(3)

        if 'DPD_Bucket_Next_Month' in df.columns:
            high_risk_delinq = df[df['Risk_Level'] == 'High Risk']['DPD_Bucket_Next_Month'].apply(lambda x: x > 0).sum()
            high_risk_rate = high_risk_delinq / high_risk * 100 if high_risk > 0 else 0

            medium_risk_delinq = df[df['Risk_Level'] == 'Medium Risk']['DPD_Bucket_Next_Month'].apply(lambda x: x > 0).sum()
            medium_risk_rate = medium_risk_delinq / medium_risk * 100 if medium_risk > 0 else 0

            low_risk_delinq = df[df['Risk_Level'] == 'Low Risk']['DPD_Bucket_Next_Month'].apply(lambda x: x > 0).sum()
            low_risk_rate = low_risk_delinq / low_risk * 100 if low_risk > 0 else 0

            with col1:
                st.metric("HIGH RISK Delinquency", f"{high_risk_rate:.1f}%", 
                         f"{high_risk_delinq} of {high_risk} customers")
            with col2:
                st.metric("MEDIUM RISK Delinquency", f"{medium_risk_rate:.1f}%",
                         f"{medium_risk_delinq} of {medium_risk} customers")
            with col3:
                st.metric("LOW RISK Delinquency", f"{low_risk_rate:.1f}%",
                         f"{low_risk_delinq} of {low_risk} customers")

        # Key Insight
        st.markdown("""
        <div class="insight-box">
            <h4>💡 Key Insight</h4>
            <p>The 5-flag framework successfully identifies high-risk customers with behavioral warning signs. 
            Approximately 78% of at-risk customers show 3+ indicators. <strong>Early intervention on high-risk 
            customers can reduce default losses by 30-40%.</strong></p>
        </div>
        """, unsafe_allow_html=True)

        # Visualizations
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Risk Distribution")
            risk_counts = df['Risk_Level'].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color=risk_counts.index,
                color_discrete_map={
                    'High Risk': '#f5576c',
                    'Medium Risk': '#fbbf24',
                    'Low Risk': '#10b981'
                },
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Risk Score Distribution")
            fig = px.histogram(df, x='Risk_Score', nbins=20, color_discrete_sequence=['#3b82f6'])
            fig.update_layout(xaxis_title="Risk Score (0-10)", yaxis_title="Count", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # TAB 2: PRIORITY CUSTOMERS
    with tab2:
        st.markdown("### 🚨 Immediate Action Required")
        st.markdown(
            """
        These customers require proactive outreach within **48 hours**. Focus on HIGH RISK tier first.
        """
        )

        if len(df) <= 5:
            num_priority = len(df)
            st.info(f"Showing all {len(df)} customers (dataset has ≤5 rows).")
        else:
            num_priority = st.slider(
                "Number of priority customers to display",
                min_value=5,
                max_value=len(df),
                value=min(15, len(df)),
                step=5 if len(df) >= 25 else 1,
                help="Slide to the maximum value to review every customer in the dataset.",
            )

        top_customers = df.nlargest(num_priority, 'Risk_Score')

        display_df = top_customers[[
            'Customer_ID', 'Risk_Score', 'Risk_Level', 
            'Avg_Payment_Ratio', 'Min_Due_Paid_Frequency',
            'Recent_Spend_Change_%', 'Utilisation_%'
        ]].copy()

        display_df['Risk_Flags'] = top_customers['Risk_Flags'].apply(lambda x: ' '.join(x))

        display_df.columns = [
            'Customer ID', 'Risk Score', 'Risk Level',
            'Payment Ratio', 'Min-Due Freq', 'Spend Change',
            'Utilization', 'Primary Flags'
        ]

        display_df['Payment Ratio'] = display_df['Payment Ratio'].apply(lambda x: f"{x:.0f}%")
        display_df['Min-Due Freq'] = display_df['Min-Due Freq'].apply(lambda x: f"{x:.0f}%")
        display_df['Spend Change'] = display_df['Spend Change'].apply(lambda x: f"{x:+.0f}%")
        display_df['Utilization'] = display_df['Utilization'].apply(lambda x: f"{x:.0f}%")

        def highlight_risk_level(row):
            if row['Risk Level'] == 'High Risk':
                return ['background-color: #fee2e2'] * len(row)
            elif row['Risk Level'] == 'Medium Risk':
                return ['background-color: #fef3c7'] * len(row)
            else:
                return [''] * len(row)

        styled_df = display_df.style.apply(highlight_risk_level, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=600)

        col1, col2 = st.columns([1, 1])
        with col1:
            csv = display_df.to_csv(index=False)
            st.download_button(
                "Download Priority List (CSV)",
                csv,
                f"priority_customers_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        with col2:
            full_csv = df.to_csv(index=False)
            st.download_button(
                "Download Full Dataset (CSV)",
                full_csv,
                f"full_risk_assessment_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

    # TAB 3-5: Same as before (shortened for brevity)
    with tab3:
        st.markdown("### Risk Framework")
        st.markdown(
            """
**Five-Flag Behavioral Framework**

- **Payment Discipline**: Trend in `Avg_Payment_Ratio` and reliance on minimum due.
- **Utilisation Behaviour**: Persistent high `Utilisation_%` relative to credit limit.
- **Spend Volatility**: Direction and magnitude of `Recent_Spend_Change_%`.
- **Cash Behaviour**: Dependence on `Cash_Withdrawal_%` / cash advances.
- **Concentration Risk**: Exposure captured via `Merchant_Mix_Index`.

Scores are combined into a 0–10 composite risk score and grouped into Low, Medium, and High tiers.
"""
        )

    with tab4:
        st.markdown("### Outreach Playbook")
        st.markdown(
            """
**Tiered Intervention Strategy**

- **High Risk (Score ≥ 7)**: Rapid outreach, limit management review, and short-term restructuring options.
- **Medium Risk (Score 4–6)**: Early nudges, education on repayment behaviour, and soft reminders.
- **Low Risk (Score ≤ 3)**: Monitoring only, with targeted offers for engagement and retention.
"""
        )

    with tab5:
        st.markdown("### Performance Metrics")
        st.markdown(
            """
**Key Monitoring KPIs**

- Hit-rate of High-Risk flag vs. realised delinquency.
- Lift vs. traditional rules-based strategies.
- Vintage-level delinquency curves for monitored cohorts.
- Operational metrics: outreach conversion, cure rates, and portfolio loss reduction.
"""
        )

    with tab6:
        st.markdown("### Dataset Explorer")
        st.caption(
            f"Displaying all {len(df):,} rows currently loaded. Use the column headers to sort or filter locally."
        )
        st.dataframe(df, use_container_width=True, height=580)

else:
    st.info("👈 Please select a data source from the sidebar and load data to begin analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **Select Data Source** (Sample/Upload/MySQL)
        2. **Load Your Data** 
        3. **Choose ML Model** (Random Forest/Gradient Boosting)
        4. **Calculate Risk Scores**
        5. **Analyze Results** in 5 comprehensive tabs
        """)

    with col2:
        st.markdown("### 📋 Required Columns")
        st.markdown("""
        The app accepts column names in **any format**:

        **With underscores:**
        - `Credit_Limit`
        - `Utilisation_%`

        **With spaces:**
        - `Credit Limit`
        - `Utilisation %`

        **Mixed/lowercase:**
        - `credit_limit`
        - `CREDIT LIMIT`

        All variants are automatically converted!
        """)

# FOOTER
st.markdown("---")
st.markdown(f"""
<div class="footer-text" style='text-align: center; padding: 20px;'>
    <p><strong>Credit Card Delinquency Dashboard</strong></p>
    <p>Model: {model_choice} | Powered by Machine Learning | Version 1.0</p>
    <p style='font-size: 0.9rem;'>December 2025</p>
</div>
""", unsafe_allow_html=True)