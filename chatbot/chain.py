# chatbot/chain.py

from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # Use this if you're using LangChain with OpenAI-compatible APIs
from db.vectorstore import get_vectorstore  # Adjust if you renamed it

CHROMA_PATH = r"C:\Users\Omar\Desktop\ai-attrition-system\db\chroma"


def get_chatbot_chain(user_id: str, session_id: str, memory=None):
    # Only use memory if it's a valid LangChain memory object, otherwise pass None
    # Do NOT call get_memory_from_session here, as it returns a list, not a memory object

    # Load vector store (used in RAG if needed)
    vectordb = get_vectorstore()

    # Initialize LLM
    llm = ChatOpenAI(
        temperature=0.7,
        model="mathstral-7b-v0.1",
        base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed"
    )

    # Define prompt template
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="""
You are Harmony, a professional and empathetic HR assistant.

Your job is to:
- Help with HR-related questions (policies, contracts, leave, workplace concerns).
- Support employees with empathy, especially on well-being and mental health.
- Politely redirect off-topic or inappropriate messages.
- Keep responses clear, concise, short and professional.
- If unsure about a specific detail, redirect to people@hydatis.com.

Conversation history:
{history}
Human: {input}
Harmony:"""
    )

    # Create the conversation chain with memory (can be None)
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )

    return chain, vectordb
