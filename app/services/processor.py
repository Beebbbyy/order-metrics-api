import pandas as pd
from uuid import UUID
from pathlib import Path
from datetime import datetime
import time

PROCESSED_DATA = {}


def read_csv_file(file_id: UUID) -> pd.DataFrame:
    """Read CSV file with error handling"""
    file_path = Path(f"data/{file_id}.csv")
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read CSV: {e}")


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean data and return cleaned DataFrame + cleaning stats"""
    # Clean column names
    df.columns = (
        df.columns
        .str.encode("ascii", errors="ignore")
        .str.decode("ascii")
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    df.rename(columns={"ordr_id": "order_id", "currncy": "currency"}, inplace=True)

    # Track cleaning stats
    blank_rows = df.isnull().all(axis=1).sum()
    df = df.dropna(how="all")

    duplicated_count = df.duplicated().sum()
    df = df.drop_duplicates()

    sanitised_count = 0
    if "sku" in df.columns:
        original_skus = df["sku"].copy()
        df["sku"] = df["sku"].astype(str).str.replace(r"[^\w\-]", "", regex=True)
        sanitised_count = (original_skus != df["sku"]).sum()

    malformed_rows = 0
    if {"item_price", "sku"}.issubset(df.columns):
        malformed_rows = df[["item_price", "sku"]].isnull().any(axis=1).sum()
    
    stats = {
        "blank_rows": blank_rows,
        "duplicated_count": duplicated_count,
        "sanitised_count": sanitised_count,
        "malformed_rows": malformed_rows
    }
    
    return df, stats


def build_metrics(df: pd.DataFrame, cleaning_stats: dict, duration: float, file_id: UUID) -> dict:
    """Build the metrics dictionary"""
    total_rows = len(df)
    formatted_processing = time.strftime("%H:%M:%S", time.gmtime(duration))
    
    existing = PROCESSED_DATA.get(str(file_id), {})
    download_seconds = existing.get("download_seconds", 0)
    formatted_download = existing.get("formatted_download", "00:00:00")

    return {
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "durations": {
            "download_seconds": int(download_seconds),
            "processing_seconds": int(duration),
            "total_seconds": int(download_seconds + duration),
            "formatted": {
                "download": formatted_download,
                "processing": formatted_processing
            }
        },
        "rows": {
            "total": total_rows,
            "blank": int(cleaning_stats["blank_rows"]),
            "malformed": int(cleaning_stats["malformed_rows"]),
            "encoding_errors": 0,
            "duplicated": int(cleaning_stats["duplicated_count"]),
            "sanitised": int(cleaning_stats["sanitised_count"]),
            "valid": total_rows,
            "usable": total_rows
        },
        "outcome": {
            "accepted": int(total_rows),
            "rejected": 0
        }
    }


def process_csv(file_id: UUID) -> dict:
    """Main function - now just orchestrates the steps"""
    start = time.time()
    
    # Read file
    df = read_csv_file(file_id)
    
    # Clean data
    cleaned_df, cleaning_stats = clean_data(df)
    
    # Build metrics
    duration = time.time() - start
    metrics = build_metrics(cleaned_df, cleaning_stats, duration, file_id)
    
    # Store results
    existing = PROCESSED_DATA.get(str(file_id), {})
    PROCESSED_DATA[str(file_id)] = {**existing, **metrics}
    
    return metrics