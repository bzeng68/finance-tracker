import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title="Finance Tracker", layout="wide")

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }
    
if os.path.exists("categories.json"):
    with open("categories.json", "r") as f:
        st.session_state.categories = json.load(f)
        
def save_categories():
    with open("categories.json", "w") as f:
        json.dump(st.session_state.categories, f)
        
def categorize_transactions(df):
    df["Category"] = "Uncategorized"
    
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        
        for idx, row in df.iterrows():
            details = row["Description"].lower().strip()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
                
    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].astype(float)
        df["Amount"] = df['Amount'].apply(lambda x: x * -1 if x < 0 else x)
        df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%m/%d/%Y")

        return categorize_transactions(df)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        return True
    return False

def main():
    st.title("Finance Dashboard")
    
    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            expenses_df = df[df["Type"] == "Sale"].copy()
            payments_df = df[df["Type"] == "Payment"].copy()
            
            st.session_state.expenses_df = expenses_df.copy()
            
            tab_expenses, tab_payments = st.tabs(["Expenses", "Payments"])
            with tab_expenses:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")
                
                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()
                
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.expenses_df[["Transaction Date", "Description", "Amount", "Category"]],
                    column_config={
                        "Transaction Date": st.column_config.DateColumn("Transaction Date", format = "MM/DD/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format = "$%.2f"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options = list(st.session_state.categories.keys()), 
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
                        if new_category == st.session_state.expenses_df.at(idx, "Category"):
                            continue
                        
                        details = row["Details"]
                        st.session_state.expenses_df.at[idx, "Category"] = new_category
                        add_keyword_to_category(new_category, details)
                        
                st.subheader("Expense Summary")
                category_totals = st.session_state.expenses_df.groupby("Category")["Amount"].sum().reset_index()
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
            
            with tab_payments:
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
        
main()