"""Indicators shown on the dashboard (World Bank WDI codes)."""

INDICATORS = [
    {"code": "NY.GDP.MKTP.CD", "name": "GDP", "unit": "current US$", "format": "usd_big", "higher_is_better": True},
    {"code": "NY.GDP.MKTP.KD.ZG", "name": "GDP growth", "unit": "annual %", "format": "pct", "higher_is_better": True},
    {"code": "NY.GDP.PCAP.CD", "name": "GDP per capita", "unit": "current US$", "format": "usd", "higher_is_better": True},
    {"code": "FP.CPI.TOTL.ZG", "name": "Inflation", "unit": "consumer prices, annual %", "format": "pct", "higher_is_better": False},
    {"code": "SL.UEM.TOTL.ZS", "name": "Unemployment", "unit": "% of labor force (ILO)", "format": "pct", "higher_is_better": False},
    {"code": "BN.CAB.XOKA.GD.ZS", "name": "Current account", "unit": "% of GDP", "format": "pct", "higher_is_better": True},
    {"code": "NE.EXP.GNFS.ZS", "name": "Exports", "unit": "goods and services, % of GDP", "format": "pct", "higher_is_better": True},
    {"code": "SP.POP.TOTL", "name": "Population", "unit": "people", "format": "big", "higher_is_better": None},
]

FIRST_YEAR = 2000
