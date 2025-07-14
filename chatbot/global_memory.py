from db.firebase import (
    load_all_session_summaries,
    save_global_summary,
)
from datetime import datetime
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
GLOBAL_MEMORY_PROMPT = PromptTemplate(
    input_variables=["sessions"],
    template="""
You're an AI HR analyst. You’ll process multiple session-level insights to build a global employee memory.

Input:
{sessions}

Extract:
- "summary": a short description of recurring concerns and themes.
- "topics": a list of repeated topics (e.g., "burnout", "promotion").
- "keywords": frequently used terms.
- "sentiment_score": average sentiment score.
- "emotions": average score of emotions like anxiety, motivation, stress.
- "sessions_analyzed": total sessions.
- "concerns_timeline": array of { date, concern } based on session insights.

Respond in valid JSON only.
"""
)


def update_global_memory(user_id: str):
    llm = ChatOpenAI(
        temperature=0.3,
        model="mathstral-7b-v0.1",
        base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed"
    )

    # Step 1: Get all session summaries from Firestore
    sessions_data = load_all_session_summaries(user_id)  # → List[Dict]

    # Build a serialized string for the prompt, handle missing fields robustly
    session_insights = "\n".join([
        f"[{s.get('timestamp_created', 'unknown')}] "
        f"Concerns: {s.get('main_concerns', [])}, "
        f"Sentiment: {s.get('sentiment_score', 0)}, "
        f"Emotions: {s.get('emotions', {})}"
        for s in sessions_data if isinstance(s, dict)
    ])

    # Step 2: Run prompt on the sessions
    prompt = GLOBAL_MEMORY_PROMPT.format(sessions=session_insights)
    response = llm.invoke(prompt)

    try:
        global_data = json.loads(response.content)
        global_data["last_updated"] = datetime.utcnow().isoformat()

        # Step 3: Save to Firestore
        save_global_summary(user_id, global_data)

        print("✅ Global memory updated.")
    except Exception as e:
        print("❌ Failed to update global memory:", e)
        print("Raw output:\n", response.content)