from ollama import chat
from langchain.schema import Document

class ChatbotManager:
    def __init__(self, retriever, model_name = "llama3"):
        self.retriever = retriever
        self.model_name = model_name
        
    def ask(self, query):
        docs = self.retriever.get_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt = f"Use the following data to answer the question.\nData:\n{context}\n\nQuestion: {query}\nAnswer:"
        response = chat(
            model = self.model_name,
            messages = [{ "role": "user", "content": prompt }]
        )
        
        return response['message']['content']