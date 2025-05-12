import os
import pandas as pd
import requests
from app.state.cache import synced_urls, sheet_cache
import cohere
import time

HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/sentence-similarity"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def query_similarity_api(query: str, questions: list[str]) -> list[float]:
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": {
            "source_sentence": query,
            "sentences": questions
        }
    }
    start = time.time()
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
        print(f"✅ HuggingFace responded in {time.time() - start:.2f}s")
        return response.json()
    except requests.exceptions.Timeout:
        print(f"⏰ HuggingFace timed out after {time.time() - start:.2f}s")
        raise RuntimeError("Sorry, I did not catch that. Please try again!")
    except Exception as e:
        raise RuntimeError(f"HuggingFace or CoHere error: {e}")

def process_query(sheet_url: str, user_question: str, top_k: int = 3) -> str:
    sheet_url = str(sheet_url).split("?")[0].strip()
    if sheet_url not in synced_urls:
        raise ValueError("Sheet not synced. Please sync the file before querying.")

    df = sheet_cache.get(sheet_url)
    if df is None or not {'Question', 'Answer'}.issubset(df.columns):
        raise ValueError("Sheet must contain 'Question' and 'Answer' columns.")

    questions = df["Question"].fillna("").tolist()
    try:
        scores = query_similarity_api(user_question, questions)
        top_indices = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]

        documents = [
            {"title": f"Q{i+1}", "snippet": f"Q: {df.iloc[idx]['Question']}\nA: {df.iloc[idx]['Answer']}"}
            for i, (idx, _) in enumerate(top_indices)
        ]

        response = co.chat(
            model="command-r",
            message=user_question,
            documents=documents,
            preamble="You are a helpful assistant. Answer ONLY based on the following Q&A pairs. If unsure, say 'I don't know.'",
            temperature=0.3
        )
        return response.text.strip()

    except Exception as e:
        print(f"❌ HuggingFace/CoHere error: {e}")
        raise