import pandas as pd
import requests
from io import BytesIO

def load_sheet_from_url(url: str) -> pd.DataFrame:
    try:
        if "docs.google.com/spreadsheets" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
            return pd.read_csv(BytesIO(requests.get(csv_url).content))
        
        elif url.endswith(".csv"):
            return pd.read_csv(BytesIO(requests.get(url).content))
        
        else:
            if "drive.google.com" in url and "uc?export=download" not in url:
                file_id = url.split("/d/")[1].split("/")[0]
                url = f"https://drive.google.com/uc?export=download&id={file_id}"
            elif "dropbox.com" in url:
                url = url.replace("?dl=0", "?dl=1")

            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return pd.read_excel(BytesIO(response.content), engine="openpyxl")

    except Exception as e:
        raise ValueError(f"Failed to load sheet: {e}")