import streamlit as st
import sqlite3
import pandas as pd
import calendar
from datetime import datetime
import altair as alt
import random
import string
import hashlib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Import configuration
try:
    from config import *
except ImportError:
    # Default configuration if config.py doesn't exist
    VERIFICATION_CODE_EXPIRY = 600
    CODE_LENGTH = 6
    DEVELOPMENT_MODE = True

# Set page config for mobile-friendly layout
st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="wide")

# Add mobile-friendly CSS and viewport meta tag
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    @media (max-width: 600px) {
        html, body, .main, .block-container {
            font-size: 18px !important;
            padding: 0 !important;
        }
        .stButton>button, .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
            font-size: 18px !important;
            width: 100% !important;
            min-height: 48px !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
        .stTabs [data-baseweb="tab"] {
            min-width: 100% !important;
            font-size: 18px !important;
        }
        .metric-container {
            margin: 0.5rem 0 !important;
            padding: 1rem !important;
        }
        .stSidebar, .css-1d391kg {
            width: 100vw !important;
            min-width: 0 !important;
            max-width: 100vw !important;
        }
        .stDataFrame, .stTable {
            font-size: 16px !important;
        }
    }
    /* Make all buttons and inputs full width on mobile */
    .stButton>button, .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        width: 100%;
        box-sizing: border-box;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .main { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .block-container { 
        padding-top: 2rem; 
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem;
    }
    .stButton>button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        font-weight: bold;
        border-radius: 25px;
        padding: 0.6em 1.5em;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #45a049, #4CAF50);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    .remove-button {
        background-color: #e74c3c !important;
        color: white !important;
        font-weight: bold !important;
    }
    .delete-link {
        color: #e74c3c;
        text-decoration: underline;
        cursor: pointer;
        font-size: 0.9em;
        font-weight: bold;
    }
    .delete-link:hover {
        color: #c0392b;
    }
    /* Style for delete buttons to look like hyperlinks */
    .stButton>button:has-text("🗑️ Delete") {
        background: transparent !important;
        color: #e74c3c !important;
        border: 1px solid #e74c3c !important;
        padding: 0.3em 0.8em !important;
        font-size: 0.85em !important;
        text-decoration: none !important;
        box-shadow: none !important;
        border-radius: 15px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:has-text("🗑️ Delete"):hover {
        background: #e74c3c !important;
        color: white !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3) !important;
    }
    /* Enhanced sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        border-radius: 15px;
        margin: 1rem;
        padding: 1rem;
    }
    /* Fix sidebar title color */
    .css-1d391kg h1 {
        color: #000000 !important;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
    }
    .css-1d391kg p {
        color: #333333 !important;
        text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.6);
    }
    /* Better input styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }
    .stNumberInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    .stNumberInput>div>div>input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }
    .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    .stSelectbox>div>div>select:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }
    /* Success and info message styling */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    /* Enhanced tab styling with better spacing */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        padding: 0 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        color: #6c757d;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 12px 20px;
        margin: 0 4px;
        min-width: 120px;
        text-align: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
        border-color: #4CAF50;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        transform: translateY(-2px);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        transform: translateY(-1px);
    }
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# --- Database Setup ---
conn = sqlite3.connect("budget_tracker.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    month TEXT,
    year INTEGER,
    category TEXT,
    sub_category TEXT,
    type TEXT,
    amount REAL,
    created_at TEXT DEFAULT (datetime('now'))
)
''')

# Authentication tables
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    user_name TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    is_verified BOOLEAN DEFAULT 0
)
''')

conn.commit()

