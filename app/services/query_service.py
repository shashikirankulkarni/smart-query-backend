import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from app.utils.sheet_loader import load_sheet_from_url
import cohere

# Initialize embedding model + Cohere client
embedder = SentenceTransformer("all-MiniLM-L6-v2")
co = cohere.Client(os.getenv("COHERE_API_KEY"))

def process_query(sheet_url: str, user_question: str, top_k: int = 3) -> str:
    # 1. Load sheet from URL
    df = load_sheet_from_url(str(sheet_url))
    if not {'Question', 'Answer'}.issubset(df.columns):
        raise ValueError("Sheet must contain 'Question' and 'Answer' columns.")

    # 2. Embed and search
    question_embeddings = embedder.encode(df['Question'].tolist(), convert_to_tensor=True)
    query_embedding = embedder.encode([user_question], convert_to_tensor=True)
    results = util.semantic_search(query_embedding, question_embeddings, top_k=top_k)
    top_indices = [hit['corpus_id'] for hit in results[0]]
    context_df = df.iloc[top_indices]

    # 3. Format context
    documents = [
        {"title": f"Q{i+1}", "snippet": f"Q: {q}\nA: {a}"}
        for i, (q, a) in enumerate(zip(context_df['Question'], context_df['Answer']))
        if pd.notna(q) and pd.notna(a)
    ]

    # 4. Call Cohere chat API
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