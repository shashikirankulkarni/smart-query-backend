import pandas as pd
import requests
from io import BytesIO
from app.models.schemas import SyncResponse
from app.state.cache import synced_urls, sheet_cache
from sentence_transformers import SentenceTransformer

# Load embedding model only once
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def sync_sheet(sheet_url) -> SyncResponse:
    sheet_url = str(sheet_url)
    try:
        # Load the sheet
        if "docs.google.com/spreadsheets" in sheet_url:
            file_id = sheet_url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
            df = pd.read_csv(BytesIO(requests.get(csv_url).content))
        elif sheet_url.endswith(".csv"):
            df = pd.read_csv(BytesIO(requests.get(sheet_url).content))
        else:
            if "drive.google.com" in sheet_url and "uc?export=download" not in sheet_url:
                file_id = sheet_url.split("/d/")[1].split("/")[0]
                sheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            elif "dropbox.com" in sheet_url:
                sheet_url = sheet_url.replace("?dl=0", "?dl=1")
            response = requests.get(sheet_url, timeout=15)
            response.raise_for_status()
            df = pd.read_excel(BytesIO(response.content), engine="openpyxl")

        # Validate format
        if not {'Question', 'Answer'}.issubset(df.columns):
            raise ValueError("Sheet must contain 'Question' and 'Answer' columns.")

        # Generate embeddings
        question_list = df["Question"].fillna("").tolist()
        question_embeddings = embedder.encode(question_list, convert_to_tensor=True)

        # Cache it
        synced_urls.add(sheet_url)
        sheet_cache[sheet_url] = {
            "df": df,
            "embeddings": question_embeddings
        }

        return SyncResponse(columns=df.columns.tolist(), row_count=len(df))

    except Exception as e:
        raise ValueError(f"Failed to load sheet: {e}")