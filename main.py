import streamlit as st
import sqlite3
import pandas as pd
import calendar
from datetime import datetime
import altair as alt

st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f4f4f8; }
    .block-container { padding-top: 2rem; }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.4em 1em;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .remove-button {
        background-color: #e74c3c !important;
        color: white !important;
        font-weight: bold !important;
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
st.sidebar.title("💼 Budget Tracker")
user_name = st.sidebar.text_input("Enter your name:")
selected_month = st.sidebar.selectbox("Select month:", get_month_options())
selected_year = st.sidebar.selectbox("Select year:", list(range(2020, datetime.now().year + 1)))

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

    # Button to pull previous month data
    if user_name:
        prev_month, prev_year = prev_month_year(selected_month, selected_year)
        if st.button(f"⬇️ Pull Data From Previous Month ({prev_month} {prev_year})"):
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

    # Income
    income_val = st.number_input("Monthly Income (USD)", min_value=0.0, format="%.2f", key="income_val")

    # Savings
    st.subheader("🏦 Add Savings")
    savings_options = ["Stocks", "FDs", "Mutual Funds", "Gold", "Other"]

    savings_to_delete = []
    for i, entry in enumerate(st.session_state.savings_entries):
        cols = st.columns([3, 2, 1])
        with cols[0]:
            selected = st.selectbox(
                f"Savings Type {i+1}", savings_options,
                index=savings_options.index(entry.get("sub_category", "Stocks")) if entry.get("sub_category") in savings_options else len(savings_options)-1,
                key=f"savings_type_{i}"
            )
            if selected == "Other":
                val = st.text_input(f"Custom Savings Type {i+1}", value=entry.get("sub_category", ""), key=f"custom_savings_{i}")
                st.session_state.savings_entries[i]["sub_category"] = val
            else:
                st.session_state.savings_entries[i]["sub_category"] = selected
        with cols[1]:
            amt = st.number_input(f"Amount (USD)", min_value=0.0, format="%.2f", value=entry.get("amount", 0.0), key=f"savings_amount_{i}")
            st.session_state.savings_entries[i]["amount"] = amt
        with cols[2]:
            if st.button("❌", key=f"del_savings_{i}"):
                savings_to_delete.append(i)
    if savings_to_delete:
        for i in sorted(savings_to_delete, reverse=True):
            st.session_state.savings_entries.pop(i)

    if st.button("➕ Add Saving"):
        st.session_state.savings_entries.append({"sub_category": "", "amount": 0.0})

    # Expenses
    st.subheader("💸 Add Expenses")
    expense_categories = {
        "Fixed Expenses": ["Rent", "WiFi", "Groceries", "Travel", "Other"],
        "Entertainment": ["Movies", "Shopping", "Vacation", "Restaurants", "Other"]
    }

    expenses_to_delete = []
    for i, entry in enumerate(st.session_state.expenses_entries):
        cols = st.columns([2, 2, 2, 1])
        with cols[0]:
            cat_val = st.selectbox(
                f"Category {i+1}",
                list(expense_categories.keys()),
                index=list(expense_categories.keys()).index(entry.get("category", "Fixed Expenses")),
                key=f"expense_cat_{i}"
            )
            st.session_state.expenses_entries[i]["category"] = cat_val
        with cols[1]:
            subcats = expense_categories[cat_val]
            subcat_val = entry.get("sub_category", "")
            idx = subcats.index(subcat_val) if subcat_val in subcats else len(subcats)-1
            selected_subcat = st.selectbox(f"Sub-category {i+1}", subcats, index=idx, key=f"expense_subcat_{i}")
            if selected_subcat == "Other":
                val = st.text_input(f"Custom Sub-category {i+1}", value=subcat_val if selected_subcat == "Other" else "", key=f"custom_expense_{i}")
                st.session_state.expenses_entries[i]["sub_category"] = val
            else:
                st.session_state.expenses_entries[i]["sub_category"] = selected_subcat
        with cols[2]:
            amt = st.number_input(f"Amount (USD)", min_value=0.0, format="%.2f", value=entry.get("amount", 0.0), key=f"expense_amount_{i}")
            st.session_state.expenses_entries[i]["amount"] = amt
        with cols[3]:
            if st.button("❌", key=f"del_expense_{i}"):
                expenses_to_delete.append(i)
    if expenses_to_delete:
        for i in sorted(expenses_to_delete, reverse=True):
            st.session_state.expenses_entries.pop(i)

    if st.button("➕ Add Expense"):
        st.session_state.expenses_entries.append({"category": "Fixed Expenses", "sub_category": "", "amount": 0.0})

    # Save all entries
    if st.button("💾 Save All Entries"):
        if not user_name:
            st.warning("⚠️ Please enter your name to save entries.")
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

            st.success("✅ All entries saved successfully!")

# --- Dashboard Tab ---
with tabs[1]:
    st.header("📈 Monthly Overview")
    if user_name:
        df = get_user_month_data(user_name, selected_month, selected_year)
        if not df.empty:
            st.subheader(f"Summary for {selected_month} {selected_year}")

            income_total = df[df['type'] == 'Income']['amount'].sum()
            expense_total = df[df['type'] == 'Expense']['amount'].sum()
            savings_total = df[df['type'] == 'Saving']['amount'].sum()
            net_savings = income_total - expense_total

            st.metric("Total Income (USD)", f"${income_total:,.2f}")
            st.metric("Total Expenses (USD)", f"${expense_total:,.2f}")
            st.metric("Total Savings (USD)", f"${savings_total:,.2f}")
            st.metric("Net Savings (USD)", f"${net_savings:,.2f}")

            # Expense Pie Chart
            expense_pie = df[df['type'] == 'Expense'].groupby('sub_category').amount.sum().reset_index()
            pie_chart = alt.Chart(expense_pie).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="amount", type="quantitative"),
                color=alt.Color(field="sub_category", type="nominal"),
                tooltip=["sub_category", "amount"]
            )
            st.subheader("💡 Expense Breakdown")
            st.altair_chart(pie_chart, use_container_width=True)

            # Savings Bar Chart
            savings_bar = df[df['type'] == 'Saving'].groupby('sub_category').amount.sum().reset_index()
            bar_chart = alt.Chart(savings_bar).mark_bar(color="#4CAF50").encode(
                x=alt.X('sub_category', sort='-y'),
                y='amount',
                tooltip=["sub_category", "amount"]
            )
            st.subheader("💰 Savings Breakdown")
            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info("No data for selected month.")
    else:
        st.warning("Please enter your name in the sidebar.")

