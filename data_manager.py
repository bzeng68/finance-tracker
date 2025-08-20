from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

class DataManager:
    def __init__(self, transactions_df, budgets, embedding_model="all-MiniLM-L6-v2"):
        self.transactions_df = transactions_df
        self.budgets = budgets
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(model_name = self.embedding_model)
        self.vector_db = None
        self._prepare_vector_db()
        
    def _prepare_vector_db(self):
        docs = []
        
        if self.transactions_df:
            docs += [
                Document(page_content = f"""
                                Transaction Date: {row['Transaction Date']}, 
                                Category: {row['Category']}, 
                                Amount: {row['Amount']}, 
                                Description: {row['Description']}
                                Type: {row['Type']}
                            """
                        )
                for _, row in self.transactions_df.iterrows()
            ]
        
        if self.budgets:
            for budget_name, budget in self.budgets.items():
                docs += [
                    Document(page_content = f"""
                                    Budget Name: {budget_name},
                                    Category: {category},
                                    Monthly Limit: {limit}
                                """
                            )
                    for category, limit in budget.items()
                ]
                
        self.vector_db = Chroma.from_documents(docs, self.embeddings)
        
    def get_retriever(self):
        return self.vector_db        