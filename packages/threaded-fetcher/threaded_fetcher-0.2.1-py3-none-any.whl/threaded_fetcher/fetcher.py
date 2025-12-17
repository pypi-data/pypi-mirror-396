from __future__ import annotations

import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable

import requests

from .utils import RateLimiter


class Fetcher:
    """Threaded URL fetcher with retries, timing and optional rate limiting."""

    def __init__(
        self,
        max_workers: int = 10,
        timeout: int = 10,
        retries: int = 2,
        backoff_factor: float = 0.5,
        rate_per_sec: Optional[float] = None,
        session_factory: Optional[Callable[[], requests.Session]] = None,
    ):
        self.max_workers = max_workers
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.rate_limiter = RateLimiter(rate_per_sec) if rate_per_sec else None
        self._results = []
        self._lock = threading.Lock()
        self._session_factory = session_factory or requests.Session

    def _fetch_one(self, url: str, idx: int) -> Dict:
        thread_name = threading.current_thread().name

        if self.rate_limiter:
            self.rate_limiter.acquire()

        start_wall = datetime.utcnow()
        start_perf = time.perf_counter()

        last_exc = None
        status = None
        text_len = None

        session = self._session_factory()
        attempts = 0

        for attempt in range(1, self.retries + 2):
            attempts = attempt
            try:
                resp = session.get(url, timeout=self.timeout)
                status = resp.status_code
                text_len = len(resp.content or b"")
                last_exc = None
                break
            except Exception as exc:
                last_exc = exc
                time.sleep(self.backoff_factor * (2 ** (attempt - 1)))

        end_perf = time.perf_counter()
        end_wall = datetime.utcnow()

        # classify status for easier reading
        status_value = status if status is not None else "error"
        error_text = repr(last_exc) if last_exc else None

        if error_text is not None or status is None:
            status_class = "network_error"
            ok = False
        elif isinstance(status, int) and 200 <= status < 300:
            status_class = "success"
            ok = True
        elif isinstance(status, int) and 300 <= status < 400:
            status_class = "redirect"
            ok = True  # often OK, but you can set False if you prefer
        elif isinstance(status, int) and 400 <= status < 500:
            status_class = "client_error"
            ok = False
        elif isinstance(status, int) and 500 <= status < 600:
            status_class = "server_error"
            ok = False
        else:
            status_class = "unknown"
            ok = False

        record = {
            "index": idx,
            "url": url,
            "thread": thread_name,
            "status": status_value,
            "status_class": status_class,  # NEW
            "ok": ok,                      # NEW
            "error": error_text,
            "text_len": text_len,
            "start_iso": start_wall.isoformat() + "Z",
            "end_iso": end_wall.isoformat() + "Z",
            "elapsed_s": end_perf - start_perf,
            "attempts": attempts,
        }


        with self._lock:
            self._results.append(record)

        return record

    def fetch(self, urls: List[str]) -> List[Dict]:
        """Fetch list of URLs concurrently."""
        self._results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_one, url, idx): idx
                for idx, url in enumerate(urls)
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    with self._lock:
                        self._results.append(
                            {"index": futures[future], "url": "<unknown>", "error": repr(e)}
                        )

        return sorted(self._results, key=lambda r: r["index"])
