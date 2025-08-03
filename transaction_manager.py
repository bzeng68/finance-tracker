import pandas as pd
from constants import TRANSACTION_DF_COLUMNS

class TransactionManager:
    def __init__(self):
        self.expenses = pd.DataFrame(columns = TRANSACTION_DF_COLUMNS)
        self.payments = pd.DataFrame(columns = TRANSACTION_DF_COLUMNS)
    
    def add_transactions(self, file, categories = {}):
        df = self.load_transactions(file, categories)
        self.expenses, self.payments = self.separate_transactions(df)
        
    def load_transactions(self, file, categories):
        df = pd.read_csv(file)
        cleaned_df = self.clean_transactions(df)

        return self.categorize_transactions(cleaned_df, categories)
        
    def clean_transactions(self, df):
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].astype(float)
        df["Amount"] = df['Amount'].apply(lambda x: x * -1 if x < 0 else x)
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