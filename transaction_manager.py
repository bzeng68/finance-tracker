import pandas as pd
import os

from constants import TRANSACTION_DF_COLUMNS, PREVIOUS_TRANSACTIONS_PATH

class TransactionManager:
    def __init__(self, categories):
        self.expenses = pd.DataFrame(columns = TRANSACTION_DF_COLUMNS)
        self.payments = pd.DataFrame(columns = TRANSACTION_DF_COLUMNS)
        self.get_previous_transactions(categories)
        
    def get_previous_transactions(self, categories):
        for entry in os.listdir(PREVIOUS_TRANSACTIONS_PATH):
            full_path = os.path.join(PREVIOUS_TRANSACTIONS_PATH, entry)
            self.add_transactions(full_path, categories)
            
    def save_transactions(self):
        expenses_to_save = self.expenses
        payments_to_save = self.payments
        
        expenses_to_save["Type"] = "Sale"
        payments_to_save["Type"] = "Payment"
        
        df_to_save = pd.concat([expenses_to_save, payments_to_save], ignore_index = True)
        df_to_save["Transaction Date"] = df_to_save["Transaction Date"].dt.strftime("%m/%d/%Y")

        for period, monthly_df in self.group_transactions_by_month(df_to_save):
            monthly_df.to_csv(f"{PREVIOUS_TRANSACTIONS_PATH}/{period}_Transactions.csv", index = False)
        
    def group_transactions_by_month(self, df_to_save):
        return [
            (str(period_dt), group.reset_index(drop=True))
            for period_dt, group in df_to_save.groupby(
                pd.to_datetime(df_to_save["Transaction Date"]).dt.strftime("%B_%Y")
            )
        ]
    
    def add_transactions(self, file, categories = {}):
        df = self.load_transactions(file, categories)
        curr_expenses, curr_payments = self.separate_transactions(df) 
        
        self.expenses = pd.concat([self.expenses, curr_expenses], ignore_index = True)
        self.payments = pd.concat([self.payments, curr_payments], ignore_index = True) 
        
    def load_transactions(self, file, categories):
        df = pd.read_csv(file)
        cleaned_df = self.clean_transactions(df)

        return self.categorize_transactions(cleaned_df, categories)
        
    def clean_transactions(self, df):
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].astype(float)
        df["Amount"] = df["Amount"].apply(lambda x: x * -1 if x < 0 else x)
        df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%m/%d/%Y")
        df["Category"] = "Uncategorized"
        
        return df
        
    def categorize_transactions(self, df, categories):
        for category, keywords in categories.items():
            if category == "Uncategorized" or not keywords:
                continue
            
            lowered_keywords = [keyword.lower().strip() for keyword in keywords]
            
            for idx, row in df.iterrows():
                description = row["Description"].lower().strip()
                if description in lowered_keywords:
                    df.at[idx, "Category"] = category
                    
        return df
    
    def separate_transactions(self, df):
        expenses_df = self.drop_unwanted_columns(df[df["Type"] == "Sale"].copy())
        payments_df = self.drop_unwanted_columns(df[df["Type"] == "Payment"].copy())
        
        return expenses_df, payments_df
    
    def drop_unwanted_columns(self, df):
        return df[TRANSACTION_DF_COLUMNS]
    
    def has_transactions(self):
        return not self.expenses.empty and not self.payments.empty
    
    def update_expense_transaction(self, idx, new_value):
        self.expenses.at[idx, "Category"] = new_value
        
    def get_available_months(self):
        return [entry.split("_Transactions")[0].replace("_", " ") for entry in os.listdir(PREVIOUS_TRANSACTIONS_PATH)]