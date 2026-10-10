import streamlit as st
import pandas as pd
from datetime import datetime
import os

import database as db
import components as comp

st.set_page_config(page_title="Smart Expense Tracker", page_icon="💰", layout="wide")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

db.init_db()
currency = db.get_settings()

def main():
    st.sidebar.title("💰 Smart Expense Tracker")
    menu = ["Dashboard", "Add Transaction", "Manage Transactions", "Budgets", "Reports", "Settings"]
    choice = st.sidebar.radio("Navigation", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.info("A smart and simple way to manage your personal finances.")
  
    if choice == "Dashboard":
        render_dashboard()
    elif choice == "Add Transaction":
        render_add_transaction()
    elif choice == "Manage Transactions":
        render_manage_transactions()
    elif choice == "Budgets":
        render_budgets()
    elif choice == "Reports":
        render_reports()
    elif choice == "Settings":
        render_settings()

def render_dashboard():
    st.title("Dashboard")
    df = db.get_transactions()
    
    if df.empty:
        st.info("Welcome! You have no transactions yet. Go to 'Add Transaction' to get started.")
        return
        
    inc = df[df['type'] == 'Income']['amount'].sum()
    exp = df[df['type'] == 'Expense']['amount'].sum()
    bal = inc - exp
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.container(border=True).metric("Total Income", f"{currency}{inc:,.2f}")
    with col2:
        st.container(border=True).metric("Total Expenses", f"{currency}{exp:,.2f}")
    with col3:
        st.container(border=True).metric("Current Balance", f"{currency}{bal:,.2f}")
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig1 = comp.plot_income_vs_expense(df, currency)
        if fig1: st.plotly_chart(fig1, use_container_width=True)
    with col_chart2:
        fig2 = comp.plot_category_breakdown(df, currency)
        if fig2: st.plotly_chart(fig2, use_container_width=True)
        
    fig3 = comp.plot_monthly_spending(df, currency)
    if fig3: st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("Recent Transactions")
    recent = df.head(5)[['date', 'description', 'category', 'type', 'amount']]
    st.dataframe(recent, hide_index=True, use_container_width=True)

def render_add_transaction():
    st.title("Add Transaction")
    
    tx_type = st.radio("Transaction Type", ["Expense", "Income"], horizontal=True)
    
    with st.form("add_tx_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        amount = col1.number_input("Amount", min_value=0.00, step=10.0, format="%.2f")
        
        if tx_type == "Expense":
            categories = ["Food & Dining", "Transportation", "Housing", "Utilities", "Shopping", "Entertainment", "Healthcare", "Personal Care", "Education", "Other"]
        else:
            categories = ["Salary", "Business", "Investments", "Gifts", "Other"]
            
        category = col2.selectbox("Category", categories)
        date = col1.date_input("Date")
        payment_method = col2.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "UPI/Wallet", "Other"])
        description = st.text_input("Description / Notes")
        
        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            if amount > 0:
                db.add_transaction(tx_type, amount, category, description, date.strftime("%Y-%m-%d"), payment_method)
                st.success("Transaction added successfully!")
            else:
                st.error("Amount must be greater than 0.")

