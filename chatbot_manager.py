from ollama import chat

class ChatbotManager:
    def __init__(self, retriever, model_name = "llama3"):
        self.retriever = retriever
        self.model_name = model_name
    
    def ask(self, conversation):
        latest_user_msg = [m["content"] for m in conversation if m["role"] == "user"][-1]
        docs = self.retriever.get_relevant_documents(latest_user_msg)
        context = "\n".join([doc.page_content for doc in docs])

        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation])
        prompt = (
            "You are a helpful personal finance assistant.\n"
            "Use the following data to answer the question accurately. "
            "Do not make up information.\n\n"
            f"Data:\n{context}\n\n"
            f"Conversation history:\n{history_text}\n"
            f"Answer the last question clearly:\n"
        )

        response = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]