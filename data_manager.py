from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

class DataManager:
    def __init__(self, transactions_df, budgets, embedding_model="all-minilm"):
        self.transactions_df = transactions_df
        self.budgets = budgets
        self.embedding_model = embedding_model
        self.embeddings = OllamaEmbeddings(model = self.embedding_model)
        self.vector_db = None
        self._prepare_vector_db()
        
    def _prepare_vector_db(self):
        docs = []
        
        if self.transactions_df is not None:
            for _, row in self.transactions_df.iterrows():
                docs.append(
                    Document (
                        page_content= (
                            f"Transaction:\n"
                            f"- Date: {row['Transaction Date']}\n"
                            f"- Category: {row['Category']}\n"
                            f"- Amount: {row['Amount']}\n"
                            f"- Type: {row['Type']}\n"
                            f"- Description: {row['Description']}\n"
                        )
                    ) 
                )
        
        if self.budgets:
            for budget_name, budget in self.budgets.items():
                for category, limit in budget.items():
                    docs.append(
                        Document(
                            page_content=(
                                f"Budget:\n"
                                f"- Budget Name: {budget_name}\n"
                                f"- Category: {category}\n"
                                f"- Monthly Limit: {limit}\n"
                            )
                        )
                    )
                
        self.vector_db = Chroma.from_documents(
            docs,
            self.embeddings,
            persist_directory="./chroma_db"
        )
        
    def get_retriever(self):
        return self.vector_db.as_retriever(search_kwargs={"k": 4})