# --- Authentication Functions ---
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def register_user(email, password, user_name):
    """Register a new user"""
    try:
        password_hash = hash_password(password)
        c.execute('''
            INSERT INTO users (email, password_hash, user_name)
            VALUES (?, ?, ?)
        ''', (email, password_hash, user_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email, password):
    """Login user and return user data"""
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    
    if user and verify_password(password, user[2]):  # user[2] is password_hash
        return {
            'id': user[0],
            'email': user[1],
            'user_name': user[3]
        }
    return None

# --- Utilities ---
def get_month_options():
    return list(calendar.month_name)[1:]

def get_user_month_data(user_name, month, year):
    return pd.read_sql_query(
        "SELECT * FROM budget WHERE user_name = ? AND month = ? AND year = ?",
        conn, params=(user_name, month, year))

def add_entry(user_name, month, year, category, sub_category, type_, amount):
    c.execute('''
        INSERT INTO budget (user_name, month, year, category, sub_category, type, amount, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (user_name, month, year, category, sub_category, type_, amount))
    conn.commit()

def prev_month_year(month_name, year):
    month_idx = get_month_options().index(month_name)
    if month_idx == 0:
        return get_month_options()[-1], year - 1
    else:
        return get_month_options()[month_idx - 1], year

# --- Helper Functions ---
def sum_expense_category(df, cat_name, subcats):
    return df[(df['type'] == 'Expense') & (df['sub_category'].isin(subcats))]['amount'].sum()

def safe_percent(value, total):
    return (value / total * 100) if total > 0 else 0

def expense_status(name, pct):
    if name == "Essential Expenses":
        if pct <= 30:
            return "✅ Expenses are in line with income"
        else:
            return "⚠️ Try to reduce essential expenses"
    if name == "Lifestyle Expenses":
        if pct <= 10:
            return "✅ Expenses are in line with income"
        else:
            return "⚠️ Lifestyle expenses are high"
    if name == "EMIs":
        if pct <= 15:
            return "✅ Leverage utilization is good"
        else:
            return "⚠️ High EMI burden"
    if name == "Investments/Savings":
        if pct >= 30:
            return "✅ Maintain or increase investments"
        else:
            return "💡 Consider increasing investments"
    if name == "Leftover":
        if pct >= 5:
            return "✅ Good leftover for the month"
        else:
            return "💡 Try to save more or reduce expenses"
    return ""

def normalize_category(category):
    """Normalize category names for backward compatibility"""
    if category == "Fixed Expenses":
        return "Essential Expenses"
    return category

# --- Global Variables ---
# Define expense categories that will be used across multiple tabs
expense_categories = {
    "Essential Expenses": [
        "House Rent & Maintenance", "Property Tax", "Utilities", "Groceries",
        "Medical Expenses", "Children School Fees", "Maid", "Other"
    ],
    "EMIs": [
        "Home Loan EMI", "Car Loan EMI", "Personal Loan EMI", "Other EMIs"
    ],
    "Lifestyle Expenses": [
        "Shopping", "Travel", "Dine & Entertainment", "Other"
    ]
}

# Define savings options that will be used across the application
savings_options = [
    "Mutual Funds", "Stocks", "Fixed Deposits", "Gold",
    "Insurance Premiums", "Emergency Fund", "Other"
]

# --- Initialize session state ---
if "savings_entries" not in st.session_state:
    st.session_state.savings_entries = []
if "expenses_entries" not in st.session_state:
    st.session_state.expenses_entries = []
if "income_val" not in st.session_state:
    st.session_state.income_val = 0.0
if "data_loaded_for" not in st.session_state:
    st.session_state.data_loaded_for = None

# Authentication session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"  # login, register, verify

# --- Authentication Interface ---
if not st.session_state.authenticated:
    # Authentication page
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #2c3e50; margin-bottom: 0;">💼 Budget Tracker</h1>
            <p style="color: #7f8c8d; font-size: 1.1em; margin-top: 0.5rem;">Secure Financial Management</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Authentication tabs
    auth_tabs = st.tabs(["🔐 Login", "📝 Register"])
    
    # --- Login Form ---
    with auth_tabs[0]:
        if st.session_state.get("just_registered"):
            st.success("🎉 Registration successful! Please log in with your new credentials.")
            st.session_state.just_registered = False
        st.subheader("Welcome Back!")
        st.markdown("Sign in to access your budget data.")
        
        with st.form("login_form"):
            login_email = st.text_input("Email Address", placeholder="Enter your email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_submitted = st.form_submit_button("🔐 Login")
            
            if login_submitted:
                login_email_clean = login_email.strip().lower()
                with st.spinner("Authenticating..."):
                    if login_email_clean and login_password:
                        c.execute("SELECT * FROM users WHERE email = ?", (login_email_clean,))
                        user = c.fetchone()
                        if not user:
                            st.error("❌ Email not registered. Please register first.")
                        elif not verify_password(login_password, user[2]):
                            st.error("❌ Incorrect password. Please try again.")
                        else:
                            st.session_state.authenticated = True
                            st.session_state.current_user = {
                                'id': user[0],
                                'email': user[1],
                                'user_name': user[3]
                            }
                            st.success("✅ Login successful! Welcome back!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Please fill in all fields.")
        
        st.markdown("---")
        st.markdown("Don't have an account? Switch to the Register tab to create one.")
    
    # --- Registration Form ---
    with auth_tabs[1]:
        st.subheader("Create New Account")
        st.markdown("Join Budget Tracker to start managing your finances securely.")
        
        with st.form("register_form"):
            reg_email = st.text_input("Email Address", placeholder="Enter your email address")
            reg_name = st.text_input("Full Name", placeholder="Enter your full name")
            reg_password = st.text_input("Password", type="password", placeholder="Create a password")
            reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            register_submitted = st.form_submit_button("📝 Register")
            
            if register_submitted:
                # Normalize email and name
                reg_email_clean = reg_email.strip().lower()
                reg_name_clean = reg_name.strip()
                
                # Password validation
                def is_strong_password(pw):
                    return len(pw) >= 8 and any(c.isdigit() for c in pw) and any(c.isalpha() for c in pw)
                
                with st.spinner("Processing registration..."):
                    if reg_email_clean and reg_name_clean and reg_password and reg_confirm_password:
                        if reg_password == reg_confirm_password:
                            if is_strong_password(reg_password):
                                # Check if email already exists
                                c.execute("SELECT id FROM users WHERE email = ?", (reg_email_clean,))
                                if c.fetchone():
                                    st.error("❌ Email already registered. Please login instead.")
                                else:
                                    if register_user(reg_email_clean, reg_password, reg_name_clean):
                                        st.session_state.just_registered = True
                                        st.session_state.auth_page = "login"
                                        st.experimental_set_query_params(tab=0)
                                        st.rerun()
                                    else:
                                        st.error("❌ Registration failed. Please try again.")
                            else:
                                st.warning("⚠️ Password must be at least 8 characters long and include both letters and numbers.")
                        else:
                            st.warning("⚠️ Passwords do not match.")
                    else:
                        st.warning("⚠️ Please fill in all fields.")
        
        st.markdown("---")
        st.markdown("Already have an account? Switch to the Login tab to sign in.")
    
    st.stop()  # Stop execution here if not authenticated

# --- Modern Flat App Banner and Tabs Styling ---
st.markdown('''
    <style>
    /* Hide the hamburger menu and collapse/expand button so sidebar is always open */
    [data-testid="collapsedControl"], .stSidebar__collapse-button { display: none !important; }
    .css-1d391kg { min-width: 320px !important; max-width: 400px !important; }
    .app-banner {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 56px;
        background: #fff;
        border-bottom: 1.5px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(44,62,80,0.06);
        z-index: 200001;
        display: flex;
        align-items: center;
        font-family: 'Inter', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        padding-left: 2.5rem;
        justify-content: flex-start;
    }
    .app-banner .app-logo {
        width: 30px;
        height: 30px;
        margin-right: 1rem;
    }
    .app-banner .app-title {
        font-size: 1.35rem;
        font-weight: 500;
        color: #222;
        letter-spacing: 1.1px;
    }
    @media (max-width: 600px) {
        .app-banner { height: 44px; padding-left: 1rem; }
        .app-banner .app-logo { width: 22px; height: 22px; }
        .app-banner .app-title { font-size: 1rem; }
    }
    .block-container { margin-top: 70px !important; }
    /* --- Modern Pill Tabs Bar --- */
    .stTabs [data-baseweb="tab-list"] {
        background: #fff;
        border-radius: 32px;
        box-shadow: 0 2px 12px rgba(44,62,80,0.07);
        padding: 0.5rem 1.5rem;
        margin: 0 0 1.5rem 2.5rem;
        display: flex;
        justify-content: flex-start;
        gap: 1.5rem;
        /* border: 1.5px solid #e0e0e0; */
        max-width: 900px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 24px;
        background: #f8fafc;
        color: #388e3c;
        font-weight: 600;
        font-size: 1.13em;
        padding: 0.7em 2.2em;
        margin: 0 2px;
        min-width: 140px;
        text-align: center;
        transition: all 0.2s;
        border: none;
        box-shadow: none;
        position: relative;
        cursor: pointer;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4CAF50 60%, #45a049 100%);
        color: #fff;
        font-weight: 700;
        box-shadow: 0 4px 16px rgba(76,175,80,0.13);
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #e8f5e9;
        color: #2e7d32;
        transform: translateY(-2px) scale(1.04);
    }
    /* Removed green underline under active tab */
    </style>
''', unsafe_allow_html=True)

# User Information Card
st.sidebar.markdown(f'''
    <div style="background: linear-gradient(90deg, #f8fafc 60%, #e3fcec 100%); border-radius: 12px; padding: 1rem 1rem 0.5rem 1rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(76,175,80,0.07);">
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="font-size:1.5em;">👤</span>
            <span style="font-weight:600; color:#222;">{st.session_state.current_user['user_name']}</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.3rem;">
            <span style="font-size:1.2em;">📧</span>
            <span style="color:#4CAF50;">{st.session_state.current_user['email']}</span>
        </div>
    </div>
''', unsafe_allow_html=True)

# Month/Year Selection Card (Squeezed into one row)
st.sidebar.markdown('''
    <div style="background: #f8fafc; border-radius: 12px; padding: 0.7rem 1rem 0.3rem 1rem; margin-bottom: 0.7rem; box-shadow: 0 2px 8px rgba(44,62,80,0.04);">
        <div style="font-weight:600; color:#222; margin-bottom:0.3rem; font-size:1.1em;">📅 Select Month and Year</div>
''', unsafe_allow_html=True)
col1, col2 = st.sidebar.columns(2)
with col1:
    selected_month = st.selectbox("Month:", get_month_options(), index=datetime.now().month-1, key="sidebar_month", help="Choose the month for your budget")
with col2:
    selected_year = st.selectbox("Year:", list(range(2020, datetime.now().year + 1)), index=list(range(2020, datetime.now().year + 1)).index(datetime.now().year), key="sidebar_year", help="Choose the year for your budget")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Quick Stats Card
if st.session_state.current_user:
    st.sidebar.markdown('''
        <div style="background: linear-gradient(90deg, #f8fafc 60%, #e3fcec 100%); border-radius: 12px; padding: 1rem 1rem 0.5rem 1rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(76,175,80,0.07);">
            <div style="font-weight:600; color:#222; margin-bottom:0.5rem; font-size:1.1em;">📊 Quick Stats</div>
    ''', unsafe_allow_html=True)
    df = get_user_month_data(st.session_state.current_user['user_name'], selected_month, selected_year)
    if not df.empty:
        income_total = df[df['type'] == 'Income']['amount'].sum()
        expense_total = df[df['type'] == 'Expense']['amount'].sum()
        savings_total = df[df['type'] == 'Saving']['amount'].sum()
        st.sidebar.markdown(f'''
            <div style="display:flex; flex-direction:column; gap:0.3rem;">
                <div style="background:#e3fcec; border-radius:8px; padding:0.5rem 0.8rem; font-size:1.1em; color:#388e3c; font-weight:600;">💰 Income: ${income_total:,.0f}</div>
                <div style="background:#fce4ec; border-radius:8px; padding:0.5rem 0.8rem; font-size:1.1em; color:#c2185b; font-weight:600;">💸 Expenses: ${expense_total:,.0f}</div>
                <div style="background:#e3f2fd; border-radius:8px; padding:0.5rem 0.8rem; font-size:1.1em; color:#1976d2; font-weight:600;">🏦 Savings: ${savings_total:,.0f}</div>
            </div>
        ''', unsafe_allow_html=True)
        if income_total > 0:
            savings_rate = (savings_total / income_total) * 100
            st.sidebar.markdown(f'<div style="margin-top:0.5rem; color:#4CAF50; font-weight:500;">📈 Savings Rate: {savings_rate:.1f}%</div>', unsafe_allow_html=True)
    else:
        st.sidebar.info("No data for selected period")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# --- Responsive Sidebar: Quick Help and Tips at the Top ---
import streamlit.components.v1 as components

# Use a component to detect screen width and set st.session_state['is_mobile']
components.html('''
<script>
const updateMobileFlag = () => {
  const isMobile = window.innerWidth < 700;
  if (window.parent) {
    window.parent.postMessage({streamlit_setComponentValue: {key: 'is_mobile', value: isMobile}}, '*');
  }
};
window.addEventListener('resize', updateMobileFlag);
updateMobileFlag();
</script>
''', height=0)

if 'is_mobile' not in st.session_state:
    st.session_state.is_mobile = False

# --- Sidebar Content ---
if st.session_state.get('is_mobile', False):
    st.sidebar.markdown("### ❓ Quick Help")
    with st.sidebar.expander("Show Help & Tips", expanded=False):
        st.markdown("""
        1. **Enter your name** in the sidebar
        2. **Select month and year** for your budget
        3. **Add Entry tab**: Input your income, savings, and expenses
        4. **Dashboard tab**: View your budget overview and insights
        5. **Reports tab**: Analyze trends over time
        6. **History tab**: Edit or review past entries
        """)
        st.markdown("---")
        st.markdown("### 💡 Budgeting Tips")
        st.markdown("""
        - **50/30/20 Rule**: 50% needs, 30% wants, 20% savings
        - **Track every expense** for better insights
        - **Set realistic goals** for savings
        - **Review monthly** to adjust your budget
        - **Use the 'Pull Data' feature** to copy previous month's structure
        """)
else:
    st.sidebar.markdown("### ❓ Quick Help")
    with st.sidebar.expander("How to use this app", expanded=False):
        st.markdown("""
        1. **Enter your name** in the sidebar
        2. **Select month and year** for your budget
        3. **Add Entry tab**: Input your income, savings, and expenses
        4. **Dashboard tab**: View your budget overview and insights
        5. **Reports tab**: Analyze trends over time
        6. **History tab**: Edit or review past entries
        """)
    st.sidebar.markdown("### 💡 Budgeting Tips")
    with st.sidebar.expander("Tips", expanded=False):
        st.markdown("""
        - **50/30/20 Rule**: 50% needs, 30% wants, 20% savings
        - **Track every expense** for better insights
        - **Set realistic goals** for savings
        - **Review monthly** to adjust your budget
        - **Use the 'Pull Data' feature** to copy previous month's structure
        """)

# --- Auto-load existing data on user/month/year change ---
if st.session_state.current_user and (st.session_state.data_loaded_for != (st.session_state.current_user['user_name'], selected_month, selected_year)):
    df = get_user_month_data(st.session_state.current_user['user_name'], selected_month, selected_year)
    if not df.empty:
        income_rows = df[df['type'] == 'Income']
        st.session_state.income_val = income_rows['amount'].sum() if not income_rows.empty else 0.0
        savings_rows = df[df['type'] == 'Saving']
        st.session_state.savings_entries = [{"sub_category": r['sub_category'], "amount": r['amount']} for _, r in savings_rows.iterrows()]
        expense_rows = df[df['type'] == 'Expense']
        st.session_state.expenses_entries = [{"category": normalize_category(r['category']), "sub_category": r['sub_category'], "amount": r['amount']} for _, r in expense_rows.iterrows()]
    else:
        st.session_state.income_val = 0.0
        st.session_state.savings_entries = []
        st.session_state.expenses_entries = []
    st.session_state.data_loaded_for = (st.session_state.current_user['user_name'], selected_month, selected_year)

# --- Sidebar Logout Button (Red, Small, Industry Standard) ---
if st.session_state.authenticated:
    st.sidebar.markdown(
        '''
        <style>
        /* Only style the sidebar logout button */
        div[data-testid="stSidebar"] .stButton>button {
            background: #e74c3c !important;
            color: #fff !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 0.4em 1.2em !important;
            font-size: 1em !important;
            min-width: 0 !important;
            min-height: 0 !important;
            box-shadow: 0 2px 8px rgba(231,76,60,0.12) !important;
            transition: background 0.2s, box-shadow 0.2s !important;
            cursor: pointer !important;
            margin-bottom: 1.2em !important;
            margin-top: 0.5em !important;
            display: block !important;
        }
        div[data-testid="stSidebar"] .stButton>button:hover {
            background: #c0392b !important;
            box-shadow: 0 4px 16px rgba(231,76,60,0.18) !important;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )
    if st.sidebar.button("🚪 Logout", key="logout_topright"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.savings_entries = []
        st.session_state.expenses_entries = []
        st.session_state.income_val = 0.0
        st.session_state.data_loaded_for = None
        st.success("✅ Logged out successfully!")
        st.rerun()

# --- Tabs App Name (Main Content) ---
st.markdown("""
    <div style="text-align:left; margin-top:0; margin-bottom:2rem; margin-left:2.5rem;">
        <span style="font-size:2rem; font-weight:700; color:#388e3c; letter-spacing:1px;">
           💼 Monthly Budget Tracker
        </span>
    </div>
""", unsafe_allow_html=True)

# --- Tabs with Icons ---
tabs = st.tabs([
    "➕ Add Entry",
    "📈 Dashboard",
    "📊 Reports",
    "📜 History"
])

# --- Add Entry Tab ---
with tabs[0]:
    st.header("➕ Add New Entry")
    
    # Welcome message and instructions
    if st.session_state.current_user:
        st.info(f"👋 Welcome {st.session_state.current_user['user_name']}! Add your budget entries for {selected_month} {selected_year}. Use the 'Pull Data' button to copy your previous month's structure.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to start adding entries.")

    # Button to pull previous month data
    if st.session_state.current_user:
        prev_month, prev_year = prev_month_year(selected_month, selected_year)
        prev_df = pd.DataFrame()  # Initialize as empty DataFrame
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"⬇️ Pull Data From Previous Month", help=f"Copy your budget structure from {prev_month} {prev_year}"):
                prev_df = get_user_month_data(st.session_state.current_user['user_name'], prev_month, prev_year)
                if not prev_df.empty:
                    # Load Income
                    income_rows = prev_df[prev_df['type'] == 'Income']
                    st.session_state.income_val = income_rows['amount'].sum() if not income_rows.empty else 0.0
                    # Load Savings
                    savings_rows = prev_df[prev_df['type'] == 'Saving']
                    st.session_state.savings_entries = [{"sub_category": r['sub_category'], "amount": r['amount']} for _, r in savings_rows.iterrows()]
                    # Load Expenses
                    expense_rows = prev_df[prev_df['type'] == 'Expense']
                    st.session_state.expenses_entries = [{"category": normalize_category(r['category']), "sub_category": r['sub_category'], "amount": r['amount']} for _, r in expense_rows.iterrows()]
                    st.success(f"✅ Data pulled from {prev_month} {prev_year}. You can edit or add entries now.")
                else:
                    st.info(f"No data found for {prev_month} {prev_year}.")
        with col2:
            st.markdown(f"*This will copy your budget structure from {prev_month} {prev_year} to help you get started quickly.*")

    # Income Section
    st.markdown("---")
    st.subheader("💰 Monthly Income")
    st.markdown("*Enter your total monthly income from all sources*")
    
    income_val = st.number_input(
        "Monthly Income (USD)", 
        min_value=0.0, 
        key="income_val",
        help="Enter your total monthly income including salary, bonuses, side income, etc."
    )
    
    if income_val > 0:
        st.success(f"✅ Income set to ${income_val:,.0f}")

    # Savings Section
    st.markdown("---")
    st.subheader("🏦 Savings & Investments")
    st.markdown("*Track your savings and investment contributions*")
    
    # Display existing savings entries
    if st.session_state.savings_entries:
        st.markdown("**Current Savings Entries:**")

    savings_to_delete = []
    for i, entry in enumerate(st.session_state.savings_entries):
        with st.container():
            cols = st.columns([3, 2, 1])
            with cols[0]:
                selected = st.selectbox(
                    f"Savings Type {i+1}", 
                    savings_options,
                    index=savings_options.index(entry.get("sub_category", savings_options[0])) if entry.get("sub_category") in savings_options else len(savings_options)-1,
                    key=f"savings_type_{i}",
                    help="Select the type of savings or investment"
                )
                if selected == "Other":
                    val = st.text_input(f"Custom Savings Type {i+1}", value=entry.get("sub_category", ""), key=f"custom_savings_{i}")
                    st.session_state.savings_entries[i]["sub_category"] = val
                else:
                    st.session_state.savings_entries[i]["sub_category"] = selected
            with cols[1]:
                amt = st.number_input(
                    f"Amount (USD)", 
                    min_value=0.0, 
                    value=entry.get("amount", 0.0), 
                    key=f"savings_amount_{i}",
                    help="Enter the amount you're saving or investing"
                )
                st.session_state.savings_entries[i]["amount"] = amt
            with cols[2]:
                if st.button("🗑️ Delete", key=f"del_savings_{i}", help="Delete this savings entry"):
                    savings_to_delete.append(i)
    
    if savings_to_delete:
        for i in sorted(savings_to_delete, reverse=True):
            st.session_state.savings_entries.pop(i)
        st.rerun()

    # Add new savings entry
    if st.button("➕ Add Savings Entry", help="Add a new savings or investment entry"):
        st.session_state.savings_entries.append({"sub_category": savings_options[0], "amount": 0.0})
        st.rerun()

    # Show savings summary
    total_savings = sum(entry.get("amount", 0) for entry in st.session_state.savings_entries)
    if total_savings > 0:
        st.info(f"💡 Total Savings: ${total_savings:,.0f}")

    # Expenses Section
    st.markdown("---")
    st.subheader("💸 Expenses")
    st.markdown("*Track your monthly expenses by category*")

    # Display existing expense entries
    if st.session_state.expenses_entries:
        st.markdown("**Current Expense Entries:**")

    expenses_to_delete = []
    for i, entry in enumerate(st.session_state.expenses_entries):
        with st.container():
            cols = st.columns([2, 2, 2, 1])
            with cols[0]:
                # Normalize the category for backward compatibility
                normalized_category = normalize_category(entry.get("category", list(expense_categories.keys())[0]))
                cat_val = st.selectbox(
                    f"Category {i+1}",
                    list(expense_categories.keys()),
                    index=list(expense_categories.keys()).index(normalized_category) if normalized_category in expense_categories else 0,
                    key=f"expense_cat_{i}",
                    help="Select the expense category"
                )
                st.session_state.expenses_entries[i]["category"] = cat_val
            with cols[1]:
                subcats = expense_categories[cat_val]
                subcat_val = entry.get("sub_category", subcats[0])
                idx = subcats.index(subcat_val) if subcat_val in subcats else len(subcats)-1
                selected_subcat = st.selectbox(
                    f"Sub-category {i+1}", 
                    subcats, 
                    index=idx, 
                    key=f"expense_subcat_{i}",
                    help="Select the specific expense type"
                )
                if selected_subcat == "Other":
                    val = st.text_input(f"Custom Sub-category {i+1}", value=subcat_val if selected_subcat == "Other" else "", key=f"custom_expense_{i}")
                    st.session_state.expenses_entries[i]["sub_category"] = val
                else:
                    st.session_state.expenses_entries[i]["sub_category"] = selected_subcat
            with cols[2]:
                amt = st.number_input(
                    f"Amount (USD)", 
                    min_value=0.0, 
                    value=entry.get("amount", 0.0), 
                    key=f"expense_amount_{i}",
                    help="Enter the expense amount"
                )
                st.session_state.expenses_entries[i]["amount"] = amt
            with cols[3]:
                if st.button("🗑️ Delete", key=f"del_expense_{i}", help="Delete this expense entry"):
                    expenses_to_delete.append(i)
    
    if expenses_to_delete:
        for i in sorted(expenses_to_delete, reverse=True):
            st.session_state.expenses_entries.pop(i)
        st.rerun()

    # Add new expense entry
    if st.button("➕ Add Expense Entry", help="Add a new expense entry"):
        first_cat = list(expense_categories.keys())[0]
        st.session_state.expenses_entries.append({"category": first_cat, "sub_category": expense_categories[first_cat][0], "amount": 0.0})
        st.rerun()

    # Show expense summary
    total_expenses = sum(entry.get("amount", 0) for entry in st.session_state.expenses_entries)
    if total_expenses > 0:
        st.info(f"💡 Total Expenses: ${total_expenses:,.0f}")

    # Budget Summary
    if income_val > 0 or total_savings > 0 or total_expenses > 0:
        st.markdown("---")
        st.subheader("📊 Budget Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Income", f"${income_val:,.0f}")
        with col2:
            st.metric("💸 Expenses", f"${total_expenses:,.0f}")
        with col3:
            st.metric("🏦 Savings", f"${total_savings:,.0f}")
        with col4:
            net_amount = income_val - total_expenses - total_savings
            st.metric("📈 Net", f"${net_amount:,.0f}", delta=f"{'Positive' if net_amount >= 0 else 'Negative'}")

    # Save all entries
    st.markdown("---")
    if st.button("💾 Save All Entries", help="Save all your budget entries to the database"):
        if not st.session_state.current_user:
            st.warning("⚠️ Please enter your name to save entries.")
        else:
            # Validation
            if income_val == 0 and not st.session_state.savings_entries and not st.session_state.expenses_entries:
                st.warning("⚠️ Please add at least one entry before saving.")
            else:
                # Remove old records for this user/month/year
                c.execute("DELETE FROM budget WHERE user_name = ? AND month = ? AND year = ?", (st.session_state.current_user['user_name'], selected_month, selected_year))
                conn.commit()

                if st.session_state.income_val > 0:
                    add_entry(st.session_state.current_user['user_name'], selected_month, selected_year, "Income", "Salary", "Income", st.session_state.income_val)

                for entry in st.session_state.savings_entries:
                    if entry["sub_category"] and entry["amount"] > 0:
                        add_entry(st.session_state.current_user['user_name'], selected_month, selected_year, "Savings", entry["sub_category"], "Saving", entry["amount"])

                for entry in st.session_state.expenses_entries:
                    if entry["sub_category"] and entry["amount"] > 0:
                        add_entry(st.session_state.current_user['user_name'], selected_month, selected_year, entry["category"], entry["sub_category"], "Expense", entry["amount"])

                st.success("✅ All entries saved successfully! Your budget data has been updated.")

# --- Dashboard Tab ---
with tabs[1]:
    st.header("📈 Monthly Overview")
    
    if st.session_state.current_user:
        df = get_user_month_data(st.session_state.current_user['user_name'], selected_month, selected_year)
        if not df.empty:
            # Welcome message
            st.success(f"📊 Here's your budget overview for {selected_month} {selected_year}")
            
            # Key Metrics with better styling
            st.subheader("💰 Key Financial Metrics")

            income_total = df[df['type'] == 'Income']['amount'].sum()
            expense_total = df[df['type'] == 'Expense']['amount'].sum()
            savings_total = df[df['type'] == 'Saving']['amount'].sum()
            net_savings = income_total - expense_total

            # Create a more visually appealing metrics display
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">💰 Total Income</div>
                    <div class="metric-value">${income_total:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">💸 Total Expenses</div>
                    <div class="metric-value">${expense_total:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">🏦 Total Savings</div>
                    <div class="metric-value">${savings_total:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                net_color = "#4CAF50" if net_savings >= 0 else "#e74c3c"
                st.markdown(f"""
                <div class="metric-container" style="background: linear-gradient(135deg, {net_color}, {net_color}dd);">
                    <div class="metric-label">📈 Net Savings</div>
                    <div class="metric-value">${net_savings:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            # Savings Rate
            if income_total > 0:
                savings_rate = (savings_total / income_total) * 100
                st.markdown("---")
                st.subheader("📊 Savings Analysis")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Savings Rate", f"{savings_rate:.1f}%", 
                             delta=f"{'Excellent' if savings_rate >= 20 else 'Good' if savings_rate >= 10 else 'Needs Improvement'}")
                with col2:
                    expense_rate = (expense_total / income_total) * 100
                    st.metric("Expense Rate", f"{expense_rate:.1f}%",
                             delta=f"{'Low' if expense_rate <= 70 else 'Moderate' if expense_rate <= 85 else 'High'}")

            # Breakdown by custom categories
            st.markdown("---")
            st.subheader("📋 Budget Breakdown Analysis")

            essential_exp_subcats = expense_categories["Essential Expenses"]
            emi_subcats = expense_categories["EMIs"]
            lifestyle_subcats = expense_categories["Lifestyle Expenses"]

            # Handle both "Essential Expenses" and "Fixed Expenses" for backward compatibility
            essential_sum = sum_expense_category(df, "Essential Expenses", essential_exp_subcats) + sum_expense_category(df, "Fixed Expenses", essential_exp_subcats)
            emi_sum = sum_expense_category(df, "EMIs", emi_subcats)
            lifestyle_sum = sum_expense_category(df, "Lifestyle Expenses", lifestyle_subcats)
            investment_sum = savings_total  # Treat all savings as investments
            leftover = income_total - (essential_sum + emi_sum + lifestyle_sum + investment_sum)

            # Percentages safe-guard
            essential_pct = safe_percent(essential_sum, income_total)
            emi_pct = safe_percent(emi_sum, income_total)
            lifestyle_pct = safe_percent(lifestyle_sum, income_total)
            investment_pct = safe_percent(investment_sum, income_total)
            leftover_pct = safe_percent(leftover, income_total)

            # Status messages with better formatting
            status_msg = expense_status("Essential Expenses", essential_pct)
            st.markdown(f"• **Essential Expenses**: {status_msg}")
            status_msg = expense_status("Lifestyle Expenses", lifestyle_pct)
            st.markdown(f"• **Lifestyle Expenses**: {status_msg}")
            status_msg = expense_status("EMIs", emi_pct)
            st.markdown(f"• **EMIs**: {status_msg}")
            status_msg = expense_status("Investments/Savings", investment_pct)
            st.markdown(f"• **Investments/Savings**: {status_msg}")
            status_msg = expense_status("Leftover", leftover_pct)
            st.markdown(f"• **Leftover**: {status_msg}")

            # Display summary table with better styling
            st.markdown("### Monthly Budget Planning Breakdown")
            
            summary_data = {
                "Category": [
                    "Essential Expenses", "Lifestyle Expenses", "EMIs", "Investments/Savings", "Leftover"
                ],
                "Value (USD)": [
                    essential_sum, lifestyle_sum, emi_sum, investment_sum, leftover
                ],
                "Percentage (%)": [
                    essential_pct, lifestyle_pct, emi_pct, investment_pct, leftover_pct
                ],
                "Status": [
                    expense_status("Essential Expenses", essential_pct),
                    expense_status("Lifestyle Expenses", lifestyle_pct),
                    expense_status("EMIs", emi_pct),
                    expense_status("Investments/Savings", investment_pct),
                    expense_status("Leftover", leftover_pct),
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            
            # Format numbers and percentage for display nicely
            summary_df["Value (USD)"] = summary_df["Value (USD)"].map(lambda x: f"${x:,.0f}")
            summary_df["Percentage (%)"] = summary_df["Percentage (%)"].map(lambda x: f"{x:.1f}%")

            # Display with better styling
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            # --- Improved Visual Analytics Section ---
            st.markdown("---")
            st.subheader("📊 Visual Analytics (Improved)")
            col1, col2 = st.columns(2)
            with col1:
                # Expense Pie Chart (modern palette, tooltips, legend)
                expense_pie = df[df['type'] == 'Expense'].groupby('sub_category').amount.sum().reset_index()
                if not expense_pie.empty:
                    pie_chart = alt.Chart(expense_pie).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="amount", type="quantitative"),
                        color=alt.Color(field="sub_category", type="nominal", scale=alt.Scale(scheme='tableau20')),
                        tooltip=["sub_category", alt.Tooltip("amount", format=",.0f")],
                        order=alt.Order('amount:Q', sort='descending')
                    ).properties(title="💡 Expense Breakdown", width=300, height=300)
                    st.altair_chart(pie_chart, use_container_width=True)
                    # Highlight top expense
                    top_exp = expense_pie.sort_values('amount', ascending=False).iloc[0]
                    st.info(f"🔎 Top Expense: **{top_exp['sub_category']}** (${top_exp['amount']:,.0f})")
                else:
                    st.info("No expense data to display")

            with col2:
                # Savings Trend Bar Chart (modern palette, tooltips, legend)
                savings_bar = df[df['type'] == 'Saving'].groupby('sub_category').amount.sum().reset_index()
                if not savings_bar.empty:
                    bar_chart = alt.Chart(savings_bar).mark_bar(color="#4CAF50").encode(
                        x=alt.X('sub_category', sort='-y'),
                        y='amount',
                        tooltip=["sub_category", alt.Tooltip("amount", format=",.0f")],
                        color=alt.Color('sub_category', scale=alt.Scale(scheme='tableau20'), legend=None)
                    ).properties(title="💰 Savings Breakdown", width=300, height=300)
                    st.altair_chart(bar_chart, use_container_width=True)
                    # Highlight top savings
                    top_save = savings_bar.sort_values('amount', ascending=False).iloc[0]
                    st.info(f"💡 Top Savings: **{top_save['sub_category']}** (${top_save['amount']:,.0f})")
                else:
                    st.info("No savings data to display")

            # Financial Health Score
            st.markdown("---")
            st.subheader("🏥 Financial Health Score")

            # Calculate a simple financial health score
            health_score = 0
            health_factors = []

            if savings_rate >= 20:
                health_score += 25
                health_factors.append("✅ Excellent savings rate (20%+)")
            elif savings_rate >= 10:
                health_score += 15
                health_factors.append("✅ Good savings rate (10-20%)")
            else:
                health_factors.append("⚠️ Low savings rate (<10%)")

            if essential_pct <= 30:
                health_score += 25
                health_factors.append("✅ Essential expenses under control")
            else:
                health_factors.append("⚠️ Essential expenses are high")

            if emi_pct <= 15:
                health_score += 25
                health_factors.append("✅ EMI burden is manageable")
            else:
                health_factors.append("⚠️ EMI burden is high")

            if lifestyle_pct <= 10:
                health_score += 25
                health_factors.append("✅ Lifestyle expenses are reasonable")
            else:
                health_factors.append("⚠️ Lifestyle expenses are high")

            # Display health score
            col1, col2 = st.columns([1, 2])
            with col1:
                if health_score >= 80:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(135deg, #4CAF50, #45a049);">
                        <div class="metric-label">🏆 Financial Health</div>
                        <div class="metric-value">{health_score}/100</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">Excellent!</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif health_score >= 60:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(135deg, #FF9800, #F57C00);">
                        <div class="metric-label">🏆 Financial Health</div>
                        <div class="metric-value">{health_score}/100</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">Good!</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-container" style="background: linear-gradient(135deg, #e74c3c, #c0392b);">
                        <div class="metric-label">🏆 Financial Health</div>
                        <div class="metric-value">{health_score}/100</div>
                        <div style="font-size: 0.9em; opacity: 0.9;">Needs Attention</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("**Health Factors:**")
                for factor in health_factors:
                    st.markdown(f"• {factor}")

                if health_score < 80:
                    st.markdown("**💡 Recommendations:**")
                    if savings_rate < 10:
                        st.markdown("• Consider increasing your savings rate")
                    if essential_pct > 30:
                        st.markdown("• Look for ways to reduce essential expenses")
                    if emi_pct > 15:
                        st.markdown("• Consider debt consolidation or refinancing")
                    if lifestyle_pct > 10:
                        st.markdown("• Review and reduce discretionary spending")
        else:
            st.info("📝 No data available for the selected month. Please add some entries in the 'Add Entry' tab first.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to view your dashboard.")

# --- Reports Tab ---
with tabs[2]:
    st.header("📅 Reports & Analytics")
    
    if st.session_state.current_user:
        df = pd.read_sql_query("SELECT * FROM budget WHERE user_name = ?", conn, params=(st.session_state.current_user['user_name'],))
        if not df.empty:
            st.success(f"📊 Analyzing your financial data across {len(df['month'].unique())} months")
            
            # Report configuration
            st.subheader("📋 Report Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                report_range = st.selectbox(
                    "Select report range:", 
                    ["Monthly", "Quarterly", "Half-Yearly", "Yearly"],
                    help="Choose how to group your data for analysis"
                )
            with col2:
                vis_type = st.selectbox(
                    "Select visualization type:", 
                    ["Line Chart", "Bar Chart", "Stacked Bar", "Area Chart", "Pie Chart", "Table"],
                    help="Choose how to display your data"
                )

            # Preprocess month to number for sorting and grouping
            month_map = {m: i+1 for i, m in enumerate(get_month_options())}
            df['month_num'] = df['month'].map(month_map)

            # Aggregate based on report range
            if report_range == "Monthly":
                grouped = df.groupby(['year', 'month_num', 'type'])['amount'].sum().reset_index()
                grouped['period'] = grouped['month_num'].apply(lambda x: get_month_options()[x-1]) + " " + grouped['year'].astype(str)

            elif report_range == "Quarterly":
                # Compute quarter
                df['quarter'] = ((df['month_num'] - 1) // 3 + 1)
                grouped = df.groupby(['year', 'quarter', 'type'])['amount'].sum().reset_index()
                grouped['period'] = "Q" + grouped['quarter'].astype(str) + " " + grouped['year'].astype(str)

            elif report_range == "Half-Yearly":
                df['half'] = df['month_num'].apply(lambda x: 1 if x <= 6 else 2)
                grouped = df.groupby(['year', 'half', 'type'])['amount'].sum().reset_index()
                grouped['period'] = "H" + grouped['half'].astype(str) + " " + grouped['year'].astype(str)

            else:  # Yearly
                grouped = df.groupby(['year', 'type'])['amount'].sum().reset_index()
                grouped['period'] = grouped['year'].astype(str)

            # Sort periods chronologically
            period_order = grouped['period'].unique().tolist()

            # Display results
            st.markdown("---")
            st.subheader("📈 Financial Trends")

            # Visualization
            if vis_type == "Table":
                st.markdown("**📊 Summary Table**")
                # Pivot table for neat view
                pivot = grouped.pivot_table(index='period', columns='type', values='amount', fill_value=0).reset_index()
                # Format numbers for display
                num_cols = [col for col in pivot.columns if col != 'period']
                st.dataframe(pivot.style.format({col: "{:,.0f}" for col in num_cols}), use_container_width=True, hide_index=True)

            elif vis_type == "Pie Chart":
                st.markdown("**📊 Pie Chart Visualization**")
                pie_data = grouped.groupby('type')['amount'].sum().reset_index()
                pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="amount", type="quantitative"),
                    color=alt.Color(field="type", type="nominal", scale=alt.Scale(scheme='tableau20')),
                    tooltip=["type", alt.Tooltip("amount", format=",.0f")],
                    order=alt.Order('amount:Q', sort='descending')
                ).properties(title="💡 Type Breakdown", width=350, height=350)
                st.altair_chart(pie_chart, use_container_width=True)

            else:
                st.markdown(f"**📊 {vis_type} Visualization**")
                mark = alt.Chart(grouped)

                if vis_type == "Line Chart":
                    chart = mark.mark_line(point=True, strokeWidth=3).encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color=alt.Color('type:N', scale=alt.Scale(scheme='tableau20')),
                        tooltip=['year', 'period', 'type', alt.Tooltip('amount', format=',.0f')]
                    ).properties(width=700, height=400, title=f"{report_range} Financial Trends")

                elif vis_type == "Bar Chart":
                    chart = mark.mark_bar().encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color=alt.Color('type:N', scale=alt.Scale(scheme='tableau20')),
                        tooltip=['year', 'period', 'type', alt.Tooltip('amount', format=',.0f')]
                    ).properties(width=700, height=400, title=f"{report_range} Financial Comparison")

                elif vis_type == "Stacked Bar":
                    chart = mark.mark_bar().encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color=alt.Color('type:N', scale=alt.Scale(scheme='tableau20')),
                        tooltip=['year', 'period', 'type', alt.Tooltip('amount', format=',.0f')],
                        order=alt.Order('type:N')
                    ).properties(width=700, height=400, title=f"{report_range} Stacked Financial Comparison")

                elif vis_type == "Area Chart":
                    chart = mark.mark_area(opacity=0.7).encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color=alt.Color('type:N', scale=alt.Scale(scheme='tableau20')),
                        tooltip=['year', 'period', 'type', alt.Tooltip('amount', format=',.0f')]
                    ).properties(width=700, height=400, title=f"{report_range} Area Chart")

                st.altair_chart(chart, use_container_width=True)

            # Key Insights
            st.markdown("---")
            st.subheader("💡 Key Insights")
            
            # Calculate insights
            total_income = df[df['type'] == 'Income']['amount'].sum()
            total_expenses = df[df['type'] == 'Expense']['amount'].sum()
            total_savings = df[df['type'] == 'Saving']['amount'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Income", f"${total_income:,.0f}")
            with col2:
                st.metric("Total Expenses", f"${total_expenses:,.0f}")
            with col3:
                st.metric("Total Savings", f"${total_savings:,.0f}")
            
            # Trend analysis
            if len(df['month'].unique()) > 1:
                st.markdown("**📈 Trend Analysis:**")
                
                # Income trend
                income_trend = df[df['type'] == 'Income'].groupby(['year', 'month_num'])['amount'].sum().reset_index()
                if len(income_trend) > 1:
                    income_growth = ((income_trend['amount'].iloc[-1] - income_trend['amount'].iloc[0]) / income_trend['amount'].iloc[0]) * 100
                    st.markdown(f"• **Income Trend**: {'📈 Increasing' if income_growth > 0 else '📉 Decreasing'} by {abs(income_growth):.1f}%")
                
                # Savings trend
                savings_trend = df[df['type'] == 'Saving'].groupby(['year', 'month_num'])['amount'].sum().reset_index()
                if len(savings_trend) > 1:
                    savings_growth = ((savings_trend['amount'].iloc[-1] - savings_trend['amount'].iloc[0]) / savings_trend['amount'].iloc[0]) * 100 if savings_trend['amount'].iloc[0] > 0 else 0
                    st.markdown(f"• **Savings Trend**: {'📈 Increasing' if savings_growth > 0 else '📉 Decreasing'} by {abs(savings_growth):.1f}%")

            # Download section
            st.markdown("---")
            st.subheader("📥 Export Data")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📊 Download Full History (CSV)", 
                    df.to_csv(index=False), 
                    file_name=f"{st.session_state.current_user['user_name']}_budget_history.csv",
                    help="Download your complete budget history as a CSV file"
                )
            with col2:
                st.download_button(
                    "📈 Download Summary Report (CSV)", 
                    grouped.to_csv(index=False), 
                    file_name=f"{st.session_state.current_user['user_name']}_{report_range.lower()}_summary.csv",
                    help="Download the current report summary as a CSV file"
                )
        else:
            st.info("📝 No historical data available. Start by adding entries in the 'Add Entry' tab to generate reports.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to view reports.")

# --- History Tab ---
with tabs[3]:
    st.header("📜 Edit History")
    
    if st.session_state.current_user:
        df_history = pd.read_sql_query("SELECT * FROM budget WHERE user_name = ?", conn, params=(st.session_state.current_user['user_name'],))
        if not df_history.empty:
            st.success(f"📊 Found {len(df_history)} entries in your budget history")
            
            # Summary stats
            st.subheader("📋 History Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Entries", len(df_history))
            with col2:
                st.metric("Months Tracked", len(df_history[['month', 'year']].drop_duplicates()))
            with col3:
                st.metric("Years Tracked", len(df_history['year'].unique()))
            with col4:
                st.metric("Total Amount", f"${df_history['amount'].sum():,.0f}")
            
            # Instructions
            st.info("💡 **Instructions**: You can edit any values in the table below. Click 'Save Changes' to update your budget history.")
            
            # Filter options
            st.subheader("🔍 Filter Options")
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_year = st.selectbox("Filter by Year:", ["All"] + sorted(df_history['year'].unique().tolist()))
            with col2:
                filter_month = st.selectbox("Filter by Month:", ["All"] + get_month_options())
            with col3:
                filter_type = st.selectbox("Filter by Type:", ["All"] + sorted(df_history['type'].unique().tolist()))
            
            # Apply filters
            filtered_df = df_history.copy()
            if filter_year != "All":
                filtered_df = filtered_df[filtered_df['year'] == filter_year]
            if filter_month != "All":
                filtered_df = filtered_df[filtered_df['month'] == filter_month]
            if filter_type != "All":
                filtered_df = filtered_df[filtered_df['type'] == filter_type]
            
            if not filtered_df.empty:
                st.markdown(f"**📊 Showing {len(filtered_df)} filtered entries**")
                
                # Prepare data for editing (remove system columns)
                edit_df = filtered_df.drop(columns=['id', 'created_at']).copy()
                
                # Edit the data
                edited_df = st.data_editor(
                    edit_df, 
                    use_container_width=True, 
                    num_rows="dynamic",
                    column_config={
                        "user_name": st.column_config.TextColumn("User Name", disabled=True),
                        "month": st.column_config.SelectboxColumn("Month", options=get_month_options()),
                        "year": st.column_config.NumberColumn("Year", min_value=2020, max_value=datetime.now().year + 10),
                        "category": st.column_config.TextColumn("Category"),
                        "sub_category": st.column_config.TextColumn("Sub Category"),
                        "type": st.column_config.SelectboxColumn("Type", options=["Income", "Expense", "Saving"]),
                        "amount": st.column_config.NumberColumn("Amount (USD)", min_value=0.0, format="%.0f")
                    }
                )
                
                # Save changes
                st.markdown("---")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("💾 Save Changes", help="Save all changes to your budget history"):
                        try:
                            # Remove old records for the filtered data
                            if filter_year != "All" and filter_month != "All" and filter_type != "All":
                                # Specific filter - only update those records
                                c.execute("DELETE FROM budget WHERE user_name = ? AND year = ? AND month = ? AND type = ?", 
                                        (st.session_state.current_user['user_name'], filter_year, filter_month, filter_type))
                            elif filter_year != "All" and filter_month != "All":
                                # Year and month filter
                                c.execute("DELETE FROM budget WHERE user_name = ? AND year = ? AND month = ?", 
                                        (st.session_state.current_user['user_name'], filter_year, filter_month))
                            elif filter_year != "All":
                                # Year filter only
                                c.execute("DELETE FROM budget WHERE user_name = ? AND year = ?", (st.session_state.current_user['user_name'], filter_year))
                            else:
                                # No filters - update all records (be careful!)
                                c.execute("DELETE FROM budget WHERE user_name = ?", (st.session_state.current_user['user_name'],))
                            conn.commit()

                            # Add the edited records
                            for _, row in edited_df.iterrows():
                                add_entry(row['user_name'], row['month'], row['year'], 
                                        row['category'], row['sub_category'], row['type'], row['amount'])

                            st.success("✅ History updated successfully! Your changes have been saved.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error saving changes: {str(e)}")

                with col2:
                    st.markdown("*⚠️ **Warning**: Saving changes will permanently update your budget history. Make sure your changes are correct before saving.*")
                
                # Export filtered data
                st.markdown("---")
                st.subheader("📥 Export Filtered Data")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📊 Download Filtered Data (CSV)", 
                        filtered_df.to_csv(index=False), 
                        file_name=f"{st.session_state.current_user['user_name']}_filtered_history.csv",
                        help="Download the currently filtered data as a CSV file"
                    )
                with col2:
                    st.download_button(
                        "📈 Download Edited Data (CSV)", 
                        edited_df.to_csv(index=False), 
                        file_name=f"{st.session_state.current_user['user_name']}_edited_data.csv",
                        help="Download the edited data as a CSV file"
                    )
        else:
            st.warning("⚠️ No entries match your current filters. Try adjusting the filter options.")
    elif not df_history.empty:
        st.info("📝 No history found for this user. Start by adding entries in the 'Add Entry' tab to build your budget history.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to view or edit history.")
