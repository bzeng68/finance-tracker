import streamlit as st
import plotly.express as px

class TrackerView:
    def __init__(self, transaction_manager, categories_utils):
        st.set_page_config(page_title="Finance Tracker", layout="wide")
        st.title("Finance Dashboard")
        self.transaction_manager = transaction_manager
        self.categories_utils = categories_utils
        
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
        self.expenses_tab, self.payments_tab = st.tabs(["Expenses", "Payments"])
        self.show_expenses_tab()
        self.show_payments_tab()
                
    def show_expenses_tab(self):
        expenses = self.transaction_manager.expenses
        with self.expenses_tab:
            self.create_add_category()
            self.create_expenses_table(expenses)
            self.create_expenses_summary(expenses)
    
    def show_payments_tab(self):
        with self.payments_tab:
            self.create_payment_summary(self.transaction_manager.payments)
            
    def create_add_category(self):
        new_category = st.text_input("New Category Name")
        add_button = st.button("Add Category")
        
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