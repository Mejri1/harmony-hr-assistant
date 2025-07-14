import streamlit as st
import sys
import os
import traceback
import pdb
from langchain.schema import AIMessage, HumanMessage

# Project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from chatbot.chain import get_chatbot_chain
    from db.firebase import save_message, load_messages, save_session_summary
    from chatbot.memory import get_memory_from_session, get_incremental_summary
except Exception as e:
    print("🔥 Import failed in chatbot_page.py")
    traceback.print_exc()
    pdb.set_trace()

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

torch.classes.__path__ = []

@st.cache_resource
def load_intent_model():
    try:
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../intent_classifier/models/intent_classifier/final"))    
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ Intent model loaded.")
        return model, tokenizer
    except Exception as e:
        print("🔥 Failed to load intent model")
        traceback.print_exc()
        pdb.set_trace()

intent_model, intent_tokenizer = load_intent_model()

label_id2name = {
    0: "needs_rag",
    1: "no_rag"
}

def classify_intent(text):
    try:
        inputs = intent_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = intent_model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)
            label_id = torch.argmax(probs, dim=1).item()
            confidence = probs[0][label_id].item()
        return label_id2name[label_id], confidence
    except Exception as e:
        print("🔥 Error in classify_intent")
        traceback.print_exc()
        pdb.set_trace()

def unique_key_generator(prefix="key"):
    counter = 0
    while True:
        counter += 1
        yield f"{prefix}_{counter}"

@st.cache_resource
def load_chatbot_resources(user_id, session_id):
    try:
        print(f"📦 Loading memory for user {user_id}, session {session_id}")
        memory = get_memory_from_session(user_id, session_id)

        print("🔗 Getting chain and vectorDB...")
        chain, vectordb = get_chatbot_chain(user_id, session_id, memory=memory)

        print("💬 Loading messages...")
        messages = load_messages(user_id, session_id)

        return chain, vectordb, messages
    except Exception as e:
        print("🔥 Error in load_chatbot_resources")
        traceback.print_exc()
        pdb.set_trace()

def chatbot_page(user_id, session_id):
    try:
        st.title("🤖 Harmony HR Chatbot")

        for key, default in {
            "displayed_messages": [],
            "last_session_id": None,
            "messages_since_summary": 0,
            "user_input": "",
            "messages": []
        }.items():
            if key not in st.session_state:
                st.session_state[key] = default

        widget_keys = unique_key_generator("user_input")

        print("🔄 Loading chatbot resources...")
        chain, vectordb, messages = load_chatbot_resources(user_id, session_id)
        memory = chain.memory

        print("✅ Resources loaded. Total messages from DB:", len(messages))
        print("👀 Memory content:", memory)

        st.session_state["chain"] = chain
        st.session_state["vectordb"] = vectordb

        if st.session_state["last_session_id"] != session_id or not st.session_state["displayed_messages"]:
            st.session_state["displayed_messages"] = []
            st.session_state["messages"] = []

            for msg in messages:
                sender = msg.get("sender", "")
                content = msg.get("content", "")
                print(f"📥 Message - Sender: {sender}, Content: {content}")
                if sender == "user":
                    st.session_state["displayed_messages"].append({"type": "human", "content": content})
                    st.session_state["messages"].append(HumanMessage(content=content))
                elif sender == "bot":
                    st.session_state["displayed_messages"].append({"type": "ai", "content": content})
                    st.session_state["messages"].append(AIMessage(content=content))

            st.session_state["last_session_id"] = session_id

        for msg in st.session_state["displayed_messages"]:
            if msg["type"] == "human":
                st.markdown(f"**You:** {msg['content']}")
            elif msg["type"] == "ai":
                st.markdown(f"**Harmony:** {msg['content']}")

        user_input = st.text_input("Your message:", key=next(widget_keys), value=st.session_state["user_input"])

        SUMMARY_K = 8

        if st.button("Send") and user_input.strip():
            print("📝 User input:", user_input)

            save_message(user_id, session_id, "user", user_input)
            st.session_state["displayed_messages"].append({"type": "human", "content": user_input})
            st.session_state["messages"].append(HumanMessage(content=user_input))

            intent, confidence = classify_intent(user_input)
            st.markdown(f"🔎 *Detected intent:* **{intent}** (Confidence: {confidence:.2f})")

            retriever = vectordb.as_retriever(search_kwargs={"k": 3})

            if intent == "needs_rag":
                print("📚 Running RAG retrieval...")
                docs = retriever.get_relevant_documents(user_input)
                context = "\n\n".join([doc.page_content for doc in docs])

                chain.prompt.template = f"""
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

---

Relevant company policies and information:
{context}

---

Conversation so far:
{{history}}

Current user question:
Human: {{input}}

---

Harmony's reply:
"""

            print("🧠 Invoking chain...")
            response = chain.invoke({"input": user_input})
            bot_reply = response if isinstance(response, str) else response.get("response", "[No response]")
            print("🤖 Bot reply:", bot_reply)

            save_message(user_id, session_id, "bot", bot_reply)
            st.session_state["displayed_messages"].append({"type": "ai", "content": bot_reply})
            st.session_state["messages"].append(AIMessage(content=bot_reply))

            memory.save_context({"input": user_input}, {"output": bot_reply})
            st.session_state["messages_since_summary"] += 2

            if st.session_state["messages_since_summary"] >= SUMMARY_K:
                summary = get_incremental_summary(user_id, session_id, k=SUMMARY_K)
                save_session_summary(user_id, session_id, summary)
                st.session_state["messages_since_summary"] = 0

            st.session_state["user_input"] = ""
            st.rerun()

    except Exception as e:
        print("🔥 Exception in chatbot_page()")
        traceback.print_exc()
        pdb.set_trace()
