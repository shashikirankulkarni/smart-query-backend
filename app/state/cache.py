# Keep only one active sheet in memory
sheet_cache = {}  # Key: sheet_url, Value: (DataFrame, Embeddings)
synced_urls = set()