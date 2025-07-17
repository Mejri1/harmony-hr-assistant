print('[DEBUG] my_streamlit_app/services/preload_resources.py imported')
import streamlit as st
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os
from db.vectorstore import get_vectorstore
import time

def load_shared_resources():
    print('[DEBUG] load_shared_resources called')
    print("[DEBUG] Loading shared resources...")
    t0 = time.time()
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../intent_classifier/models/intent_classifier/final"))
    intent_model = AutoModelForSequenceClassification.from_pretrained(model_path)
    intent_tokenizer = AutoTokenizer.from_pretrained(model_path)
    t1 = time.time()
    print(f"[DEBUG] Loaded intent model/tokenizer in {t1-t0:.2f}s")

    fr_to_en = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
    en_to_fr = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
    t2 = time.time()
    print(f"[DEBUG] Loaded translation pipelines in {t2-t1:.2f}s")

    vectordb = get_vectorstore()
    t3 = time.time()
    print(f"[DEBUG] Loaded vectorstore in {t3-t2:.2f}s")

    print("[DEBUG] Shared resources loaded: intent_model, intent_tokenizer, fr_to_en, en_to_fr, vectordb")
    return {
        "intent_model": intent_model,
        "intent_tokenizer": intent_tokenizer,
        "fr_to_en": fr_to_en,
        "en_to_fr": en_to_fr,
        "vectordb": vectordb
    }
