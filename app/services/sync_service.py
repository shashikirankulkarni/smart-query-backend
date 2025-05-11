import pandas as pd
import requests
from io import BytesIO
from app.models.schemas import SyncResponse
from app.state.cache import synced_urls, sheet_cache, embedding_cache

def sync_sheet(sheet_url: str) -> SyncResponse:
    sheet_url = str(sheet_url)

    synced_urls.clear()
    sheet_cache.clear()
    embedding_cache.clear()

    try:
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

        synced_urls.add(sheet_url)
        sheet_cache[sheet_url] = df

        return SyncResponse(columns=df.columns.tolist(), row_count=len(df))

    except Exception as e:
        raise ValueError(f"Failed to load sheet: {e}")