# Global Market Indicators

**Live dashboard:** https://nbbz95.github.io/global-market-dashboard/

An interactive dashboard of the macro indicators most used to compare markets internationally, for 200+ economies, with World Bank data refreshed automatically.

| Indicator | World Bank code |
|---|---|
| GDP (current US$) | `NY.GDP.MKTP.CD` |
| GDP growth (annual %) | `NY.GDP.MKTP.KD.ZG` |
| GDP per capita (current US$) | `NY.GDP.PCAP.CD` |
| Inflation, consumer prices (annual %) | `FP.CPI.TOTL.ZG` |
| Unemployment (% of labor force, ILO) | `SL.UEM.TOTL.ZS` |
| Current account balance (% of GDP) | `BN.CAB.XOKA.GD.ZS` |
| Exports of goods and services (% of GDP) | `NE.EXP.GNFS.ZS` |
| Population | `SP.POP.TOTL` |

## Features

- **Country filter** grouped by region, plus up to three countries (or the World aggregate) to compare against.
- **KPI cards** with the latest value, change against the previous year (percentage points for rates, % for levels), sparkline and global rank. Click a card to chart it.
- **Trend chart** for 10, 15 or 25 years with a hover crosshair.
- **Ranking** worldwide or within the country's region, always showing where the selected country sits.
- **Side-by-side table** of every indicator for the selected countries.
- The view is stored in the URL, so a comparison can be shared as a link. Light and dark mode, works on phones.

## How it works

```
src/indicators.py   the indicator list (add a WDI code here to extend the dashboard)
src/fetch.py        downloads the series from the World Bank API (with retries)
src/build.py        normalizes them into a compact site/data.json (~400 KB)
site/assets/market.js  ranking, latest value and change logic, no DOM
site/index.html     the dashboard (HTML + SVG, no framework)
tests/              pytest for the data build, node:test for the dashboard logic
```

A GitHub Actions workflow runs every Monday: it fetches fresh data, rebuilds, runs the tests and deploys to the `gh-pages` branch. If the API is down, it deploys the last committed snapshot and leaves a warning instead of failing.

```bash
pip install -r requirements.txt
python src/fetch.py && python src/build.py
python -m pytest -q && node --test tests/*.test.mjs
python -m http.server -d site
```

**Source:** World Bank, [World Development Indicators](https://databank.worldbank.org/source/world-development-indicators) (CC BY 4.0).
