import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [persona, setPersona] = useState(null);
  const [personaError, setPersonaError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/personas/1`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setPersona)
      .catch((e) => setPersonaError(e.message));
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Header persona={persona} personaError={personaError} />
      <main className="max-w-5xl mx-auto px-6 pb-16">
        <StockAnalyzer />
      </main>
    </div>
  );
}

function Header({ persona, personaError }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
      <div className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Mahiro Invest</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            NSE stock analyzer powered by yfinance + screener.in
          </p>
        </div>
        <div className="text-right">
          {persona && (
            <>
              <div className="text-xs uppercase tracking-wider text-slate-500">Active persona</div>
              <div className="text-sm font-medium text-emerald-400">{persona.name}</div>
            </>
          )}
          {personaError && (
            <div className="text-xs text-red-400">Persona load failed: {personaError}</div>
          )}
        </div>
      </div>
    </header>
  );
}

function StockAnalyzer() {
  const [ticker, setTicker] = useState("RELIANCE.NS");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      // Step 1: refresh (fetches fresh data + saves snapshot)
      const refreshRes = await fetch(`${API_URL}/api/stocks/${ticker}/refresh`, { method: "POST" });
      if (!refreshRes.ok) {
        const body = await refreshRes.json().catch(() => ({}));
        throw new Error(body.detail || `Refresh failed: HTTP ${refreshRes.status}`);
      }

      // Step 2: evaluate against dad's persona
      const evalRes = await fetch(`${API_URL}/api/stocks/${ticker}/evaluate?persona_id=1`);
      if (!evalRes.ok) {
        const body = await evalRes.json().catch(() => ({}));
        throw new Error(body.detail || `Evaluate failed: HTTP ${evalRes.status}`);
      }
      setResult(await evalRes.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          NSE Ticker (use .NS suffix, e.g. <span className="text-emerald-400">RELIANCE.NS</span>)
        </label>
        <div className="flex gap-3">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase().trim())}
            onKeyDown={(e) => e.key === "Enter" && !loading && analyze()}
            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent font-mono"
            placeholder="TICKER.NS"
            disabled={loading}
          />
          <button
            onClick={analyze}
            disabled={loading || !ticker}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium px-6 py-2.5 rounded-lg transition-colors"
          >
            {loading ? "Analyzing…" : "Analyze"}
          </button>
        </div>
        {error && (
          <div className="mt-4 bg-red-950 border border-red-800 text-red-300 text-sm rounded-lg p-3">
            {error}
          </div>
        )}
      </div>

      {result && <ResultPanel result={result} />}
    </div>
  );
}

function ResultPanel({ result }) {
  const passColor = result.summary.verdict === "PASS" ? "emerald" : "red";
  return (
    <div className="space-y-6">
      <StockHeader result={result} passColor={passColor} />
      <FundamentalsGrid fundamentals={result.fundamentals} marketCap={result.market_cap_cr} />
      <CriteriaList evaluations={result.evaluations} />
      <Footer source={result.source} fetchedAt={result.fetched_at} />
    </div>
  );
}

function StockHeader({ result, passColor }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-wider">
            {result.sector} · {result.industry}
          </div>
          <h2 className="text-2xl font-bold mt-1">{result.name}</h2>
          <div className="text-sm text-slate-400 font-mono mt-1">{result.ticker}</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">
            vs. {result.persona.name}
          </div>
          <div
            className={`inline-flex items-center gap-2 text-lg font-bold px-4 py-1.5 rounded-full bg-${passColor}-950 border border-${passColor}-700 text-${passColor}-400`}
          >
            {result.summary.verdict}
          </div>
          <div className="text-xs text-slate-500 mt-2">
            {result.summary.pass} pass · {result.summary.fail} fail · {result.summary.skipped} skipped
          </div>
        </div>
      </div>
    </div>
  );
}

function FundamentalsGrid({ fundamentals, marketCap }) {
  const items = [
    { label: "Market Cap", value: fmtCr(marketCap), unit: "₹ Cr" },
    { label: "P/E Ratio", value: fmt(fundamentals.pe_ratio) },
    { label: "P/B Ratio", value: fmt(fundamentals.pb_ratio) },
    { label: "ROE", value: fmt(fundamentals.roe_pct), unit: "%" },
    { label: "Debt/Equity", value: fmt(fundamentals.debt_to_equity) },
    { label: "Quick Ratio", value: fmt(fundamentals.quick_ratio) },
    { label: "Revenue Growth", value: fmt(fundamentals.revenue_growth_yoy_pct), unit: "% YoY" },
    { label: "Profit Margin", value: fmt(fundamentals.profit_margin_pct), unit: "%" },
    { label: "EPS", value: fmt(fundamentals.eps), unit: "₹" },
    { label: "EPS Growth", value: fmt(fundamentals.eps_growth_pct), unit: "%" },
    { label: "Debtor Days", value: fmt(fundamentals.debtor_days) },
    { label: "Public Holding", value: fmt(fundamentals.public_holding_pct), unit: "%" },
  ];
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-4">
        Fundamentals
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {items.map((it) => (
          <div key={it.label}>
            <div className="text-xs text-slate-500">{it.label}</div>
            <div className="text-lg font-mono mt-0.5">
              {it.value}
              {it.unit && it.value !== "—" && <span className="text-slate-500 text-sm ml-1">{it.unit}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CriteriaList({ evaluations }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-4">
        Persona Criteria
      </h3>
      <div className="space-y-2">
        {evaluations.map((e, i) => (
          <CriterionRow key={i} evaluation={e} />
        ))}
      </div>
    </div>
  );
}

function CriterionRow({ evaluation }) {
  const config = {
    pass: { bg: "bg-emerald-950", border: "border-emerald-800", text: "text-emerald-400", icon: "✓" },
    fail: { bg: "bg-red-950", border: "border-red-800", text: "text-red-400", icon: "✗" },
    skipped: { bg: "bg-slate-800", border: "border-slate-700", text: "text-slate-500", icon: "—" },
  };
  const c = config[evaluation.status];
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
      <div className="flex items-center gap-3">
        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full ${c.bg} border ${c.border} ${c.text} text-xs font-bold`}>
          {c.icon}
        </span>
        <span className="text-sm">{evaluation.criterion}</span>
      </div>
      <div className="text-right text-sm">
        {evaluation.status === "skipped" ? (
          <span className="text-slate-500 italic text-xs">{evaluation.reason}</span>
        ) : (
          <>
            <span className="font-mono text-slate-300">{fmt(evaluation.value)}</span>
            <span className="text-slate-500 text-xs ml-2">{evaluation.rule}</span>
          </>
        )}
      </div>
    </div>
  );
}

function Footer({ source, fetchedAt }) {
  return (
    <div className="text-xs text-slate-500 text-center pt-2">
      Data source: <span className="text-slate-400 font-mono">{source}</span> · fetched{" "}
      {fetchedAt ? new Date(fetchedAt).toLocaleString() : "—"}
    </div>
  );
}

// ---- helpers ----
function fmt(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "boolean") return v ? "Yes" : "No";
  if (typeof v === "number") {
    if (Math.abs(v) >= 1000) return v.toLocaleString("en-IN", { maximumFractionDigits: 2 });
    return v.toFixed(2);
  }
  return String(v);
}

function fmtCr(v) {
  if (v === null || v === undefined) return "—";
  return v.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}