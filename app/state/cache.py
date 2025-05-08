# app/state/cache.py

from typing import Dict, Any
import pandas as pd
import torch

# Tracks which URLs were successfully synced
synced_urls = set()

# Main cache for each sheet_url
# {
#   sheet_url: {
#       "df": pd.DataFrame,
#       "embeddings": torch.Tensor
#   }
# }
sheet_cache: Dict[str, Dict[str, Any]] = {}