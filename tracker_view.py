import streamlit as st
import plotly.express as px
import pandas as pd
from constants import PREVIOUS_TRANSACTIONS_PATH

class TrackerView:
    def __init__(self, transaction_manager, categories_utils, budget_manager):
        st.set_page_config(page_title="Finance Tracker", layout="wide")
        st.title("Finance Dashboard")
        self.transaction_manager = transaction_manager
        self.categories_utils = categories_utils
        self.budget_manager = budget_manager
        
    def handle_file_upload(self):
        uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])
        
        if uploaded_file is not None:
            try:
                self.transaction_manager.add_transactions(
                    uploaded_file, 
                    self.categories_utils.get_categories()
                )
                self.transaction_manager.save_transactions()
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                raise e
                
    def show_separated_tabs(self):
        self.expenses_tab, self.payments_tab, self.budgets_tab = st.tabs(["Expenses", "Payments", "Budgets"])
        self.show_expenses_tab()
        self.show_payments_tab()
        self.show_budgets_tab()
                
    def show_expenses_tab(self):
        expenses = self.transaction_manager.expenses
        with self.expenses_tab:
            self.create_add_category()
            self.create_expenses_table(expenses)
            self.create_expenses_summary(expenses)
    
    def show_payments_tab(self):
        with self.payments_tab:
            self.create_payment_summary(self.transaction_manager.payments)
            
    def show_budgets_tab(self):
        with self.budgets_tab:
            self.display_budgets()
            
    def create_add_category(self):
        new_category = st.text_input("New Category Name")
        add_button = st.button("Add Category", key="add_category_btn")
        
        if add_button and new_category:
            if new_category not in self.categories_utils.get_categories():
                self.categories_utils.add_category(new_category)
                self.categories_utils.save_categories()
                st.rerun()
                
    def create_expenses_table(self, expenses_df):
        st.subheader("Your Expenses")
        edited_df = st.data_editor(
            expenses_df,
            column_config={
                "Transaction Date": st.column_config.DateColumn("Transaction Date", format = "MM/DD/YYYY"),
                "Amount": st.column_config.NumberColumn("Amount", format = "$%.2f"),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options = list(self.categories_utils.get_categories().keys()), 
                    required = True
                )
            },
            hide_index = True,
            use_container_width = True,
            key = "category_editor"
        )
        save_button = st.button("Apply Changes", type = "primary")
        if save_button:
            for idx, row in edited_df.iterrows():
                new_category = row["Category"]
                if new_category == expenses_df.at[idx, "Category"]:
                    continue
                
                description = row["Description"]
                self.transaction_manager.update_expense_transaction(idx, new_category)
                self.categories_utils.add_keyword_to_category(new_category, description)
                self.categories_utils.save_categories()
                self.transaction_manager.save_transactions()
                
    def create_expenses_summary(self, expenses_df):
        st.subheader("Expense Summary")
        category_totals = expenses_df.groupby("Category")["Amount"].sum().reset_index()
        category_totals = category_totals.sort_values("Amount", ascending = False)
        
        st.dataframe(
            category_totals,
            column_config = {
                "Amount": st.column_config.NumberColumn("Amount", format = "$%.2f")
            },
            use_container_width = True,
            hide_index = True
        )
        
        fig = px.pie(
            category_totals,
            values = "Amount",
            names = "Category",
            title = "Expenses by Category"
        )
        st.plotly_chart(fig, use_container_width = True)
        
    def create_payment_summary(self, payments_df):
        st.subheader("Payments Summary")
        total_payments = payments_df["Amount"].sum()
        st.metric("Total Payments", f"${total_payments:,.2f}")
        st.dataframe(
            payments_df[["Transaction Date", "Amount"]],
            column_config = {
                "Transaction Date": st.column_config.DateColumn("Transaction Date", format = "MM/DD/YYYY"),
                "Amount": st.column_config.NumberColumn("Amount", format = "$%.2f")
            },
            hide_index = True,
            use_container_width = True
        )
        
    def display_budgets(self):
        self.show_create_budget_form()
        current_budget, current_monthly_transactions = self.show_selectors()
        
        if current_budget and current_monthly_transactions is not None:
            self.display_budget_calculations(current_budget, current_monthly_transactions)
            
    def show_selectors(self):
        saved_budgets = self.budget_manager.list_budgets()
        available_months = self.transaction_manager.get_available_months()
        
        if saved_budgets and available_months:
            return self.show_budget_selector(saved_budgets), self.show_month_selector(available_months)
        elif not saved_budgets:
            st.info("No budgets saved yet. Add one below!")  
        elif not available_months:
            st.info("No months of transactions saved yet. Add one in above!")  
        else:
            st.info("No budgets or months of transactions saved yet. Add some before doing budget calculations!")
        return None, None
        
    def show_budget_selector(self, saved_budgets):
        selected = st.selectbox("Select existing budget:", saved_budgets)
        loaded = self.budget_manager.load_budget(selected)
        if loaded:
            return loaded
    
    def show_month_selector(self, available_months):
        selected = st.selectbox("Select month of transactions:", available_months)
        selected_transactions_month_filepath = selected.replace(" ", "_") + "_Transactions.csv"
        loaded_expenses, _ = self.transaction_manager.separate_transactions(
            self.transaction_manager.load_transactions(
                PREVIOUS_TRANSACTIONS_PATH + "/" + selected_transactions_month_filepath,
                self.categories_utils.get_categories()
            )
        )
        if loaded_expenses is not None:
            return loaded_expenses
        
    def show_create_budget_form(self):
        with st.expander("Add Budget"):
            budget_name = st.text_input("Budget Name", placeholder="e.g. Vacation, Groceries, Default")

            if "num_categories" not in st.session_state:
                st.session_state.num_categories = 0
            if "budget_categories" not in st.session_state:
                st.session_state.budget_categories = []
            
            if st.button("Add Category", key="add_category_of_budget_btn"):
                st.session_state.num_categories += 1
                
            if st.button("Remove Category"):
                st.session_state.num_categories -= 1

            budget = {}

            with st.form("budget_form"):
                st.write("Enter categories and values:")

                for i in range(st.session_state.num_categories):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        cat = st.text_input(f"Category {i+1}", key=f"cat_{i}")
                    with col2:
                        val = st.text_input(f"Value {i+1}", key=f"value_{i}")

                    budget[cat] = val

                submitted = st.form_submit_button("Save Budget")

            if submitted:
                save_result = self.budget_manager.save_budget(budget_name, budget)
                if save_result:
                    for problem in save_result:
                        st.error(problem)
                else:
                    st.success(f"Successfully saved budget {budget_name}!")
                    st.session_state.num_categories = 0
                    budget = {}
                    
    def display_budget_calculations(self, budget, monthly_transactions):
        categorized_transactions = monthly_transactions[monthly_transactions["Category"] != "Uncategorized"]
        
        budget_categories = set(budget.keys())
        transaction_categories = set(categorized_transactions["Category"].unique())

        missing_in_transactions = budget_categories - transaction_categories
        missing_in_budget = transaction_categories - budget_categories

        if missing_in_transactions:
            st.warning(f"Categories in budget but not in transactions: {missing_in_transactions}")
        if missing_in_budget:
            st.warning(f"Categories in transactions but not in budget: {missing_in_budget}")

        if not missing_in_budget and not missing_in_transactions:
            spent_per_category = categorized_transactions.groupby('Category')['Amount'].sum().reset_index()
            spent_per_category.rename(columns={'Amount': 'Spent'}, inplace=True)

            summary = pd.DataFrame(columns=["Category", "Budget", "Spent", "Remaining"])

            for cat, limit in budget.items():
                limit_float = float(limit)
                spent = float(spent_per_category[spent_per_category["Category"] == cat]["Spent"])
                remaining = float(limit_float - spent)
                summary = pd.concat([summary, pd.DataFrame([{
                    "Category": cat,
                    "Budget": limit_float,
                    "Spent": spent,
                    "Remaining": remaining,
                    "Progress": "✔" if remaining >= 0 else "✖"
                }])], ignore_index=True)
                
            st.subheader("Summary")
            st.dataframe(
                summary, 
                column_config={
                    "Budget": st.column_config.NumberColumn("Budget", format = "$%.2f"),
                    "Spent": st.column_config.NumberColumn("Amount", format = "$%.2f"),
                    "Remaining": st.column_config.NumberColumn("Remaining", format = "$%.2f")
                },
                hide_index = True
            )

            st.subheader("Category Breakdown")
            for cat in budget.keys():
                cat_transactions = monthly_transactions[monthly_transactions["Category"] == cat]
                with st.expander(f"{cat} ({len(cat_transactions)} transactions)"):
                    st.dataframe(
                        cat_transactions[["Transaction Date", "Description", "Amount"]],
                        column_config={
                            "Transaction Date": st.column_config.DateColumn("Transaction Date", format = "MM/DD/YYYY"),
                            "Amount": st.column_config.NumberColumn("Amount", format = "$%.2f")
                        },
                        hide_index = True
                    )