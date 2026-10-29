import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";

const require = createRequire(import.meta.url);
const M = require("../site/assets/market.js");

const years = [2020, 2021, 2022, 2023];

test("latest skips trailing gaps", () => {
  assert.deepEqual(M.latest([1, 2, null, null], years), { year: 2021, index: 1, value: 2 });
  assert.equal(M.latest([null, null], years), null);
});

test("change compares against the previous available year", () => {
  const ch = M.change([100, null, 110, null], years);
  assert.equal(ch.from, 2020);
  assert.equal(ch.abs, 10);
  assert.ok(Math.abs(ch.rel - 0.1) < 1e-9);
});

test("formats", () => {
  assert.equal(M.fmt(2.5e13, "usd_big"), "$25.00T");
  assert.equal(M.fmt(640e9, "usd_big"), "$640.0B");
  assert.equal(M.fmt(13456.7, "usd"), "$13,457");
  assert.equal(M.fmt(4.26, "pct"), "4.3%");
  assert.equal(M.fmt(45.8e6, "big"), "45.8M");
  assert.equal(M.fmt(null, "pct"), "n/a");
  assert.equal(M.fmtChange({ abs: -1.24, rel: -0.2 }, "pct"), "−1.2 pp");
  assert.equal(M.fmtChange({ abs: 5, rel: 0.05 }, "usd"), "+5.0%");
  assert.equal(M.fmtChange({ abs: -0.01, rel: 0 }, "pct"), "0.0 pp");
});

test("ranking excludes aggregates and stale values, and filters by region", () => {
  const data = {
    years,
    countries: [
      { iso3: "AAA", name: "A", region: "X" },
      { iso3: "BBB", name: "B", region: "Y" },
      { iso3: "CCC", name: "C", region: "X" },
      { iso3: "WLD", name: "World", region: "Aggregate" },
    ],
    values: { g: { AAA: [1, 2, 3, 4], BBB: [9, 9, 9, 9], CCC: [5, null, null, null], WLD: [7, 7, 7, 7] } },
  };
  const r = M.ranking(data, "g", { window: 1 });
  assert.deepEqual(r.map((x) => x.iso3), ["BBB", "AAA"]);
  assert.equal(r[1].rank, 2);
  assert.deepEqual(M.ranking(data, "g", { region: "X", window: 1 }).map((x) => x.iso3), ["AAA"]);
});

test("published data is complete", () => {
  const data = JSON.parse(readFileSync(new URL("../site/data.json", import.meta.url)));
  assert.equal(data.indicators.length, 8);
  assert.ok(data.countries.length > 150);
  assert.ok(data.countries.some((c) => c.iso3 === "WLD"));
  for (const ind of data.indicators) {
    const usa = data.values[ind.code].USA;
    assert.equal(usa.length, data.years.length, ind.code);
    assert.ok(M.latest(usa, data.years), `USA has data for ${ind.code}`);
  }
});
