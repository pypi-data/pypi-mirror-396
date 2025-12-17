import argparse
import csv
from pathlib import Path

from colorama import init as colorama_init, Fore, Style

from threaded_fetcher.utils import write_json, write_xlsx, load_urls, write_sqlite, write_parquet, write_feather
from .fetcher import Fetcher

colorama_init(autoreset=True)

def format_result_colored(rec: dict) -> str:
    """
    Return a one-line colored summary for a single result record.
    """
    status = rec.get("status")
    error = rec.get("error")
    url = rec.get("url")
    elapsed = rec.get("elapsed_s", 0.0)
    thread = rec.get("thread", "")

    # Decide color based on status / error
    if error is not None or status == "error":
        color = Fore.RED
        label = "ERROR"
    elif isinstance(status, int) and 200 <= status < 300:
        color = Fore.GREEN
        label = "OK"
    elif isinstance(status, int) and 300 <= status < 400:
        color = Fore.CYAN
        label = "REDIRECT"
    elif isinstance(status, int) and 400 <= status < 500:
        color = Fore.YELLOW
        label = "CLIENT"
    elif isinstance(status, int) and 500 <= status < 600:
        color = Fore.RED
        label = "SERVER"
    else:
        color = Fore.MAGENTA
        label = "UNKNOWN"

    base = (
        f"[{thread}] {url} -> status={status} "
        f"({elapsed:.3f}s) [{label}]"
    )
    return f"{color}{base}{Style.RESET_ALL}"
def print_summary(results: list[dict]) -> None:
    total = len(results)
    successes = 0
    client_err = 0
    server_err = 0
    other_err = 0

    total_time = 0.0

    for r in results:
        status = r.get("status")
        err = r.get("error")
        elapsed = r.get("elapsed_s", 0.0)
        total_time += elapsed

        if err is not None or status == "error":
            other_err += 1
        elif isinstance(status, int) and 200 <= status < 300:
            successes += 1
        elif isinstance(status, int) and 400 <= status < 500:
            client_err += 1
        elif isinstance(status, int) and 500 <= status < 600:
            server_err += 1
        else:
            other_err += 1

    avg_time = total_time / total if total > 0 else 0.0

    print("\n" + "-" * 60)
    print(f"Total URLs    : {total}")
    print(f"{Fore.GREEN}Success 2xx   : {successes}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Client 4xx    : {client_err}{Style.RESET_ALL}")
    print(f"{Fore.RED}Server 5xx    : {server_err}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Other / errors: {other_err}{Style.RESET_ALL}")
    print(f"Avg elapsed   : {avg_time:.3f}s")
    print("-" * 60)

def parse_args():
    p = argparse.ArgumentParser(prog="threaded-fetcher", description="Fetch multiple URLs concurrently.")
    p.add_argument("urls_file", type=Path, help="Plain file with one URL per line")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--retries", type=int, default=1)
    p.add_argument("--backoff", type=float, default=0.5)
    p.add_argument("--rate", type=float, default=None)
    p.add_argument("--format", choices=["csv", "json", "xlsx", "parquet", "feather", "sqlite"], default="csv")
    p.add_argument("--output", type=Path, default=None)
    p.add_argument(
        "--column",
        type=str,
        default="url",
        help="Column name to read URLs from (for CSV/Excel/JSON with objects)",
    )
    return p.parse_args()

def write_csv(rows, path):
    fieldnames = ["index","url","status","error","text_len","start_iso","end_iso","elapsed_s","attempts","thread"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})



def main():
    args = parse_args()

    input_path = Path(args.urls_file)
    urls = load_urls(input_path, column=args.column)

    if not urls:
        raise SystemExit("No URLs loaded from input file.")

    f = Fetcher(
        max_workers=args.workers,
        timeout=args.timeout,
        retries=args.retries,
        backoff_factor=args.backoff,
        rate_per_sec=args.rate,
    )

    results = f.fetch(urls)

    print(f"Fetched {len(results)} URLs.")

    for rec in results:
        print(format_result_colored(rec))

        # 2) Summary at the end
    print_summary(results)

    if args.output:
        if args.format == "csv":
            write_csv(results, args.output)
        elif args.format == "json":
            write_json(results, args.output)
        elif args.format == "xlsx":
            write_xlsx(results, args.output)
        elif args.format == "parquet":
            write_parquet(results, args.output)
        elif args.format == "feather":
            write_feather(results, args.output)
        elif args.format == "sqlite":
            write_sqlite(results, args.output)

        print(f"\nSaved results to: {args.output}")

if __name__ == "__main__":
    main()
