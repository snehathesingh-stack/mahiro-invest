import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowUpDown,
  BarChart3,
  Bell,
  Bookmark,
  CalendarDays,
  CheckCircle2,
  Edit3,
  Eye,
  ExternalLink,
  ListPlus,
  LogOut,
  PieChart as PieIcon,
  Play,
  Plus,
  Save,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Wallet,
} from "lucide-react";
import { Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import logoUrl from "../../assets/logo.jpg";

const API_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`;
const COLORS = ["#0f766e", "#b45309", "#2563eb", "#be123c", "#4d7c0f", "#7c3aed"];
const DEFAULT_QUALITY_CRITERIA = {
  hard_filters: {
    market_cap_cr: { min: 5000 },
    eps_trend: { lookback_years: 5, must_trend_up: true },
    revenue_growth_yoy: { min: 10, sustained_years: 3 },
    profit_margin: { positive: true },
    debt_to_equity: { max: 1 },
    roe: { min: 15 },
    cash_flow_from_operations: { positive: true, growing_yoy: true },
    debtor_days: { max: 100 },
    fii_holding_pct: { min: 0, max: 100 },
    dii_holding_pct: { min: 0, max: 100 },
    public_holding_pct: { min: 0, max: 100 },
    moving_average_signal: { ma20_above_ma200: true },
    dividend_yield: { nice_to_have: true },
  },
  ranking_weights: {},
  portfolio_alerts: { on_hard_filter_violation: "SELL IMMEDIATELY" },
  earnings_strategy: { buy_decisions: "before_earnings", post_earnings: "rerun_persona" },
};
const NAV = [
  ["dashboard", BarChart3, "Dashboard"],
  ["screener", Search, "Screener"],
  ["portfolio", Wallet, "Portfolio"],
  ["earnings", CalendarDays, "Earnings"],
  ["personas", Edit3, "Persona"],
];
const PERSONA_PRESETS = ["Conservative", "Growth", "Dividend", "Momentum", "Banking-focused"];
const SORT_OPTIONS = [
  ["score", "Score"],
  ["market_cap", "Market cap"],
  ["roe", "ROE"],
  ["revenue", "Revenue growth"],
  ["debt", "Debt/equity"],
  ["verdict", "Pass/fail"],
];

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("mahiro_token"));
  const [user, setUser] = useState(null);
  const [active, setActive] = useState("dashboard");
  const api = useMemo(() => makeApi(token), [token]);

  useEffect(() => {
    if (!token) return;
    api("/auth/me").then(setUser).catch(() => logout());
  }, [token]);

  function onAuth(data) {
    localStorage.setItem("mahiro_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  }

  function logout() {
    localStorage.removeItem("mahiro_token");
    setToken(null);
    setUser(null);
  }

  if (!token) return <AuthPage onAuth={onAuth} />;

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="px-6 py-7 border-b border-amber-500/20">
          <BrandBlock />
        </div>
        <nav className="p-4 space-y-1">
          {NAV.map(([id, Icon, label]) => (
            <button key={id} title={label} onClick={() => setActive(id)} className={`nav-button ${active === id ? "nav-active" : ""}`}>
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>
      <main className="lg:pl-72">
        <header className="app-header">
          <div className="mx-auto flex max-w-[1500px] items-center justify-between px-4 py-4 lg:px-8">
            <div>
              <div className="text-sm text-stone-400">Signed in as {user?.name || "Investor"}</div>
              <h1 className="text-xl font-semibold text-stone-100">{NAV.find((n) => n[0] === active)?.[2]}</h1>
            </div>
            <div className="flex items-center gap-2">
              <select className="lg:hidden input" value={active} onChange={(e) => setActive(e.target.value)}>
                {NAV.map(([id, , label]) => <option key={id} value={id}>{label}</option>)}
              </select>
              <button title="Sign out" className="icon-button" onClick={logout}><LogOut size={18} /></button>
            </div>
          </div>
        </header>
        <div className="mx-auto max-w-[1500px] px-4 py-6 lg:px-8">
          {active === "dashboard" && <Dashboard api={api} setActive={setActive} user={user} />}
          {active === "screener" && <Screener api={api} />}
          {active === "portfolio" && <Portfolio api={api} />}
          {active === "earnings" && <Earnings api={api} />}
          {active === "personas" && <Personas api={api} />}
        </div>
      </main>
    </div>
  );
}

function BrandBlock({ compact = false }) {
  return (
    <div className={compact ? "flex items-center gap-3" : "flex items-center gap-4"}>
      <img className={compact ? "brand-logo-sm" : "brand-logo"} src={logoUrl} alt="Mahiro Invest" />
      <div>
        <div className={compact ? "brand-title text-xl" : "brand-title text-2xl leading-tight"}>Mahiro Invest</div>
        <div className="mt-1 max-w-44 text-sm leading-snug text-stone-400">Personal NSE quality screener</div>
      </div>
    </div>
  );
}

function AuthPage({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await rawApi(`/auth/${mode}`, { method: "POST", body: form });
      onAuth(data);
    } catch (err) {
      setError(err.message);
    }
  }
  return (
    <div className="min-h-screen grid place-items-center bg-[#08090a] px-4 text-white">
      <form onSubmit={submit} className="premium-card w-full max-w-md p-6 shadow-2xl">
        <div className="mb-5">
          <BrandBlock compact />
        </div>
        {mode === "register" && <input className="auth-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Name" />}
        <input className="auth-input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" />
        <input className="auth-input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" />
        {error && <div className="mb-3 rounded border border-red-800 bg-red-950 p-2 text-sm text-red-200">{error}</div>}
        <button className="primary-button w-full">{mode === "login" ? "Login" : "Register"}</button>
        <button type="button" className="mt-3 w-full text-sm text-zinc-400" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Create an account" : "Use existing account"}
        </button>
      </form>
    </div>
  );
}

function Dashboard({ api, setActive, user }) {
  const { data: portfolio, load: loadPortfolio } = useLoad(() => api("/portfolio/"), []);
  const { data: alerts, load: loadAlerts } = useLoad(() => api("/alerts/"), []);
  const { data: earnings, load: loadEarnings } = useLoad(() => api("/earnings/upcoming?days=30"), []);
  useEffect(() => { loadPortfolio(); loadAlerts(); loadEarnings(); }, []);
  return (
    <div className="space-y-6">
      <section className="welcome-row">
        <div>
          <h2 className="premium-heading">Welcome back, {user?.name || "Investor"}</h2>
          <p className="text-stone-400">Smart filters. Sharp decisions. Cleaner investing workflow.</p>
        </div>
        <button className="gold-button" onClick={() => setActive("screener")}><Play size={18} /> Run Screener</button>
      </section>
      <section className="hero-band">
        <img className="hero-logo" src={logoUrl} alt="Mahiro Invest" />
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded border border-amber-500/30 bg-amber-500/10 px-2 py-1 text-xs font-medium text-amber-200">
            <Sparkles size={14} /> 16 active quality criteria
          </div>
          <h2 className="mt-4 text-3xl font-semibold text-stone-100">Quality Investing OS</h2>
          <p className="mt-2 text-stone-300">Filter NSE stocks using your own rules, compare pass/fail criteria, and track opportunities before earnings.</p>
          <div className="mt-5 flex flex-wrap gap-3">
            <button className="gold-button" onClick={() => setActive("screener")}><Play size={18} /> Run Screener</button>
            <button className="dark-button" onClick={() => setActive("screener")}>View Opportunities</button>
          </div>
        </div>
      </section>
      <Stats stats={portfolio?.stats} />
      <section className="grid items-start gap-4 xl:grid-cols-[1fr_1fr]">
        <Panel title="Top Alerts" icon={Bell}>
          <AlertList alerts={alerts || []} />
        </Panel>
        <Panel title="Earnings This Week" icon={CalendarDays}>
          <EarningsList items={(earnings || []).filter((e) => e.is_this_week)} compact />
        </Panel>
      </section>
      <button className="gold-button" onClick={() => setActive("screener")}><Play size={18} /> Run Screener</button>
    </div>
  );
}

function Screener({ api }) {
  const [personas, setPersonas] = useState([]);
  const [personaId, setPersonaId] = useState("");
  const [draft, setDraft] = useState(null);
  const [results, setResults] = useState([]);
  const [savedScreens, setSavedScreens] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sectorFilters, setSectorFilters] = useState([]);
  const [sortBy, setSortBy] = useState("score");
  const [sortDir, setSortDir] = useState("desc");
  const [message, setMessage] = useState("");
  const debouncedDraft = useDebounce(draft, 700);
  useEffect(() => {
    api("/personas/").then((p) => {
      setPersonas(p);
      setPersonaId(p[0]?.id || "");
      setDraft(p[0] ? clone(p[0]) : null);
    });
    api("/screener/saved").then(setSavedScreens).catch(() => setSavedScreens([]));
  }, []);
  useEffect(() => {
    const next = personas.find((p) => String(p.id) === String(personaId));
    setDraft(next ? clone(next) : null);
  }, [personaId]);
  useEffect(() => {
    if (!debouncedDraft?.id) return;
    run({ auto: true });
  }, [debouncedDraft]);

  async function savePersona({ updateDraft = true } = {}) {
    if (!draft) return null;
    const saved = await api(`/personas/${draft.id}`, { method: "PUT", body: draft });
    setPersonas((current) => current.map((p) => (p.id === saved.id ? saved : p)));
    if (updateDraft) setDraft(clone(saved));
    return saved;
  }

  async function run({ auto = false } = {}) {
    setLoading(true);
    setMessage(auto ? "Applying filters..." : "");
    try {
      const saved = await savePersona({ updateDraft: !auto });
      const data = await api("/screener/run", { method: "POST", body: { persona_id: Number(saved?.id || personaId) } });
      setResults(data.results);
      setSelected((current) => current ? data.results.find((r) => r.symbol === current.symbol) || data.results[0] : data.results[0]);
      setMessage(auto ? "Filters applied live." : "Screener run complete.");
    } catch (err) {
      setMessage(err.message || "Could not run screener.");
    } finally {
      setLoading(false);
    }
  }
  async function createPreset(name) {
    const persona = await api("/personas/preset", { method: "POST", body: { name } });
    const next = await api("/personas/");
    setPersonas(next);
    setPersonaId(persona.id);
    setDraft(clone(persona));
    setMessage(`${persona.name} profile created.`);
  }
  async function duplicateCurrent() {
    if (!personaId) return;
    const persona = await api(`/personas/${personaId}/duplicate`, { method: "POST" });
    const next = await api("/personas/");
    setPersonas(next);
    setPersonaId(persona.id);
    setDraft(clone(persona));
    setMessage("Profile duplicated.");
  }
  async function saveScreen() {
    const name = window.prompt("Save this screen as", "Today's shortlist");
    if (!name) return;
    const saved = await api("/screener/saved", { method: "POST", body: { name, persona_id: Number(personaId), results: visibleResults } });
    setSavedScreens((items) => [saved, ...items]);
    setMessage(`Saved ${saved.name}.`);
  }
  async function addToWatchlist(stock) {
    const lists = await api("/watchlists/");
    const list = lists[0] || await api("/watchlists/", { method: "POST", body: { name: "Screener Picks", stock_ids: [] } });
    const stock_ids = Array.from(new Set([...(list.stock_ids || []), stock.symbol]));
    await api(`/watchlists/${list.id}`, { method: "PUT", body: { name: list.name, stock_ids } });
    setMessage(`${stock.symbol} added to ${list.name}.`);
  }
  async function addToPortfolio(stock) {
    await api("/portfolio/", { method: "POST", body: { symbol: stock.symbol, quantity: 1, avg_buy_price: stock.last_price || 0 } });
    setMessage(`${stock.symbol} added to portfolio with quantity 1.`);
  }
  const sectors = [...new Set(results.map((r) => r.sector || "Unknown"))].sort();
  const visibleResults = results.filter((r) => {
    const matchesText = `${r.company_name} ${r.symbol}`.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || r.summary.verdict.toLowerCase() === statusFilter;
    const matchesSector = !sectorFilters.length || sectorFilters.includes(r.sector || "Unknown");
    return matchesText && matchesStatus && matchesSector;
  }).sort((a, b) => sortResults(a, b, sortBy, sortDir));
  return (
    <div className="space-y-5">
      <section className="screener-shell">
        <aside className="filter-sidebar">
          <div className="mb-4 flex items-center gap-2 text-lg font-semibold">
            <SlidersHorizontal size={20} className="text-teal-800" /> Filters
          </div>
          <label className="field-label mb-4">
            <span>Investor persona</span>
            <select className="input w-full" value={personaId} onChange={(e) => setPersonaId(e.target.value)}>
              {personas.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </label>
          <div className="mb-4 flex gap-2">
            <button className="secondary-button flex-1" type="button" onClick={duplicateCurrent}>Duplicate</button>
            <select className="input min-w-0 flex-1" defaultValue="" onChange={(e) => e.target.value && createPreset(e.target.value)}>
              <option value="">Create preset</option>
              {PERSONA_PRESETS.map((preset) => <option key={preset} value={preset}>{preset}</option>)}
            </select>
          </div>
          {draft && <PreferenceEditor persona={draft} onChange={setDraft} compact />}
          <Facet title="Result View">
            <ChipGroup
              value={statusFilter}
              options={[
                ["all", "All"],
                ["pass", "Pass"],
                ["fail", "Fail"],
              ]}
              onChange={setStatusFilter}
            />
          </Facet>
          <Facet title="Sector">
            <MultiCheck options={sectors} selected={sectorFilters} onChange={setSectorFilters} />
          </Facet>
          <div className="sticky-actions">
            <button className="secondary-button flex-1" onClick={savePersona} disabled={!draft}><Save size={18} /> Save</button>
            <button className="primary-button flex-1" onClick={() => run()} disabled={!personaId || loading}><Play size={18} /> {loading ? "Running" : "Run"}</button>
          </div>
        </aside>
        <main className="space-y-4">
          <section className="results-toolbar">
            <div>
              <div className="text-xs font-semibold uppercase text-zinc-500">Ranked Stock List</div>
              <h2 className="text-2xl font-semibold">Stocks matching your personal rules</h2>
            </div>
            <div className="relative min-w-72">
              <Search className="pointer-events-none absolute left-3 top-3 text-zinc-400" size={17} />
              <input className="input w-full pl-9" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search stock or symbol" />
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <select className="input" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                {SORT_OPTIONS.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
              </select>
              <button className="icon-button" title="Toggle sort direction" onClick={() => setSortDir(sortDir === "desc" ? "asc" : "desc")}><ArrowUpDown size={17} /></button>
              <button className="secondary-button" onClick={saveScreen} disabled={!visibleResults.length}><Bookmark size={17} /> Save Screen</button>
            </div>
          </section>
          {message && <div className="rounded-md border border-amber-500/25 bg-amber-500/10 px-3 py-2 text-sm text-amber-100">{message}</div>}
          {!!savedScreens.length && (
            <div className="flex flex-wrap gap-2">
              {savedScreens.slice(0, 5).map((screen) => <button key={screen.id} className="chip" onClick={() => { setResults(screen.results || []); setMessage(`Loaded ${screen.name}.`); }}>{screen.name}</button>)}
            </div>
          )}
          <ResultSummary results={visibleResults} total={results.length} />
          <Panel title="Screener Results" icon={ShieldCheck}>
            <ResultsTable results={visibleResults} onSelect={setSelected} onWatchlist={addToWatchlist} onPortfolio={addToPortfolio} />
          </Panel>
        </main>
      </section>
      {selected && <StockDetail api={api} stock={selected} personaId={personaId} />}
    </div>
  );
}

function ResultSummary({ results, total }) {
  if (!results.length) {
    return <div className="empty-state"><Search size={18} /> Adjust preferences on the left and run the screener to show stocks.</div>;
  }
  const pass = results.filter((r) => r.summary.verdict === "PASS").length;
  return (
    <div className="mb-4 grid gap-3 sm:grid-cols-3">
      <Metric label="Shown" value={total ? `${results.length}/${total}` : results.length} />
      <Metric label="Passed all filters" value={pass} />
      <Metric label="Rejected" value={results.length - pass} />
    </div>
  );
}

function ResultsTable({ results, onSelect, onWatchlist, onPortfolio }) {
  if (!results.length) return null;
  return (
    <div className="overflow-auto">
      <table className="data-table">
        <thead><tr>{["Stock", "Sector", "Data", "Revenue", "ROE", "D/E", "FII", "DII", "Public", "MA", "Score", "Status", "Actions"].map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{results.map((r) => <tr key={r.symbol}>
          <td><div className="font-semibold">{r.company_name}</div><div className="font-mono text-xs text-zinc-500">{r.symbol}</div></td>
          <td>{r.sector}</td><td><DataQualityBadge snapshot={r.fundamentals} /></td><td>{fmt(r.fundamentals.revenue_growth_yoy)}%</td><td>{fmt(r.fundamentals.roe)}%</td><td>{fmt(r.fundamentals.debt_to_equity)}</td><td>{fmt(r.fundamentals.fii_holding_pct)}%</td><td>{fmt(r.fundamentals.dii_holding_pct)}%</td><td>{fmt(r.fundamentals.public_holding_pct)}%</td>
          <td>{r.fundamentals.moving_avg_20d > r.fundamentals.moving_avg_200d ? "Bullish" : "Weak"}</td><td>{fmt(r.score)}</td><td><Badge ok={r.summary.verdict === "PASS"} text={r.summary.verdict} /></td>
          <td>
            <div className="flex gap-1">
              <button title="View detail" className="icon-button" onClick={() => onSelect(r)}><Eye size={17} /></button>
              <a title="Open live chart" className="icon-button" href={chartUrl(r.symbol)} target="_blank" rel="noreferrer"><ExternalLink size={17} /></a>
              <button title="Add to watchlist" className="icon-button" onClick={() => onWatchlist(r)}><ListPlus size={17} /></button>
              <button title="Add to portfolio" className="icon-button" onClick={() => onPortfolio(r)}><Wallet size={17} /></button>
            </div>
          </td>
        </tr>)}</tbody>
      </table>
    </div>
  );
}

function StockDetail({ api, stock, personaId }) {
  const [explain, setExplain] = useState("");
  const f = stock.fundamentals;
  const chart = (f.raw_json?.eps_history || [f.eps]).map((eps, i) => ({ year: String(2021 + i), eps, revenue: f.raw_json?.revenue_growth_history?.[i] || f.revenue_growth_yoy }));
  const passed = stock.evaluations.filter((e) => e.status === "pass");
  const failed = stock.evaluations.filter((e) => e.status !== "pass");
  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_.9fr]">
      <Panel title={`${stock.company_name} Detail`} icon={BarChart3}>
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <Badge ok={stock.summary.verdict === "PASS"} text={stock.summary.verdict} />
          <DataQualityBadge snapshot={f} />
          <a className="secondary-button" href={chartUrl(stock.symbol)} target="_blank" rel="noreferrer"><ExternalLink size={17} /> Live Chart</a>
          <span className="text-sm text-stone-400">{failed.length ? `${failed.length} filters rejected this stock` : "No selected filters rejected this stock"}</span>
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">{[
          ["Market Cap", `${fmt(stock.market_cap_cr)} Cr`], ["P/E", fmt(f.pe_ratio)], ["EPS", fmt(f.eps)], ["ROE", `${fmt(f.roe)}%`], ["Revenue", `${fmt(f.revenue_growth_yoy)}%`], ["Margin", `${fmt(f.profit_margin)}%`], ["Debt/Equity", fmt(f.debt_to_equity)], ["FII", `${fmt(f.fii_holding_pct)}%`], ["DII", `${fmt(f.dii_holding_pct)}%`], ["Public", `${fmt(f.public_holding_pct)}%`],
        ].map(([k, v]) => <Metric key={k} label={k} value={v} />)}</div>
        <div className="mt-5 h-56"><ResponsiveContainer><LineChart data={chart}><XAxis dataKey="year" /><YAxis /><Tooltip /><Line dataKey="eps" stroke="#0f766e" strokeWidth={2} /><Line dataKey="revenue" stroke="#b45309" strokeWidth={2} /></LineChart></ResponsiveContainer></div>
      </Panel>
      <Panel title="Why It Passed Or Failed" icon={CheckCircle2}>
        <div className="mb-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-md border border-emerald-400/20 bg-emerald-400/10 p-3">
            <div className="text-sm font-semibold text-emerald-200">Passed filters</div>
            <div className="mt-1 text-2xl font-semibold text-stone-100">{passed.length}</div>
          </div>
          <div className="rounded-md border border-red-400/20 bg-red-400/10 p-3">
            <div className="text-sm font-semibold text-red-200">Rejected by</div>
            <div className="mt-1 text-2xl font-semibold text-stone-100">{failed.length}</div>
          </div>
        </div>
        <div className="space-y-2">{stock.evaluations.map((e) => <div key={e.criterion} className="rounded-md border border-amber-500/10 bg-black/20 p-3">
          <div className="flex items-center justify-between gap-3"><span className="font-medium text-stone-100">{e.criterion}</span><Badge ok={e.status === "pass"} text={e.status.toUpperCase()} /></div>
          <div className="mt-1 text-sm text-stone-400">{e.reason}</div>
        </div>)}</div>
        <button className="secondary-button mt-4" onClick={() => api(`/screener/explain/${stock.symbol}/${personaId}`).then((r) => setExplain(r.explanation))}>Get LLM Explanation</button>
        {explain && <p className="mt-3 rounded border border-amber-500/20 bg-black/20 p-3 text-sm text-stone-300">{explain}</p>}
      </Panel>
    </section>
  );
}

function Portfolio({ api }) {
  const [portfolio, setPortfolio] = useState(null);
  const [watchlists, setWatchlists] = useState([]);
  const [form, setForm] = useState({ symbol: "TCS.NS", quantity: 10, avg_buy_price: 3500 });
  const load = () => { api("/portfolio/").then(setPortfolio); api("/watchlists/").then(setWatchlists); };
  useEffect(load, []);
  async function add(e) {
    e.preventDefault();
    await api("/portfolio/", { method: "POST", body: form });
    load();
  }
  return (
    <div className="space-y-5">
      <Stats stats={portfolio?.stats} />
      <section className="grid gap-4 xl:grid-cols-[1fr_360px]">
        <Panel title="Holdings" icon={Wallet}>
          <form onSubmit={add} className="toolbar mb-4">
            <input className="input" value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })} />
            <input className="input" type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} />
            <input className="input" type="number" value={form.avg_buy_price} onChange={(e) => setForm({ ...form, avg_buy_price: Number(e.target.value) })} />
            <button title="Add holding" className="primary-button"><Plus size={18} /> Add</button>
          </form>
          <div className="overflow-auto"><table className="data-table"><thead><tr>{["Stock", "Qty", "Avg", "Current", "P&L", "Return", "Days"].map((h) => <th key={h}>{h}</th>)}</tr></thead><tbody>{portfolio?.holdings.map((h) => <tr key={h.id}><td>{h.symbol}</td><td>{h.quantity}</td><td>{money(h.avg_buy_price)}</td><td>{money(h.current_price)}</td><td className={h.gain_loss >= 0 ? "text-teal-700" : "text-red-700"}>{money(h.gain_loss)}</td><td>{fmt(h.return_pct)}%</td><td>{h.days_held}</td></tr>)}</tbody></table></div>
        </Panel>
        <Panel title="Sector Allocation" icon={PieIcon}>
          <div className="h-64"><ResponsiveContainer><PieChart><Pie data={portfolio?.sector_allocation || []} dataKey="value" nameKey="sector">{(portfolio?.sector_allocation || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie><Tooltip formatter={(v) => money(v)} /></PieChart></ResponsiveContainer></div>
          <Watchlists api={api} items={watchlists} reload={load} />
        </Panel>
      </section>
    </div>
  );
}

function Watchlists({ api, items, reload }) {
  const [name, setName] = useState("Core Quality");
  const [symbols, setSymbols] = useState("RELIANCE.NS,TCS.NS");
  async function add() {
    await api("/watchlists/", { method: "POST", body: { name, stock_ids: symbols.split(",").map((s) => s.trim()).filter(Boolean) } });
    reload();
  }
  return <div className="border-t border-zinc-200 pt-4"><div className="mb-2 font-medium">Watchlists</div><div className="flex gap-2"><input className="input min-w-0" value={name} onChange={(e) => setName(e.target.value)} /><button title="Create watchlist" className="icon-button" onClick={add}><Plus size={17} /></button></div><input className="input mt-2 w-full" value={symbols} onChange={(e) => setSymbols(e.target.value)} />{items.map((w) => <div key={w.id} className="mt-2 text-sm text-zinc-600">{w.name}: {w.stock_ids.join(", ")}</div>)}</div>;
}

function Earnings({ api }) {
  const [days, setDays] = useState(30);
  const [scope, setScope] = useState("full");
  const [items, setItems] = useState([]);
  useEffect(() => { api(`/earnings/upcoming?days=${days}&scope=${scope}`).then(setItems); }, [days, scope]);
  return <Panel title="Upcoming NSE Earnings" icon={CalendarDays}><div className="toolbar mb-4"><select className="input" value={days} onChange={(e) => setDays(Number(e.target.value))}><option>30</option><option>60</option><option>90</option></select><select className="input" value={scope} onChange={(e) => setScope(e.target.value)}><option value="full">Full Nifty 500</option><option value="portfolio">Portfolio</option></select></div><EarningsList items={items} /></Panel>;
}

function Personas({ api }) {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = () => {
    setLoading(true);
    setError("");
    api("/personas/")
      .then((p) => {
        setItems(p);
        setSelected((current) => {
          if (!p.length) return null;
          const same = current && p.find((item) => item.id === current.id);
          return clone(same || p[0]);
        });
      })
      .catch((err) => setError(err.message || "Could not load personas"))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);
  async function save() {
    if (!selected) return;
    await api(`/personas/${selected.id}`, { method: "PUT", body: selected });
    load();
  }
  async function createPreset(name) {
    if (!name) return;
    const persona = await api("/personas/preset", { method: "POST", body: { name } });
    const next = await api("/personas/");
    setItems(next);
    setSelected(clone(persona));
  }
  async function duplicateSelected() {
    if (!selected) return;
    const persona = await api(`/personas/${selected.id}/duplicate`, { method: "POST" });
    const next = await api("/personas/");
    setItems(next);
    setSelected(clone(persona));
  }
  function resetCriteria() {
    if (!selected) return;
    setSelected({ ...selected, criteria: clone(DEFAULT_QUALITY_CRITERIA) });
  }
  if (loading) return <Panel title="Preference Studio" icon={Edit3}><div className="empty-state">Loading persona preferences...</div></Panel>;
  if (error) return <Panel title="Preference Studio" icon={Edit3}><div className="rounded-md border border-red-400/30 bg-red-400/10 p-4 text-red-200">{error}</div></Panel>;
  return (
    <section className="grid gap-5 xl:grid-cols-[340px_1fr]">
      <Panel title="Investor Profiles" icon={ShieldCheck}>
        <div className="mb-4 grid gap-2">
          <select className="input w-full" defaultValue="" onChange={(e) => createPreset(e.target.value)}>
            <option value="">Create profile preset</option>
            {PERSONA_PRESETS.map((preset) => <option key={preset} value={preset}>{preset}</option>)}
          </select>
          <button className="secondary-button w-full" onClick={duplicateSelected} disabled={!selected}>Duplicate selected</button>
        </div>
        <div className="space-y-3">
          {items.map((p) => (
            <button key={p.id} className={`persona-card ${selected?.id === p.id ? "persona-card-active" : ""}`} onClick={() => setSelected(clone(p))}>
              <span className="font-semibold">{p.name}</span>
              <span className="mt-1 block text-xs text-stone-400">{p.description || "Custom rule set"}</span>
            </button>
          ))}
          {!items.length && <div className="empty-state">No personas found. Register or reload seed data.</div>}
        </div>
      </Panel>
      {selected && (
        <Panel title="Preference Studio" icon={Edit3}>
          <div className="mb-5 grid gap-3 md:grid-cols-[1fr_2fr]">
            <label className="field-label">
              <span>Profile name</span>
              <input className="input w-full" value={selected.name} onChange={(e) => setSelected({ ...selected, name: e.target.value })} />
            </label>
            <label className="field-label">
              <span>Description</span>
              <input className="input w-full" value={selected.description || ""} onChange={(e) => setSelected({ ...selected, description: e.target.value })} />
            </label>
          </div>
          <PreferenceEditor persona={selected} onChange={setSelected} />
          <div className="mt-5 flex flex-wrap gap-3">
            <button className="gold-button" onClick={save}><Save size={18} /> Save Preferences</button>
            <button className="dark-button" onClick={resetCriteria}>Reset Quality Defaults</button>
          </div>
        </Panel>
      )}
    </section>
  );
}

function PreferenceEditor({ persona, onChange, compact = false }) {
  const criteria = persona.criteria || {};
  const filters = criteria.hard_filters || {};
  const setPath = (path, value) => {
    const next = clone(persona);
    let cursor = next;
    path.slice(0, -1).forEach((key) => {
      cursor[key] = cursor[key] || {};
      cursor = cursor[key];
    });
    cursor[path[path.length - 1]] = value;
    onChange(next);
  };
  return (
    <div className={compact ? "space-y-3" : "grid gap-4 lg:grid-cols-2"}>
      <div className="space-y-3">
        <Facet title="Size">
          <RangeField label="Market cap above" suffix="Cr" min={1000} max={200000} step={500} value={filters.market_cap_cr?.min} onChange={(v) => setPath(["criteria", "hard_filters", "market_cap_cr", "min"], v)} />
        </Facet>
        <Facet title="Growth">
          <RangeField label="Revenue growth at least" suffix="%" min={0} max={40} value={filters.revenue_growth_yoy?.min} onChange={(v) => setPath(["criteria", "hard_filters", "revenue_growth_yoy", "min"], v)} />
          <ChipGroup
            value={String(filters.revenue_growth_yoy?.sustained_years || 3)}
            options={[["1", "1 yr"], ["2", "2 yrs"], ["3", "3 yrs"], ["5", "5 yrs"]]}
            onChange={(v) => setPath(["criteria", "hard_filters", "revenue_growth_yoy", "sustained_years"], Number(v))}
          />
          <ChipGroup
            value={String(filters.eps_trend?.lookback_years || 5)}
            options={[["3", "EPS 3 yrs"], ["5", "EPS 5 yrs"]]}
            onChange={(v) => setPath(["criteria", "hard_filters", "eps_trend", "lookback_years"], Number(v))}
          />
        </Facet>
        <Facet title="Quality">
          <RangeField label="ROE at least" suffix="%" min={0} max={40} value={filters.roe?.min} onChange={(v) => setPath(["criteria", "hard_filters", "roe", "min"], v)} />
          <RangeField label="Debt/equity below" min={0} max={3} step={0.1} value={filters.debt_to_equity?.max} onChange={(v) => setPath(["criteria", "hard_filters", "debt_to_equity", "max"], v)} />
          <RangeField label="Debtor days below" min={30} max={180} value={filters.debtor_days?.max} onChange={(v) => setPath(["criteria", "hard_filters", "debtor_days", "max"], v)} />
        </Facet>
        <Facet title="Ownership">
          <DualRangeField
            label="FII holding"
            suffix="%"
            minValue={filters.fii_holding_pct?.min}
            maxValue={filters.fii_holding_pct?.max}
            min={0}
            max={100}
            step={1}
            onMinChange={(v) => setPath(["criteria", "hard_filters", "fii_holding_pct", "min"], v)}
            onMaxChange={(v) => setPath(["criteria", "hard_filters", "fii_holding_pct", "max"], v)}
          />
          <DualRangeField
            label="DII holding"
            suffix="%"
            minValue={filters.dii_holding_pct?.min}
            maxValue={filters.dii_holding_pct?.max}
            min={0}
            max={100}
            step={1}
            onMinChange={(v) => setPath(["criteria", "hard_filters", "dii_holding_pct", "min"], v)}
            onMaxChange={(v) => setPath(["criteria", "hard_filters", "dii_holding_pct", "max"], v)}
          />
          <DualRangeField
            label="Public holding"
            suffix="%"
            minValue={filters.public_holding_pct?.min}
            maxValue={filters.public_holding_pct?.max}
            min={0}
            max={100}
            step={1}
            onMinChange={(v) => setPath(["criteria", "hard_filters", "public_holding_pct", "min"], v)}
            onMaxChange={(v) => setPath(["criteria", "hard_filters", "public_holding_pct", "max"], v)}
          />
        </Facet>
      </div>
      <div className="space-y-3">
        <Facet title="Mandatory Signals">
          <CheckBox label="Profit margin must be positive" checked={filters.profit_margin?.positive !== false} onChange={(v) => setPath(["criteria", "hard_filters", "profit_margin", "positive"], v)} />
          <CheckBox label="Cash flow must be positive and growing" checked={filters.cash_flow_from_operations?.growing_yoy !== false} onChange={(v) => setPath(["criteria", "hard_filters", "cash_flow_from_operations", "growing_yoy"], v)} />
          <CheckBox label="20 DMA must be above 200 DMA" checked={filters.moving_average_signal?.ma20_above_ma200 !== false} onChange={(v) => setPath(["criteria", "hard_filters", "moving_average_signal", "ma20_above_ma200"], v)} />
        </Facet>
        <div className="rounded-md border border-amber-500/20 bg-amber-500/10 p-3 text-sm text-amber-100">
          Every checked filter is mandatory. If a stock fails even one selected rule, it is rejected.
        </div>
      </div>
    </div>
  );
}

function Facet({ title, children }) {
  return (
    <section className="facet">
      <div className="facet-title">{title}</div>
      <div className="space-y-3">{children}</div>
    </section>
  );
}

function RangeField({ label, value, onChange, min, max, step = 1, suffix = "" }) {
  const current = value ?? min;
  return (
    <label className="range-field">
      <span className="flex items-center justify-between gap-3">
        <span>{label}</span>
        <span className="range-value">{fmt(current)} {suffix}</span>
      </span>
      <input type="range" min={min} max={max} step={step} value={current} onChange={(e) => onChange(Number(e.target.value))} />
      <input className="input w-full" type="number" min={min} max={max} step={step} value={current} onChange={(e) => onChange(Number(e.target.value))} />
    </label>
  );
}

function DualRangeField({ label, minValue, maxValue, onMinChange, onMaxChange, min, max, step = 1, suffix = "" }) {
  const currentMin = minValue ?? min;
  const currentMax = maxValue ?? max;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm font-medium text-zinc-700">
        <span>{label}</span>
        <span className="range-value">{fmt(currentMin)} - {fmt(currentMax)} {suffix}</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <RangeField label="Min" suffix={suffix} min={min} max={max} step={step} value={currentMin} onChange={onMinChange} />
        <RangeField label="Max" suffix={suffix} min={min} max={max} step={step} value={currentMax} onChange={onMaxChange} />
      </div>
    </div>
  );
}

function CheckBox({ label, checked, onChange }) {
  return (
    <label className="check-row">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

function ChipGroup({ value, options, onChange }) {
  return <div className="chip-group">{options.map(([id, label]) => <button key={id} type="button" className={`chip ${value === id ? "chip-active" : ""}`} onClick={() => onChange(id)}>{label}</button>)}</div>;
}

function MultiCheck({ options, selected, onChange }) {
  if (!options.length) return <div className="text-sm text-zinc-500">Run the screener to see sectors.</div>;
  const toggle = (option) => {
    onChange(selected.includes(option) ? selected.filter((item) => item !== option) : [...selected, option]);
  };
  return (
    <div className="multi-check">
      {options.map((option) => (
        <label key={option} className="check-row">
          <input type="checkbox" checked={selected.includes(option)} onChange={() => toggle(option)} />
          <span>{option}</span>
        </label>
      ))}
    </div>
  );
}

function Stats({ stats }) {
  const values = [["Invested", money(stats?.total_invested || 0)], ["Current Value", money(stats?.current_value || 0)], ["Gain/Loss", money(stats?.gain_loss || 0)], ["Return", `${fmt(stats?.gain_loss_pct || 0)}%`]];
  return <section className="grid gap-3 md:grid-cols-4">{values.map(([label, value]) => <Metric key={label} label={label} value={value} />)}</section>;
}

function AlertList({ alerts }) {
  if (!alerts.length) return <p className="text-sm text-zinc-500">No portfolio hard-filter violations.</p>;
  return <div className="space-y-2">{alerts.map((a) => <div key={a.symbol} className="rounded border border-red-200 bg-red-50 p-3"><div className="flex items-center gap-2 font-semibold text-red-800"><AlertTriangle size={17} /> {a.symbol} - {a.flag}</div><div className="mt-1 text-sm text-red-700">{a.failures.map((f) => f.criterion).join(", ")}</div></div>)}</div>;
}

function EarningsList({ items, compact }) {
  if (!items.length) return <p className="text-sm text-zinc-500">No earnings in this view.</p>;
  return <div className="space-y-2">{items.map((e) => <div key={e.symbol} className={`flex items-center justify-between border-b border-zinc-100 py-2 ${e.is_this_week ? "font-semibold text-amber-800" : ""}`}><div><div>{e.company_name}</div><div className="text-xs text-zinc-500">{e.symbol} · {e.sector}</div></div><div className="text-right text-sm">{new Date(e.earnings_date).toLocaleDateString("en-IN")}{!compact && <div className="text-xs text-zinc-500">Buy prep before date</div>}</div></div>)}</div>;
}

function Panel({ title, icon: Icon, children }) {
  return <section className="premium-card p-5"><div className="mb-4 flex items-center gap-2 text-base font-semibold text-stone-100"><Icon size={18} className="text-amber-400" /> {title}</div>{children}</section>;
}

function Metric({ label, value }) {
  return <div className="premium-card p-5"><div className="text-xs font-medium uppercase text-stone-400">{label}</div><div className="mt-2 text-2xl font-semibold tracking-tight text-stone-100">{value}</div></div>;
}

function Badge({ ok, text }) {
  return <span className={`inline-flex rounded px-2 py-1 text-xs font-semibold ${ok ? "bg-emerald-400/15 text-emerald-300" : "bg-red-400/15 text-red-300"}`}>{text}</span>;
}

function DataQualityBadge({ snapshot }) {
  const quality = dataQuality(snapshot);
  const classes = {
    Live: "border-emerald-400/25 bg-emerald-400/10 text-emerald-200",
    Cached: "border-blue-400/25 bg-blue-400/10 text-blue-200",
    Estimated: "border-amber-400/25 bg-amber-400/10 text-amber-200",
    Missing: "border-red-400/25 bg-red-400/10 text-red-200",
  };
  return <span className={`inline-flex rounded border px-2 py-1 text-xs font-semibold ${classes[quality]}`}>{quality}</span>;
}

function dataQuality(snapshot) {
  if (!snapshot) return "Missing";
  if (snapshot.raw_json?.fallback || snapshot.source === "fallback") return "Estimated";
  if (!snapshot.pe_ratio && !snapshot.roe && !snapshot.revenue_growth_yoy) return "Missing";
  const fetched = snapshot.fetched_at ? new Date(snapshot.fetched_at).getTime() : 0;
  if (fetched && Date.now() - fetched < 1000 * 60 * 60 * 8) return "Live";
  return "Cached";
}

function chartUrl(symbol) {
  const base = String(symbol || "").replace(".NS", "").toUpperCase();
  return `https://www.tradingview.com/chart/?symbol=NSE%3A${encodeURIComponent(base)}`;
}

function sortResults(a, b, sortBy, dir) {
  const mult = dir === "asc" ? 1 : -1;
  const value = (row) => {
    if (sortBy === "score") return row.score ?? 0;
    if (sortBy === "market_cap") return row.market_cap_cr ?? 0;
    if (sortBy === "roe") return row.fundamentals?.roe ?? 0;
    if (sortBy === "revenue") return row.fundamentals?.revenue_growth_yoy ?? 0;
    if (sortBy === "debt") return row.fundamentals?.debt_to_equity ?? 999;
    if (sortBy === "verdict") return row.summary?.verdict === "PASS" ? 1 : 0;
    return 0;
  };
  return (value(a) - value(b)) * mult || a.symbol.localeCompare(b.symbol);
}

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delay);
    return () => window.clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

function useLoad(fn) {
  const [data, setData] = useState(null);
  const load = () => fn().then(setData).catch(() => setData(null));
  return { data, load };
}

function makeApi(token) {
  return (path, options = {}) => rawApi(path, { ...options, token });
}

async function rawApi(path, { method = "GET", body, token } = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

function fmt(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "-";
  return Number(v).toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function money(v) {
  return `₹${fmt(v)}`;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}
