import streamlit as st
import sys
import os
import traceback
import threading
from langchain.schema import AIMessage, HumanMessage
from langdetect import detect
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# === Global resource dictionary ===
resources = {}
torch.classes.__path__ = []

def setup_project_path():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if project_root not in sys.path:
        sys.path.append(project_root)
    return project_root

def load_intent_classifier(project_root):
    try:
        model_path = os.path.join(project_root, "intent_classifier/models/intent_classifier/final")
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        resources["intent_model"] = model
        resources["intent_tokenizer"] = tokenizer
        print("✅ Intent classifier chargé")
    except Exception:
        print("❌ Erreur lors du chargement du modèle d'intention")
        traceback.print_exc()

def load_translation_pipelines():
    try:
        resources["fr_to_en"] = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
        resources["en_to_fr"] = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
        print("✅ Pipelines de traduction chargés")
    except Exception:
        print("❌ Erreur lors du chargement des pipelines de traduction")
        traceback.print_exc()

def load_chatbot_chain(user_id="temp_user", session_id="temp_session"):
    try:
        from chatbot.chain import get_chatbot_chain
        from chatbot.memory import get_memory_from_session
        from db.firebase import load_messages

        memory = get_memory_from_session(user_id, session_id)
        chain, vectordb = get_chatbot_chain(user_id, session_id, memory=memory)
        messages = load_messages(user_id, session_id)

        resources["chatbot_chain"] = chain
        resources["vectordb"] = vectordb
        resources["messages"] = messages
        print("✅ Chaîne RAG et messages chargés")
    except Exception:
        print("❌ Erreur lors du chargement de la chaîne chatbot")
        traceback.print_exc()

@st.cache_resource
def preload_all_resources(user_id, session_id):
    project_root = setup_project_path()
    threads = [
        threading.Thread(target=load_intent_classifier, args=(project_root,)),
        threading.Thread(target=load_translation_pipelines),
        threading.Thread(target=load_chatbot_chain, args=(user_id, session_id))
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print("✅ Tous les composants ont été préchargés")

def translate_text(text, source_lang, target_lang):
    if source_lang == "fr" and target_lang == "en":
        return resources["fr_to_en"](text, max_length=512)[0]['translation_text']
    elif source_lang == "en" and target_lang == "fr":
        return resources["en_to_fr"](text, max_length=512)[0]['translation_text']
    return text

def classify_intent(text):
    try:
        tokenizer = resources["intent_tokenizer"]
        model = resources["intent_model"]
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)
            label_id = torch.argmax(probs, dim=1).item()
            confidence = probs[0][label_id].item()
        return {0: "needs_rag", 1: "no_rag"}[label_id], confidence
    except Exception:
        print("🔥 Error in classify_intent")
        traceback.print_exc()


def chatbot_page(user_id, session_id):
    from db.firebase import save_message, save_session_summary
    from chatbot.memory import get_incremental_summary

    preload_all_resources(user_id, session_id)

    st.title("🤖 Harmony HR Chatbot")

    for key, default in {
        "displayed_messages": [],
        "last_session_id": None,
        "user_input": "",
        "messages": [],
        "user_lang": "en"
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state["last_session_id"] != session_id:
        st.session_state["displayed_messages"] = []
        st.session_state["messages"] = []

        for msg in resources["messages"]:
            content = msg["content"]
            if msg["sender"] == "user":
                st.session_state["displayed_messages"].append({"type": "human", "content": content})
                st.session_state["messages"].append(HumanMessage(content=content))
            elif msg["sender"] == "bot":
                st.session_state["displayed_messages"].append({"type": "ai", "content": content})
                st.session_state["messages"].append(AIMessage(content=content))
        st.session_state["last_session_id"] = session_id

    for msg in st.session_state["displayed_messages"]:
        role = "You" if msg["type"] == "human" else "Harmony"
        st.markdown(f"**{role}:** {msg['content']}")

    user_input = st.text_input("Your message:", value=st.session_state["user_input"])

    if st.button("Send") and user_input.strip():
        try:
            from chatbot.chain import get_chatbot_chain
            detected_lang = detect(user_input)
            st.session_state["user_lang"] = detected_lang
            user_input_en = translate_text(user_input, "fr", "en") if detected_lang == "fr" else user_input

            save_message(user_id, session_id, "user", user_input)
            st.session_state["displayed_messages"].append({"type": "human", "content": user_input})
            st.session_state["messages"].append(HumanMessage(content=user_input))

            intent, confidence = classify_intent(user_input_en)
            st.markdown(f"🔎 *Detected intent:* **{intent}** (Confidence: {confidence:.2f})")

            chain = resources["chatbot_chain"]
            vectordb = resources["vectordb"]
            retriever = vectordb.as_retriever(search_kwargs={"k": 3})

            if intent == "needs_rag":
                docs = retriever.get_relevant_documents(user_input_en)
                context = "\n\n".join([doc.page_content for doc in docs])
                chain.prompt.template = f"""
You are Harmony, a professional and empathetic HR assistant at Hydatis.
...
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

            response = chain.invoke({"input": user_input_en})
            bot_reply_en = response if isinstance(response, str) else response.get("response", "[No response]")
            bot_reply = translate_text(bot_reply_en, "en", "fr") if detected_lang == "fr" else bot_reply_en

            save_message(user_id, session_id, "bot", bot_reply)
            st.session_state["displayed_messages"].append({"type": "ai", "content": bot_reply})
            st.session_state["messages"].append(AIMessage(content=bot_reply))

            chain.memory.save_context({"input": user_input_en}, {"output": bot_reply_en})


            st.session_state["user_input"] = ""
            st.rerun()

        except Exception:
            print("🔥 Error in message handling")
            traceback.print_exc()
