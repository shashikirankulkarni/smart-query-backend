
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from app.state.cache import synced_urls, sheet_cache, embedding_cache
import cohere

embedder = SentenceTransformer("all-MiniLM-L6-v2")
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def process_query(sheet_url: str, user_question: str, top_k: int = 3) -> str:
    sheet_url = str(sheet_url)

    if sheet_url not in synced_urls:
        raise ValueError("Sheet not synced. Please sync the file before querying.")

    df = sheet_cache.get(sheet_url)
    embeddings = embedding_cache.get(sheet_url)

    if df is None or embeddings is None:
        raise ValueError("Cached data not found. Please sync again.")

    if not {'Question', 'Answer'}.issubset(df.columns):
        raise ValueError("Sheet must contain 'Question' and 'Answer' columns.")

    # Embed query and perform semantic search
    query_embedding = embedder.encode([user_question], convert_to_numpy=True)
    results = util.semantic_search(query_embedding, embeddings, top_k=top_k)
    top_indices = [hit['corpus_id'] for hit in results[0]]
    context_df = df.iloc[top_indices]

    documents = [
        {"title": f"Q{i+1}", "snippet": f"Q: {q}\nA: {a}"}
        for i, (q, a) in enumerate(zip(context_df['Question'], context_df['Answer']))
        if pd.notna(q) and pd.notna(a)
    ]

    response = co.chat(
        model="command-r",
        message=user_question,
        documents=documents,
        preamble="You are a helpful assistant. Answer ONLY based on the following Q&A pairs. If the answer is not available, say 'I don't know.'",
        temperature=0.3
    )
    return response.text.strip()