def render_manage_transactions():
    st.title("Manage Transactions")
    df = db.get_transactions()
    
    if df.empty:
        st.info("No transactions found.")
        return
        
    st.subheader("Filter & Search")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        search = col1.text_input("Search by description", placeholder="e.g. Groceries")
        f_type = col2.selectbox("Filter by Type", ["All", "Income", "Expense"])
        sort_by = col3.selectbox("Sort by", ["Date (Newest First)", "Date (Oldest First)", "Amount (Highest)", "Amount (Lowest)"])
    
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['description'].str.contains(search, case=False, na=False)]
    if f_type != "All":
        filtered_df = filtered_df[filtered_df['type'] == f_type]
        
    if sort_by == "Date (Newest First)":
        filtered_df = filtered_df.sort_values(by='date', ascending=False)
    elif sort_by == "Date (Oldest First)":
        filtered_df = filtered_df.sort_values(by='date', ascending=True)
    elif sort_by == "Amount (Highest)":
        filtered_df = filtered_df.sort_values(by='amount', ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by='amount', ascending=True)
        
    st.dataframe(filtered_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Edit or Delete a Transaction")
    if not filtered_df.empty:
        tx_id = st.selectbox("Select Transaction ID to manage", filtered_df['id'].tolist())
        if tx_id:
            tx = filtered_df[filtered_df['id'] == tx_id].iloc[0]
            
            with st.expander("Edit Transaction", expanded=False):
                with st.form("edit_form"):
                    e_type = st.selectbox("Type", ["Expense", "Income"], index=0 if tx['type']=="Expense" else 1)
                    e_amount = st.number_input("Amount", value=float(tx['amount']), min_value=0.01)
                    e_category = st.text_input("Category", value=tx['category'])
                    e_desc = st.text_input("Description", value=tx['description'] if pd.notnull(tx['description']) else "")
                    e_date = st.date_input("Date", value=datetime.strptime(tx['date'], "%Y-%m-%d"))
                    e_pay = st.text_input("Payment Method", value=tx['payment_method'] if pd.notnull(tx['payment_method']) else "")
                    
                    if st.form_submit_button("Update Transaction"):
                        db.update_transaction(tx_id, e_type, e_amount, e_category, e_desc, e_date.strftime("%Y-%m-%d"), e_pay)
                        st.success("Transaction updated successfully!")
                        st.rerun()
      
            st.button("Delete Transaction", type="primary", key="del_btn", on_click=delete_tx_callback, args=(tx_id,))

def delete_tx_callback(tx_id):
    db.delete_transaction(tx_id)
    st.session_state.tx_deleted = True

if 'tx_deleted' in st.session_state and st.session_state.tx_deleted:
    st.success("Transaction deleted successfully!")
    st.session_state.tx_deleted = False

def render_budgets():
    st.title("Budget Management")
    current_month = datetime.now().strftime('%Y-%m')
    st.write(f"**Budget for:** {datetime.now().strftime('%B %Y')}")
    
    with st.container(border=True):
        st.subheader("Set a Budget")
        with st.form("budget_form"):
            col1, col2 = st.columns(2)
            cat = col1.selectbox("Category", ["Total", "Food & Dining", "Transportation", "Housing", "Utilities", "Shopping", "Entertainment", "Healthcare", "Personal Care", "Education", "Other"])
            amt = col2.number_input("Monthly Budget Amount", min_value=1.0, step=100.0)
            if st.form_submit_button("Save Budget"):
                db.set_budget(cat, amt, current_month)
                st.success(f"Budget for '{cat}' saved!")
                st.rerun()
                
    st.subheader("Budget Progress")
    budgets = db.get_budgets()
    df = db.get_transactions()
    
    if not budgets.empty:
        month_budgets = budgets[budgets['month_year'] == current_month]
        if month_budgets.empty:
            st.info("No budgets set for this month.")
        else:
            expenses = df[(df['type'] == 'Expense') & (df['date'].str.startswith(current_month))]
            for _, row in month_budgets.iterrows():
                b_id = row['id']
                cat = row['category']
                b_amt = row['amount']
                
                if cat == "Total":
                    used = expenses['amount'].sum()
                else:
                    used = expenses[expenses['category'] == cat]['amount'].sum()
                    
                progress = min(used / b_amt, 1.0) if b_amt > 0 else 0
                
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{cat}** (Budget limit: {currency}{b_amt:,.2f})")
                        st.progress(progress)
                        st.caption(f"Used: {currency}{used:,.2f} | Remaining: {currency}{(b_amt - used):,.2f} ({progress*100:.1f}%)")
                        
                        if progress >= 1.0:
                            st.error("Budget exceeded!")
                        elif progress >= 0.8:
                            st.warning("Approaching limit!")
                            
                    with col2:
                        st.write("") # Spacer
                        if st.button("Delete", key=f"del_b_{b_id}"):
                            db.delete_budget(b_id)
                            st.rerun()
    else:
        st.info("No budgets set. Create one above.")

def render_reports():
    st.title("Reports & Insights")
    df = db.get_transactions()
    if df.empty:
        st.info("Need more transactions to generate reports.")
        return
        
    st.subheader("Monthly Income vs Expense Summary")
    df['month'] = df['date'].str[:7]
    monthly_summary = df.pivot_table(index='month', columns='type', values='amount', aggfunc='sum', fill_value=0).reset_index()
    if 'Income' not in monthly_summary.columns: monthly_summary['Income'] = 0
    if 'Expense' not in monthly_summary.columns: monthly_summary['Expense'] = 0
    monthly_summary['Net Savings'] = monthly_summary['Income'] - monthly_summary['Expense']
    
    st.dataframe(monthly_summary, use_container_width=True, hide_index=True)
    
    st.subheader("Highest Spending Categories")
    expenses = df[df['type'] == 'Expense']
    if not expenses.empty:
        cat_exp = expenses.groupby('category')['amount'].sum().sort_values(ascending=False).reset_index()
        st.dataframe(cat_exp, use_container_width=True, hide_index=True)
        
    st.markdown("---")
    st.subheader("Export Data")
    st.write("Download your complete transaction history as a CSV file.")
    csv = df.drop(columns=['month'], errors='ignore').to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "transactions.csv", "text/csv")

def render_settings():
    st.title("Settings")
    
    with st.container(border=True):
        st.subheader("Preferences")
        curr = db.get_settings()
        new_curr = st.text_input("Preferred Currency Symbol", value=curr)
        if st.button("Save Preferences"):
            db.update_settings(new_curr)
            st.success("Preferences updated!")
            st.rerun()
            
    with st.container(border=True):
        st.subheader("App Theme")
        st.write("Toggle the theme for the application.")
        theme = st.selectbox("Select Theme", ["dark", "light"], index=0)
        if st.button("Apply Theme"):
            config_dir = ".streamlit"
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "config.toml")
            content = ""
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    lines = f.readlines()
                    content = "".join([l for l in lines if not l.startswith("[theme]") and "base=" not in l and "primaryColor=" not in l])
            
            with open(config_path, "w") as f:
                f.write(content)
                f.write("\n[theme]\n")
                f.write(f'base="{theme}"\n')
                f.write('primaryColor="#3b82f6"\n')
                
            st.success(f"{theme.capitalize()} theme applied! Please refresh the page in your browser to see changes.")
            
    with st.container(border=True):
        st.subheader("Danger Zone")
        st.warning("Deleting data cannot be undone.")
        if st.button("Clear All Data", type="primary"):
            st.session_state.confirm_clear = True
            
        if st.session_state.get('confirm_clear', False):
            st.error("Are you sure? This will delete ALL transactions and budgets.")
            col1, col2 = st.columns(2)
            if col1.button("Yes, delete everything"):
                db.clear_all_data()
                st.session_state.confirm_clear = False
                st.success("All data cleared!")
                st.rerun()
            if col2.button("Cancel"):
                st.session_state.confirm_clear = False
                st.rerun()

if __name__ == "__main__":
    main()
