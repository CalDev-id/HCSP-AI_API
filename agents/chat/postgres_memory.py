from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from utils import postgredb_apilogy

class PostgresConversationMemory(ConversationBufferMemory):
    def __init__(self, session_id: str, window: int = 10, **kwargs):
        super().__init__(memory_key="chat_history", **kwargs)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "window", window)

    async def load_memory_variables(self, inputs):
        rows = await postgredb_apilogy.fetch_chat_history(self.session_id, self.window)
        messages = []
        for row in rows:
            if row["role"] == "user":
                messages.append(HumanMessage(content=row["message"]))
            else:
                messages.append(AIMessage(content=row["message"]))
        self.chat_memory.messages = messages
        return {self.memory_key: self.chat_memory.messages}

    async def save_context(self, inputs, outputs):
        user_message = inputs.get("input") or ""
        ai_message = outputs.get("output") or ""

        await postgredb_apilogy.insert_chat_message(self.session_id, "user", user_message)
        await postgredb_apilogy.insert_chat_message(self.session_id, "assistant", ai_message)

        await super().save_context(inputs, outputs)
