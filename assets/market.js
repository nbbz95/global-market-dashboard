// Pure helpers for the dashboard (no DOM). Tested with node --test.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Market = factory();
})(typeof self !== "undefined" ? self : this, function () {
  // Latest non-null value at or before maxYearIndex.
  function latest(values, years, maxYearIndex = values.length - 1) {
    for (let i = maxYearIndex; i >= 0; i--) if (values[i] != null) return { year: years[i], index: i, value: values[i] };
    return null;
  }

  // Change against the previous available year.
  function change(values, years) {
    const now = latest(values, years);
    if (!now) return null;
    const before = latest(values, years, now.index - 1);
    if (!before) return null;
    return { from: before.year, abs: now.value - before.value, rel: before.value ? now.value / before.value - 1 : null };
  }

  // Ranking for one indicator: uses each country's latest value within `window` years of the newest year with data.
  function ranking(data, code, { region = null, window = 2 } = {}) {
    const lastIdx = data.years.length - 1;
    const rows = [];
    for (const c of data.countries) {
      if (c.region === "Aggregate") continue;
      if (region && c.region !== region) continue;
      const l = latest(data.values[code][c.iso3] || [], data.years);
      if (l && l.index >= lastIdx - window) rows.push({ iso3: c.iso3, name: c.name, year: l.year, value: l.value });
    }
    rows.sort((a, b) => b.value - a.value);
    rows.forEach((r, i) => (r.rank = i + 1));
    return rows;
  }

  function sliceYears(data, fromYear) {
    const start = Math.max(0, data.years.indexOf(fromYear));
    return { start, years: data.years.slice(start) };
  }

  function fmt(value, kind, { compact = true } = {}) {
    if (value == null || !isFinite(value)) return "n/a";
    const abs = Math.abs(value);
    const short = (v, d = 1) => {
      if (abs >= 1e12) return (v / 1e12).toFixed(d) + "T";
      if (abs >= 1e9) return (v / 1e9).toFixed(d) + "B";
      if (abs >= 1e6) return (v / 1e6).toFixed(d) + "M";
      if (abs >= 1e3) return (v / 1e3).toFixed(d) + "K";
      return v.toFixed(0);
    };
    switch (kind) {
      case "pct": return value.toFixed(1) + "%";
      case "usd_big": return "$" + short(value, abs >= 1e12 ? 2 : 1);
      case "usd": return "$" + (compact && abs >= 1e5 ? short(value) : Math.round(value).toLocaleString("en-US"));
      case "big": return short(value);
      default: return value.toLocaleString("en-US");
    }
  }

  // Wording for a change: percentage points for rates, % for levels.
  function fmtChange(ch, kind) {
    if (!ch) return null;
    if (kind === "pct") return Math.abs(ch.abs) < 0.05 ? "0.0 pp" : (ch.abs >= 0 ? "+" : "−") + Math.abs(ch.abs).toFixed(1) + " pp";
    if (ch.rel == null) return null;
    return (ch.rel >= 0 ? "+" : "−") + Math.abs(ch.rel * 100).toFixed(1) + "%";
  }

  return { latest, change, ranking, sliceYears, fmt, fmtChange };
});
