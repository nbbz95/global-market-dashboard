"""Turns the raw World Bank payloads into the compact site/data.json used by the dashboard."""
import json
from pathlib import Path

from indicators import FIRST_YEAR, INDICATORS

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
KEEP_AGGREGATES = {"WLD": "World"}


def load_countries() -> list[dict]:
    rows = json.loads((RAW / "countries.json").read_text())[1]
    out = []
    for c in rows:
        is_aggregate = c["region"]["id"] == "NA"
        if is_aggregate and c["id"] not in KEEP_AGGREGATES:
            continue
        out.append({
            "iso3": c["id"],
            "name": KEEP_AGGREGATES.get(c["id"], c["name"]),
            "region": "Aggregate" if is_aggregate else c["region"]["value"].strip(),
            "income": "" if is_aggregate else c["incomeLevel"]["value"].strip(),
        })
    return sorted(out, key=lambda c: (c["region"] == "Aggregate", c["name"]))


def build() -> dict:
    countries = load_countries()
    iso = {c["iso3"] for c in countries}
    series: dict[str, dict[str, dict[int, float]]] = {}
    last_year = FIRST_YEAR
    updated = ""
    for ind in INDICATORS:
        meta, rows = json.loads((RAW / f"{ind['code']}.json").read_text())
        updated = max(updated, meta.get("lastupdated", ""))
        s = series.setdefault(ind["code"], {})
        for r in rows:
            if r["value"] is None or r["countryiso3code"] not in iso:
                continue
            y = int(r["date"])
            s.setdefault(r["countryiso3code"], {})[y] = r["value"]
            last_year = max(last_year, y)
    years = list(range(FIRST_YEAR, last_year + 1))

    def row(code, c):
        d = series[code].get(c, {})
        return [None if y not in d else round(d[y], 4 if abs(d[y]) < 1000 else 0) for y in years]

    # Drop countries with no data at all (small territories).
    countries = [c for c in countries if any(series[i["code"]].get(c["iso3"]) for i in INDICATORS)]
    return {
        "source": "World Bank, World Development Indicators",
        "updated": updated,
        "years": years,
        "indicators": INDICATORS,
        "countries": countries,
        "values": {i["code"]: {c["iso3"]: row(i["code"], c["iso3"]) for c in countries} for i in INDICATORS},
    }


if __name__ == "__main__":
    data = build()
    (ROOT / "site" / "data.json").write_text(json.dumps(data, separators=(",", ":")))
    print(len(data["countries"]), "countries,", data["years"][0], "-", data["years"][-1], "| WDI updated", data["updated"])