# --- Reports Tab ---
with tabs[2]:
    st.header("📅 Reports & History")
    if user_name:
        df = pd.read_sql_query("SELECT * FROM budget WHERE user_name = ?", conn, params=(user_name,))
        if not df.empty:
            # --- Select report range ---
            report_range = st.selectbox("Select report range:", ["Monthly", "Quarterly", "Half-Yearly", "Yearly"])

            # --- Select visualization type ---
            vis_type = st.selectbox("Select visualization type:", ["Line Chart", "Bar Chart", "Table"])

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

            # Visualization
            if vis_type == "Table":
                # Pivot table for neat view
                pivot = grouped.pivot_table(index='period', columns='type', values='amount', fill_value=0).reset_index()
                # Format numbers for display
                num_cols = [col for col in pivot.columns if col != 'period']
                st.dataframe(pivot.style.format({col: "{:,.2f}" for col in num_cols}))

            else:
                mark = alt.Chart(grouped)

                if vis_type == "Line Chart":
                    chart = mark.mark_line(point=True).encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color='type:N',
                        tooltip=['year', 'period', 'type', 'amount']
                    ).properties(width=700, height=400)

                else:  # Bar Chart
                    chart = mark.mark_bar().encode(
                        x=alt.X('period:N', sort=period_order, title='Period'),
                        y=alt.Y('amount:Q', title='Amount (USD)'),
                        color='type:N',
                        tooltip=['year', 'period', 'type', 'amount']
                    ).properties(width=700, height=400)

                st.altair_chart(chart, use_container_width=True)

            st.download_button("📥 Download Full History (CSV)", df.to_csv(index=False), file_name=f"{user_name}_full_history.csv")
        else:
            st.info("No historical data available.")
    else:
        st.warning("Please enter your name in the sidebar.")
        
# --- History Tab ---
with tabs[3]:
    st.header("📜 Editable History")
    if user_name:
        df_history = pd.read_sql_query("SELECT * FROM budget WHERE user_name = ?", conn, params=(user_name,))
        if not df_history.empty:
            edited_df = st.data_editor(df_history.drop(columns=['id', 'created_at']), use_container_width=True, num_rows="dynamic")
            if st.button("💾 Save Changes to History"):
                c.execute("DELETE FROM budget WHERE user_name = ?", (user_name,))
                conn.commit()
                for _, row in edited_df.iterrows():
                    add_entry(row['user_name'], row['month'], row['year'], row['category'], row['sub_category'], row['type'], row['amount'])
                st.success("✅ History updated successfully!")
        else:
            st.info("No history found for this user.")
    else:
        st.warning("⚠️ Please enter your name to view or edit history.")
