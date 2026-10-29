"""Downloads the indicators and country metadata from the World Bank API into data/raw/."""
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from indicators import FIRST_YEAR, INDICATORS

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
API = "https://api.worldbank.org/v2"


def get(url: str, tries: int = 4) -> list:
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - network errors are retried, then re-raised
            if attempt == tries - 1:
                raise
            print(f"retry {attempt + 1} for {url}: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    last = date.today().year
    payloads = {"countries": get(f"{API}/country?format=json&per_page=400")}
    for ind in INDICATORS:
        payloads[ind["code"]] = get(f"{API}/country/all/indicator/{ind['code']}?format=json&per_page=20000&date={FIRST_YEAR}:{last}")
    # Write only after every download succeeded, so a partial failure keeps the previous snapshot intact.
    for name, payload in payloads.items():
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            raise SystemExit(f"Unexpected response for {name}")
        (RAW / f"{name}.json").write_text(json.dumps(payload))
    print("downloaded", len(payloads), "files")


if __name__ == "__main__":
    main()
