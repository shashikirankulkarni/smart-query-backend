import os
import pandas as pd
from sentence_transformers import util
from app.state.cache import synced_urls, sheet_cache
import cohere

# Initialize Cohere client
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def process_query(sheet_url: str, user_question: str, top_k: int = 3) -> str:
    sheet_url = str(sheet_url)

    # 1. Check if sheet is synced
    if sheet_url not in synced_urls or sheet_url not in sheet_cache:
        raise ValueError("Sheet not synced. Please sync the file before querying.")

    # 2. Retrieve cached data
    cache = sheet_cache[sheet_url]
    df = cache["df"]
    question_embeddings = cache["embeddings"]

    if not {'Question', 'Answer'}.issubset(df.columns):
        raise ValueError("Sheet must contain 'Question' and 'Answer' columns.")

    # 3. Embed query and search
    query_embedding = cache["embedder"].encode([user_question], convert_to_tensor=True) \
        if "embedder" in cache else \
        util.semantic_search(
            embedder.encode([user_question], convert_to_tensor=True),
            question_embeddings,
            top_k=top_k
        )
    results = util.semantic_search(query_embedding, question_embeddings, top_k=top_k)
    top_indices = [hit['corpus_id'] for hit in results[0]]
    context_df = df.iloc[top_indices]

    # 4. Format context
    documents = [
        {"title": f"Q{i+1}", "snippet": f"Q: {q}\nA: {a}"}
        for i, (q, a) in enumerate(zip(context_df['Question'], context_df['Answer']))
        if pd.notna(q) and pd.notna(a)
    ]

    # 5. Cohere API call
    preamble = (
        "You are a helpful assistant. Answer ONLY based on the following Q&A pairs. "
        "If the answer is not available in this data, say: 'I don't know.'"
    )
    response = co.chat(
        model="command-r",
        message=user_question,
        documents=documents,
        preamble=preamble,
        temperature=0.3
    )

    return response.text.strip()