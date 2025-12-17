# threaded-fetcher

A small Python package that fetches many URLs concurrently using threads, records per-task timing, supports retries with exponential backoff, and optional rate limiting.

## Features
- ThreadPoolExecutor-based concurrency
- Per-task start/end timestamps and elapsed time
- Retries with exponential backoff
- Token-bucket rate limiter
- Load URLs from `.txt`, `.csv`, `.xlsx`, `.json`
- Save results to `.csv`, `.json`, `.xlsx` (multi-sheet summary), `.parquet`, `.feather`, `.sqlite`
- Auto-detect URL column names (e.g. `url`, `link`, `Career Page Link`)
- Colored console output and summary metrics

## Installation
Create and activate a virtualenv, then install:

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -e .
pip install openpyxl pyarrow colorama tqdm
