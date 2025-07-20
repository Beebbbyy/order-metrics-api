import requests
import os

def download_csv_file(url: str, file_id: str):
    response = requests.get(url)
    response.raise_for_status()

    file_path = os.path.join("data", f"{file_id}.csv")
    with open(file_path, "wb") as f:
        f.write(response.content)
