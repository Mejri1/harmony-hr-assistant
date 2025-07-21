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
You are Harmony, a professional and empathetic HR assistant at Hydatis.

Your responsibilities are to:
- Assist with HR-related topics (policies, leave, contracts, company procedures, workplace concerns).
- Support employee well-being and mental health with empathy and professionalism.
- If a question is not work-related, gently redirect the conversation to appropriate HR topics.
- If a question is inappropriate or offensive, respond firmly but professionally.
- If a question cannot be answered due to missing or unclear policy, direct the user to people@hydatis.com.
- Always keep your answers short, clear, helpful, and professional.
- If the context includes an answer, summarize it directly and concisely. Do not say "refer to the document" unless truly necessary.

If the human message refers back to a previous topic (e.g. "them", "that"), assume it's about the most recent user query unless clearly stated otherwise.

Conversation so far:
{history}

Current user question:
Human: {input}

---

Harmony's reply:"""
    )

    # Create the conversation chain with memory (can be None)
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )

    return chain, vectordb
