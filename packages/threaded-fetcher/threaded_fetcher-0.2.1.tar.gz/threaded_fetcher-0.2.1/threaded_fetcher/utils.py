import threading
import time
import csv
import json
import sqlite3
import pandas as pd
from pathlib import Path


def _auto_detect_url_column(df: pd.DataFrame, requested: str | None = None) -> str:
    """
    Try to find a reasonable column that contains URLs.
    - First try the requested name (case-insensitive).
    - Then look for columns containing 'url' or 'link' in their name.
    - If nothing matches, raise ValueError.
    """
    cols = list(df.columns)

    # 1) Case-insensitive exact match for requested
    if requested:
        for c in cols:
            if c.lower() == requested.lower():
                return c

    # 2) Look for anything with 'url' or 'link' in the name
    lower_map = {c.lower(): c for c in cols}
    keywords = ["url", "link"]

    for key in keywords:
        for col_lower, original in lower_map.items():
            if key in col_lower:
                return original

    # 3) Nothing found → fail with a clear message
    raise ValueError(
        f"Could not auto-detect URL column. Tried '{requested}'. "
        f"Available columns: {cols}"
    )


def load_urls(path: Path, column: str = "url") -> list[str]:
    """
    Load URLs from different file formats:
    - .txt  -> one URL per line
    - .csv  -> column with URLs (default: 'url' or auto-detected)
    - .xlsx -> Excel column with URLs (default: 'url' or auto-detected)
    - .json -> list of strings OR list of objects with URL-like key
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = path.suffix.lower()

    # 1) Plain text: one URL per line
    if suffix == ".txt":
        return [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    # 2) CSV file
    if suffix == ".csv":
        df = pd.read_csv(path)
        col_to_use = _auto_detect_url_column(df, requested=column)
        return df[col_to_use].dropna().astype(str).tolist()

    # 3) Excel file
    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
        col_to_use = _auto_detect_url_column(df, requested=column)
        return df[col_to_use].dropna().astype(str).tolist()

    # 4) JSON file (optional, simple support)
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))

        # if it's a list of strings
        if isinstance(data, list) and all(isinstance(x, str) for x in data):
            return data

        # if it's a list of dicts – auto-detect key using same logic
        if isinstance(data, list) and all(isinstance(x, dict) for x in data) and data:
            keys = list(data[0].keys())
            fake_df = pd.DataFrame(columns=keys)
            col_to_use = _auto_detect_url_column(fake_df, requested=column)
            return [
                item[col_to_use]
                for item in data
                if col_to_use in item and item[col_to_use]
            ]

        raise ValueError("Unsupported JSON structure for URLs")

    raise ValueError(f"Unsupported file type: {suffix}")


def write_csv(rows, path):
    if not rows:
        # nothing to write; create an empty file
        Path(path).write_text("", encoding="utf-8")
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_json(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

def write_parquet(rows, path):
    df = pd.DataFrame(rows)
    df.to_parquet(path, index=False)

def write_feather(rows, path):
    df = pd.DataFrame(rows)
    df.to_feather(path)

def write_xlsx(rows, path):
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)

def write_sqlite(rows, path, table_name="results"):
    df = pd.DataFrame(rows)
    conn = sqlite3.connect(path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

class RateLimiter:
    """Simple token-bucket rate limiter."""
    def __init__(self, rate_per_sec: float):
        if rate_per_sec <= 0:
            raise ValueError("rate_per_sec must be > 0")
        self.rate = float(rate_per_sec)
        self._lock = threading.Lock()
        self._tokens = float(rate_per_sec)
        self._last = time.perf_counter()

    def acquire(self):
        with self._lock:
            now = time.perf_counter()
            elapsed = now - self._last
            self._tokens = min(self.rate, self._tokens + elapsed * self.rate)
            self._last = now

            if self._tokens >= 1:
                self._tokens -= 1
                return

            wait = (1 - self._tokens) / self.rate

        time.sleep(wait)

        with self._lock:
            self._tokens = max(0.0, self._tokens - 1)
            self._last = time.perf_counter()
