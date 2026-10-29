import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import build  # noqa: E402
from indicators import INDICATORS  # noqa: E402


@pytest.fixture
def raw(tmp_path, monkeypatch):
    countries = [{"page": 1}, [
        {"id": "ARG", "name": "Argentina", "region": {"id": "LCN", "value": "Latin America & Caribbean "}, "incomeLevel": {"value": "Upper middle income"}},
        {"id": "WLD", "name": "World", "region": {"id": "NA", "value": "Aggregates"}, "incomeLevel": {"value": "Aggregates"}},
        {"id": "EUU", "name": "European Union", "region": {"id": "NA", "value": "Aggregates"}, "incomeLevel": {"value": "Aggregates"}},
        {"id": "XXX", "name": "No data land", "region": {"id": "LCN", "value": "Latin America & Caribbean"}, "incomeLevel": {"value": "High income"}},
    ]]
    (tmp_path / "countries.json").write_text(json.dumps(countries))
    for ind in INDICATORS:
        rows = [
            {"countryiso3code": "ARG", "date": "2001", "value": 1234.5678},
            {"countryiso3code": "ARG", "date": "2003", "value": 2.345678},
            {"countryiso3code": "WLD", "date": "2002", "value": None},
            {"countryiso3code": "EUU", "date": "2002", "value": 9.0},
        ]
        (tmp_path / f"{ind['code']}.json").write_text(json.dumps([{"lastupdated": "2026-01-01"}, rows]))
    monkeypatch.setattr(build, "RAW", tmp_path)


def test_build_keeps_countries_and_world_only(raw):
    d = build.build()
    assert [c["iso3"] for c in d["countries"]] == ["ARG"]  # WLD has no values here, EUU is an aggregate we drop, XXX has no data
    assert d["countries"][0]["region"] == "Latin America & Caribbean"


def test_series_are_aligned_to_years(raw):
    d = build.build()
    assert d["years"] == [2000, 2001, 2002, 2003]
    s = d["values"][INDICATORS[0]["code"]]["ARG"]
    assert s == [None, 1235.0, None, 2.3457]
    assert d["updated"] == "2026-01-01"


def test_published_snapshot_is_valid():
    d = json.loads((Path(build.ROOT) / "site" / "data.json").read_text())
    assert {i["code"] for i in d["indicators"]} == {i["code"] for i in INDICATORS}
    assert all(len(v) == len(d["years"]) for s in d["values"].values() for v in s.values())
