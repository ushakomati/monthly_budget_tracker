import streamlit as st
import sqlite3
import pandas as pd
import calendar
from datetime import datetime
import altair as alt

st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="wide")
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
conn.commit()

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

# --- Initialize session state ---
if "savings_entries" not in st.session_state:
    st.session_state.savings_entries = []
if "expenses_entries" not in st.session_state:
    st.session_state.expenses_entries = []
if "income_val" not in st.session_state:
    st.session_state.income_val = 0.0
if "data_loaded_for" not in st.session_state:
    st.session_state.data_loaded_for = None

# --- Sidebar ---
st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: black; margin-bottom: 0;">💼 Budget Tracker</h1>
        <p style="color: #bdc3c7; font-size: 0.9em; margin-top: 0.5rem;">Track your finances with ease</p>
    </div>
""", unsafe_allow_html=True)

# User information section
st.sidebar.markdown("### 👤 User Information")
user_name = st.sidebar.text_input("Enter your name:", placeholder="e.g., John Doe", help="Enter your name to save and load your budget data")

if user_name:
    st.sidebar.success(f"✅ Welcome, {user_name}!")

# Date selection section
st.sidebar.markdown("### 📅 Select Period")
selected_month = st.sidebar.selectbox("Month:", get_month_options(), help="Choose the month for your budget")
selected_year = st.sidebar.selectbox("Year:", list(range(2020, datetime.now().year + 1)), help="Choose the year for your budget")

# Quick stats in sidebar
if user_name:
    st.sidebar.markdown("### 📊 Quick Stats")
    df = get_user_month_data(user_name, selected_month, selected_year)
    if not df.empty:
        income_total = df[df['type'] == 'Income']['amount'].sum()
        expense_total = df[df['type'] == 'Expense']['amount'].sum()
        savings_total = df[df['type'] == 'Saving']['amount'].sum()
        
        st.sidebar.metric("💰 Income", f"${income_total:,.0f}")
        st.sidebar.metric("💸 Expenses", f"${expense_total:,.0f}")
        st.sidebar.metric("🏦 Savings", f"${savings_total:,.0f}")
        
        if income_total > 0:
            savings_rate = (savings_total / income_total) * 100
            st.sidebar.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
    else:
        st.sidebar.info("No data for selected period")

# Help section
st.sidebar.markdown("### ❓ Quick Help")
with st.sidebar.expander("How to use this app"):
    st.markdown("""
    1. **Enter your name** in the sidebar
    2. **Select month and year** for your budget
    3. **Add Entry tab**: Input your income, savings, and expenses
    4. **Dashboard tab**: View your budget overview and insights
    5. **Reports tab**: Analyze trends over time
    6. **History tab**: Edit or review past entries
    """)

# Tips section
with st.sidebar.expander("💡 Budgeting Tips"):
    st.markdown("""
    - **50/30/20 Rule**: 50% needs, 30% wants, 20% savings
    - **Track every expense** for better insights
    - **Set realistic goals** for savings
    - **Review monthly** to adjust your budget
    - **Use the 'Pull Data' feature** to copy previous month's structure
    """)

# --- Auto-load existing data on user/month/year change ---
if user_name and (st.session_state.data_loaded_for != (user_name, selected_month, selected_year)):
    df = get_user_month_data(user_name, selected_month, selected_year)
    if not df.empty:
        income_rows = df[df['type'] == 'Income']
        st.session_state.income_val = income_rows['amount'].sum() if not income_rows.empty else 0.0
        savings_rows = df[df['type'] == 'Saving']
        st.session_state.savings_entries = [{"sub_category": r['sub_category'], "amount": r['amount']} for _, r in savings_rows.iterrows()]
        expense_rows = df[df['type'] == 'Expense']
        st.session_state.expenses_entries = [{"category": r['category'], "sub_category": r['sub_category'], "amount": r['amount']} for _, r in expense_rows.iterrows()]
    else:
        st.session_state.income_val = 0.0
        st.session_state.savings_entries = []
        st.session_state.expenses_entries = []
    st.session_state.data_loaded_for = (user_name, selected_month, selected_year)

# --- Tabs ---
tabs = st.tabs(["Add Entry", "Dashboard", "Reports", "History"])

# --- Add Entry Tab ---
with tabs[0]:
    st.header("➕ Add New Entry")
    
    # Welcome message and instructions
    if user_name:
        st.info(f"👋 Welcome {user_name}! Add your budget entries for {selected_month} {selected_year}. Use the 'Pull Data' button to copy your previous month's structure.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to start adding entries.")

    # Button to pull previous month data
    if user_name:
        prev_month, prev_year = prev_month_year(selected_month, selected_year)
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"⬇️ Pull Data From Previous Month", help=f"Copy your budget structure from {prev_month} {prev_year}"):
                prev_df = get_user_month_data(user_name, prev_month, prev_year)
                if not prev_df.empty:
                    # Load Income
                    income_rows = prev_df[prev_df['type'] == 'Income']
                    st.session_state.income_val = income_rows['amount'].sum() if not income_rows.empty else 0.0
                    # Load Savings
                    savings_rows = prev_df[prev_df['type'] == 'Saving']
                    st.session_state.savings_entries = [{"sub_category": r['sub_category'], "amount": r['amount']} for _, r in savings_rows.iterrows()]
                    # Load Expenses
                    expense_rows = prev_df[prev_df['type'] == 'Expense']
                    st.session_state.expenses_entries = [{"category": r['category'], "sub_category": r['sub_category'], "amount": r['amount']} for _, r in expense_rows.iterrows()]
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
    
    savings_options = [
        "Mutual Funds", "Stocks", "Fixed Deposits", "Gold",
        "Insurance Premiums", "Emergency Fund", "Other"
    ]

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

    # Display existing expense entries
    if st.session_state.expenses_entries:
        st.markdown("**Current Expense Entries:**")
        
    expenses_to_delete = []
    for i, entry in enumerate(st.session_state.expenses_entries):
        with st.container():
            cols = st.columns([2, 2, 2, 1])
            with cols[0]:
                cat_val = st.selectbox(
                    f"Category {i+1}",
                    list(expense_categories.keys()),
                    index=list(expense_categories.keys()).index(entry.get("category", list(expense_categories.keys())[0])),
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
        if not user_name:
            st.warning("⚠️ Please enter your name to save entries.")
        else:
            # Validation
            if income_val == 0 and not st.session_state.savings_entries and not st.session_state.expenses_entries:
                st.warning("⚠️ Please add at least one entry before saving.")
            else:
                # Remove old records for this user/month/year
                c.execute("DELETE FROM budget WHERE user_name = ? AND month = ? AND year = ?", (user_name, selected_month, selected_year))
                conn.commit()

                if st.session_state.income_val > 0:
                    add_entry(user_name, selected_month, selected_year, "Income", "Salary", "Income", st.session_state.income_val)

                for entry in st.session_state.savings_entries:
                    if entry["sub_category"] and entry["amount"] > 0:
                        add_entry(user_name, selected_month, selected_year, "Savings", entry["sub_category"], "Saving", entry["amount"])

                for entry in st.session_state.expenses_entries:
                    if entry["sub_category"] and entry["amount"] > 0:
                        add_entry(user_name, selected_month, selected_year, entry["category"], entry["sub_category"], "Expense", entry["amount"])

                st.success("✅ All entries saved successfully! Your budget data has been updated.")

# --- Dashboard Tab ---
with tabs[1]:
    st.header("📈 Monthly Overview")
    
    if user_name:
        df = get_user_month_data(user_name, selected_month, selected_year)
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
            
            # Sum amounts by expense categories groupings
            def sum_expense_category(df, cat_name, subcats):
                return df[(df['type'] == 'Expense') & (df['sub_category'].isin(subcats))]['amount'].sum()

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

            essential_exp_subcats = expense_categories["Essential Expenses"]
            emi_subcats = expense_categories["EMIs"]
            lifestyle_subcats = expense_categories["Lifestyle Expenses"]

            essential_sum = sum_expense_category(df, "Essential Expenses", essential_exp_subcats)
            emi_sum = sum_expense_category(df, "EMIs", emi_subcats)
            lifestyle_sum = sum_expense_category(df, "Lifestyle Expenses", lifestyle_subcats)
            investment_sum = savings_total  # Treat all savings as investments
            leftover = income_total - (essential_sum + emi_sum + lifestyle_sum + investment_sum)

            # Percentages safe-guard
            def safe_percent(value, total):
                return (value / total * 100) if total > 0 else 0

            essential_pct = safe_percent(essential_sum, income_total)
            emi_pct = safe_percent(emi_sum, income_total)
            lifestyle_pct = safe_percent(lifestyle_sum, income_total)
            investment_pct = safe_percent(investment_sum, income_total)
            leftover_pct = safe_percent(leftover, income_total)

            # Status messages with better formatting
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

            # Charts Section
            st.markdown("---")
            st.subheader("📊 Visual Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Expense Pie Chart
                expense_pie = df[df['type'] == 'Expense'].groupby('sub_category').amount.sum().reset_index()
                if not expense_pie.empty:
                    pie_chart = alt.Chart(expense_pie).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="amount", type="quantitative"),
                        color=alt.Color(field="sub_category", type="nominal"),
                        tooltip=["sub_category", alt.Tooltip("amount", format=",.0f")]
                    ).properties(title="💡 Expense Breakdown", width=300, height=300)
                    st.altair_chart(pie_chart, use_container_width=True)
                else:
                    st.info("No expense data to display")

            with col2:
                # Savings Bar Chart
                savings_bar = df[df['type'] == 'Saving'].groupby('sub_category').amount.sum().reset_index()
                if not savings_bar.empty:
                    bar_chart = alt.Chart(savings_bar).mark_bar(color="#4CAF50").encode(
                        x=alt.X('sub_category', sort='-y'),
                        y='amount',
                        tooltip=["sub_category", alt.Tooltip("amount", format=",.0f")]
                    ).properties(title="💰 Savings Breakdown", width=300, height=300)
                    st.altair_chart(bar_chart, use_container_width=True)
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
    
    if user_name:
        df = pd.read_sql_query("SELECT * FROM budget WHERE user_name = ?", conn, params=(user_name,))
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
                    ["Line Chart", "Bar Chart", "Table"],
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

            else:
                st.markdown(f"**📊 {vis_type} Visualization**")
                mark = alt.Chart(grouped)

                if vis_type == "Line Chart":
                    chart = mark.mark_line(point=True, strokeWidth=3).encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color=alt.Color('type:N', scale=alt.Scale(range=['#4CAF50', '#e74c3c', '#3498db'])),
                        tooltip=['year', 'period', 'type', alt.Tooltip('amount', format=',.0f')]
                    ).properties(width=700, height=400, title=f"{report_range} Financial Trends")

                else:  # Bar Chart
                    chart = mark.mark_bar().encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color=alt.Color('type:N', scale=alt.Scale(range=['#4CAF50', '#e74c3c', '#3498db'])),
                        tooltip=['year', 'period', 'type', alt.Tooltip('amount', format=',.0f')]
                    ).properties(width=700, height=400, title=f"{report_range} Financial Comparison")

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
                    file_name=f"{user_name}_budget_history.csv",
                    help="Download your complete budget history as a CSV file"
                )
            with col2:
                st.download_button(
                    "📈 Download Summary Report (CSV)", 
                    grouped.to_csv(index=False), 
                    file_name=f"{user_name}_{report_range.lower()}_summary.csv",
                    help="Download the current report summary as a CSV file"
                )
        else:
            st.info("📝 No historical data available. Start by adding entries in the 'Add Entry' tab to generate reports.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to view reports.")

# --- History Tab ---
with tabs[3]:
    st.header("📜 Edit History")
    
    if user_name:
        df_history = pd.read_sql_query("SELECT * FROM budget WHERE user_name = ?", conn, params=(user_name,))
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
                                        (user_name, filter_year, filter_month, filter_type))
                            elif filter_year != "All" and filter_month != "All":
                                # Year and month filter
                                c.execute("DELETE FROM budget WHERE user_name = ? AND year = ? AND month = ?", 
                                        (user_name, filter_year, filter_month))
                            elif filter_year != "All":
                                # Year filter only
                                c.execute("DELETE FROM budget WHERE user_name = ? AND year = ?", (user_name, filter_year))
                            else:
                                # No filters - update all records (be careful!)
                                c.execute("DELETE FROM budget WHERE user_name = ?", (user_name,))
                            
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
                        file_name=f"{user_name}_filtered_history.csv",
                        help="Download the currently filtered data as a CSV file"
                    )
                with col2:
                    st.download_button(
                        "📈 Download Edited Data (CSV)", 
                        edited_df.to_csv(index=False), 
                        file_name=f"{user_name}_edited_data.csv",
                        help="Download the edited data as a CSV file"
                    )
            else:
                st.warning("⚠️ No entries match your current filters. Try adjusting the filter options.")
        else:
            st.info("📝 No history found for this user. Start by adding entries in the 'Add Entry' tab to build your budget history.")
    else:
        st.warning("⚠️ Please enter your name in the sidebar to view or edit history.")
