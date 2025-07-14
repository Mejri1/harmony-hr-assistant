from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
from chatbot.chain import get_chatbot_chain
from db.firebase import save_message, save_session_summary

# Load intent classifier
INTENT_MODEL_PATH = "intent_classifier/models/intent_classifier/final"
intent_model = AutoModelForSequenceClassification.from_pretrained(INTENT_MODEL_PATH)
intent_tokenizer = AutoTokenizer.from_pretrained(INTENT_MODEL_PATH)

# Label mapping based on updated dataset
label_id2name = {
    0: "moderation_required",
    1: "needs_rag",
    2: "no_rag"
}

# Inference function
def classify_intent(text):
    inputs = intent_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = intent_model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        label_id = torch.argmax(probs, dim=1).item()
        confidence = probs[0][label_id].item()
    return label_id2name[label_id], confidence

# Chatbot setup
user_id = "user_123"
session_id = "session_001"

chain, vectordb = get_chatbot_chain(user_id, session_id)
memory = chain.memory
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

print("🤖 Harmony: Hello! How can I assist you today? (type 'exit' to quit)")

# Main loop
while True:
    user_input = input("🧑 You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    save_message(user_id, session_id, "user", user_input)

    # Step 1: Classify intent
    intent, confidence = classify_intent(user_input)
    print(f"🔎 Detected intent: {intent} (Confidence: {confidence:.2f})")

    # Step 2: Route based on intent
    if intent == "moderation_required":
        bot_reply = "⚠️ Please be respectful. I’m here to support you with work-related topics only."

    elif intent == "needs_rag":
        docs = retriever.get_relevant_documents(user_input)
        print("\n📚 Retrieved context:")
        for i, doc in enumerate(docs):
            print(f"  [{i+1}] {doc.page_content.strip()[:300]}...\n")

        context = "\n\n".join([doc.page_content for doc in docs])
        augmented_input = f"""Use the context below to answer the employee's question:

Context:
{context}

Question: {user_input}
"""
        response = chain.invoke({"input": augmented_input})
        bot_reply = response.get("response", "[No response]")

    elif intent == "no_rag":
        # Direct prompt to LLM without context
        direct_prompt = f"""You are Harmony, an HR assistant. Answer the following employee question as helpfully as possible.

Question: {user_input}
"""
        response = chain.invoke({"input": direct_prompt})
        bot_reply = response.get("response", "[No response]")

    else:
        bot_reply = "🤖 I'm not sure how to respond to that yet. Let me try to connect you with HR."

    print(f"🤖 Harmony: {bot_reply}")
    save_message(user_id, session_id, "bot", bot_reply)
    save_session_summary(user_id, session_id, memory.buffer)
