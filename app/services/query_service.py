import os
import pandas as pd
import requests
from app.state.cache import synced_urls, sheet_cache
import cohere

HF_API_URL = "https://api-inference.huggingface.co/embeddings/sentence-transformers/all-MiniLM-L6-v2"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def get_embeddings_from_huggingface(sentences):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": sentences})
    response.raise_for_status()
    return response.json()

def cosine_similarity(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def process_query(sheet_url: str, user_question: str, top_k: int = 3) -> str:
    print(f"Received query for sheet: {sheet_url} | Question: {user_question}")
    if sheet_url not in synced_urls:
        print("❌ Sheet not synced!")
        raise ValueError("Sheet not synced. Please sync the file before querying.")

    df = sheet_cache.get(sheet_url)
    if df is None:
        print("❌ DataFrame not found in cache!")
        raise ValueError("Cached sheet not found. Please sync again.")

    if not {'Question', 'Answer'}.issubset(df.columns):
        print("❌ Missing required columns!")
        raise ValueError("Sheet must contain 'Question' and 'Answer' columns.")

    question_texts = df["Question"].fillna("").tolist()
    question_embeddings = get_embeddings_from_huggingface(question_texts)
    query_embedding = get_embeddings_from_huggingface([user_question])[0]

    scored = [
        (i, cosine_similarity(query_embedding, emb))
        for i, emb in enumerate(question_embeddings)
    ]
    top_indices = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]

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
