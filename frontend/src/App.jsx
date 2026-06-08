import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Bell,
  CalendarDays,
  CheckCircle2,
  Edit3,
  Eye,
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
const NAV = [
  ["dashboard", BarChart3, "Dashboard"],
  ["screener", Search, "Screener"],
  ["portfolio", Wallet, "Portfolio"],
  ["earnings", CalendarDays, "Earnings"],
  ["personas", Edit3, "Persona"],
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
    <div className="min-h-screen bg-zinc-50 text-zinc-950">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-zinc-200 bg-white lg:block">
        <div className="px-6 py-6 border-b border-zinc-200">
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
        <header className="sticky top-0 z-10 border-b border-zinc-200 bg-white/90 backdrop-blur">
          <div className="mx-auto flex max-w-[1500px] items-center justify-between px-4 py-4 lg:px-8">
            <div>
              <div className="text-sm text-zinc-500">Signed in as {user?.name || "Investor"}</div>
              <h1 className="text-xl font-semibold">{NAV.find((n) => n[0] === active)?.[2]}</h1>
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
          {active === "dashboard" && <Dashboard api={api} setActive={setActive} />}
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
        <div className={compact ? "text-xl font-bold" : "text-2xl font-bold leading-tight"}>Mahiro Invest</div>
        <div className="mt-1 max-w-40 text-sm leading-snug text-zinc-500">Personal NSE quality screener</div>
      </div>
    </div>
  );
}

function AuthPage({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "Dad", email: "dad@example.com", password: "mahiro123" });
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
    <div className="min-h-screen grid place-items-center bg-zinc-950 px-4 text-white">
      <form onSubmit={submit} className="w-full max-w-md rounded-lg border border-zinc-800 bg-zinc-900 p-6 shadow-2xl">
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

function Dashboard({ api, setActive }) {
  const { data: portfolio, load: loadPortfolio } = useLoad(() => api("/portfolio/"), []);
  const { data: alerts, load: loadAlerts } = useLoad(() => api("/alerts/"), []);
  const { data: earnings, load: loadEarnings } = useLoad(() => api("/earnings/upcoming?days=30"), []);
  useEffect(() => { loadPortfolio(); loadAlerts(); loadEarnings(); }, []);
  return (
    <div className="space-y-6">
      <section className="hero-band">
        <div className="max-w-4xl">
          <div className="inline-flex items-center gap-2 rounded bg-white/10 px-2 py-1 text-xs font-medium text-teal-50">
            <Sparkles size={14} /> Dad's 16-criteria workflow, now searchable
          </div>
          <h2 className="mt-4 text-2xl font-semibold text-white lg:text-3xl">Tune your quality filters, run the screener, then inspect every pass or fail.</h2>
        </div>
        <button className="primary-button bg-white text-teal-900 hover:bg-teal-50" onClick={() => setActive("screener")}><Play size={18} /> Open Screener</button>
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
      <button className="primary-button" onClick={() => setActive("screener")}><Play size={18} /> Run Dad's Screener</button>
    </div>
  );
}

function Screener({ api }) {
  const [personas, setPersonas] = useState([]);
  const [personaId, setPersonaId] = useState("");
  const [draft, setDraft] = useState(null);
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    api("/personas/").then((p) => {
      setPersonas(p);
      setPersonaId(p[0]?.id || "");
      setDraft(p[0] ? clone(p[0]) : null);
    });
  }, []);
  useEffect(() => {
    const next = personas.find((p) => String(p.id) === String(personaId));
    setDraft(next ? clone(next) : null);
  }, [personaId]);

  async function savePersona() {
    if (!draft) return null;
    const saved = await api(`/personas/${draft.id}`, { method: "PUT", body: draft });
    setPersonas((current) => current.map((p) => (p.id === saved.id ? saved : p)));
    setDraft(clone(saved));
    return saved;
  }

  async function run() {
    setLoading(true);
    const saved = await savePersona();
    const data = await api("/screener/run", { method: "POST", body: { persona_id: Number(saved?.id || personaId) } }).finally(() => setLoading(false));
    setResults(data.results);
    setSelected(data.results[0]);
  }
  return (
    <div className="space-y-5">
      <section className="grid gap-4 xl:grid-cols-[380px_1fr]">
        <Panel title="Personal Preference Filters" icon={SlidersHorizontal}>
          <div className="space-y-4">
            <select className="input w-full" value={personaId} onChange={(e) => setPersonaId(e.target.value)}>
              {personas.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            {draft && <PreferenceEditor persona={draft} onChange={setDraft} compact />}
            <div className="flex gap-2">
              <button className="secondary-button flex-1" onClick={savePersona} disabled={!draft}><Save size={18} /> Save</button>
              <button className="primary-button flex-1" onClick={run} disabled={!personaId || loading}><Play size={18} /> {loading ? "Running" : "Run"}</button>
            </div>
          </div>
        </Panel>
        <Panel title="Ranked Stock List" icon={ShieldCheck}>
          <ResultSummary results={results} />
          <ResultsTable results={results} onSelect={setSelected} />
        </Panel>
      </section>
      {selected && <StockDetail api={api} stock={selected} personaId={personaId} />}
    </div>
  );
}

function ResultSummary({ results }) {
  if (!results.length) {
    return <div className="empty-state"><Search size={18} /> Adjust preferences on the left and run the screener to show stocks.</div>;
  }
  const pass = results.filter((r) => r.summary.verdict === "PASS").length;
  return (
    <div className="mb-4 grid gap-3 sm:grid-cols-3">
      <Metric label="Universe checked" value={results.length} />
      <Metric label="Passed all filters" value={pass} />
      <Metric label="Rejected" value={results.length - pass} />
    </div>
  );
}

function ResultsTable({ results, onSelect }) {
  if (!results.length) return null;
  return (
    <div className="overflow-auto">
      <table className="data-table">
        <thead><tr>{["Stock", "Sector", "P/E", "Revenue", "ROE", "D/E", "Debtors", "MA", "Score", "Status", ""].map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>{results.map((r) => <tr key={r.symbol}>
          <td><div className="font-semibold">{r.company_name}</div><div className="font-mono text-xs text-zinc-500">{r.symbol}</div></td>
          <td>{r.sector}</td><td>{fmt(r.fundamentals.pe_ratio)}</td><td>{fmt(r.fundamentals.revenue_growth_yoy)}%</td><td>{fmt(r.fundamentals.roe)}%</td><td>{fmt(r.fundamentals.debt_to_equity)}</td><td>{fmt(r.fundamentals.debtor_days)}</td>
          <td>{r.fundamentals.moving_avg_20d > r.fundamentals.moving_avg_200d ? "Bullish" : "Weak"}</td><td>{fmt(r.score)}</td><td><Badge ok={r.summary.verdict === "PASS"} text={r.summary.verdict} /></td>
          <td><button title="View detail" className="icon-button" onClick={() => onSelect(r)}><Eye size={17} /></button></td>
        </tr>)}</tbody>
      </table>
    </div>
  );
}

function StockDetail({ api, stock, personaId }) {
  const [explain, setExplain] = useState("");
  const f = stock.fundamentals;
  const chart = (f.raw_json?.eps_history || [f.eps]).map((eps, i) => ({ year: String(2021 + i), eps, revenue: f.raw_json?.revenue_growth_history?.[i] || f.revenue_growth_yoy }));
  return (
    <section className="grid gap-4 xl:grid-cols-[1.1fr_.9fr]">
      <Panel title={`${stock.company_name} Detail`} icon={BarChart3}>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">{[
          ["Market Cap", `${fmt(stock.market_cap_cr)} Cr`], ["P/E", fmt(f.pe_ratio)], ["EPS", fmt(f.eps)], ["ROE", `${fmt(f.roe)}%`], ["Revenue", `${fmt(f.revenue_growth_yoy)}%`], ["Margin", `${fmt(f.profit_margin)}%`], ["Debt/Equity", fmt(f.debt_to_equity)], ["FII+DII", `${fmt((f.fii_holding_pct || 0) + (f.dii_holding_pct || 0))}%`],
        ].map(([k, v]) => <Metric key={k} label={k} value={v} />)}</div>
        <div className="mt-5 h-56"><ResponsiveContainer><LineChart data={chart}><XAxis dataKey="year" /><YAxis /><Tooltip /><Line dataKey="eps" stroke="#0f766e" strokeWidth={2} /><Line dataKey="revenue" stroke="#b45309" strokeWidth={2} /></LineChart></ResponsiveContainer></div>
      </Panel>
      <Panel title="Criteria Badges" icon={CheckCircle2}>
        <div className="space-y-2">{stock.evaluations.map((e) => <div key={e.criterion} className="flex items-center justify-between border-b border-zinc-100 py-2"><span>{e.criterion}</span><Badge ok={e.status === "pass"} text={e.status.toUpperCase()} /></div>)}</div>
        <button className="secondary-button mt-4" onClick={() => api(`/screener/explain/${stock.symbol}/${personaId}`).then((r) => setExplain(r.explanation))}>Get LLM Explanation</button>
        {explain && <p className="mt-3 rounded bg-zinc-100 p-3 text-sm text-zinc-700">{explain}</p>}
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
  const load = () => api("/personas/").then((p) => { setItems(p); setSelected(p[0] ? clone(p[0]) : null); });
  useEffect(load, []);
  async function save() {
    await api(`/personas/${selected.id}`, { method: "PUT", body: selected });
    load();
  }
  return (
    <section className="grid gap-4 xl:grid-cols-[320px_1fr]">
      <Panel title="Personas" icon={ShieldCheck}>
        <div className="space-y-2">
          {items.map((p) => <button key={p.id} className="nav-button" onClick={() => setSelected(clone(p))}>{p.name}</button>)}
        </div>
      </Panel>
      {selected && (
        <Panel title="Preference Builder" icon={Edit3}>
          <input className="input mb-3 w-full" value={selected.name} onChange={(e) => setSelected({ ...selected, name: e.target.value })} />
          <textarea className="input mb-4 h-20 w-full" value={selected.description || ""} onChange={(e) => setSelected({ ...selected, description: e.target.value })} />
          <PreferenceEditor persona={selected} onChange={setSelected} />
          <button className="primary-button mt-4" onClick={save}><Save size={18} /> Save Preferences</button>
        </Panel>
      )}
    </section>
  );
}

function PreferenceEditor({ persona, onChange, compact = false }) {
  const criteria = persona.criteria || {};
  const filters = criteria.hard_filters || {};
  const weights = criteria.ranking_weights || {};
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
    <div className={compact ? "space-y-4" : "grid gap-4 lg:grid-cols-2"}>
      <section>
        <SectionTitle title="Hard Filters" />
        <div className="filter-grid">
          <NumberField label="Market Cap Min (₹ Cr)" value={filters.market_cap_cr?.min} onChange={(v) => setPath(["criteria", "hard_filters", "market_cap_cr", "min"], v)} />
          <NumberField label="P/E Min" value={filters.pe_ratio?.min} onChange={(v) => setPath(["criteria", "hard_filters", "pe_ratio", "min"], v)} />
          <NumberField label="P/E Max" value={filters.pe_ratio?.max} onChange={(v) => setPath(["criteria", "hard_filters", "pe_ratio", "max"], v)} />
          <NumberField label="Revenue Growth Min %" value={filters.revenue_growth_yoy?.min} onChange={(v) => setPath(["criteria", "hard_filters", "revenue_growth_yoy", "min"], v)} />
          <NumberField label="Revenue Years" value={filters.revenue_growth_yoy?.sustained_years} onChange={(v) => setPath(["criteria", "hard_filters", "revenue_growth_yoy", "sustained_years"], v)} />
          <NumberField label="ROE Min %" value={filters.roe?.min} onChange={(v) => setPath(["criteria", "hard_filters", "roe", "min"], v)} />
          <NumberField label="Debt/Equity Max" value={filters.debt_to_equity?.max} onChange={(v) => setPath(["criteria", "hard_filters", "debt_to_equity", "max"], v)} step="0.1" />
          <NumberField label="Debtor Days Max" value={filters.debtor_days?.max} onChange={(v) => setPath(["criteria", "hard_filters", "debtor_days", "max"], v)} />
          <NumberField label="EPS Lookback Years" value={filters.eps_trend?.lookback_years} onChange={(v) => setPath(["criteria", "hard_filters", "eps_trend", "lookback_years"], v)} />
        </div>
        <div className="mt-3 space-y-2">
          <Toggle label="Profit margin must be positive" checked={filters.profit_margin?.positive !== false} onChange={(v) => setPath(["criteria", "hard_filters", "profit_margin", "positive"], v)} />
          <Toggle label="Cash flow must be growing" checked={filters.cash_flow_from_operations?.growing_yoy !== false} onChange={(v) => setPath(["criteria", "hard_filters", "cash_flow_from_operations", "growing_yoy"], v)} />
          <Toggle label="FII and DII both increasing" checked={filters.fii_dii_holding?.both_increasing !== false} onChange={(v) => setPath(["criteria", "hard_filters", "fii_dii_holding", "both_increasing"], v)} />
          <Toggle label="20 DMA above 200 DMA" checked={filters.moving_average_signal?.ma20_above_ma200 !== false} onChange={(v) => setPath(["criteria", "hard_filters", "moving_average_signal", "ma20_above_ma200"], v)} />
        </div>
      </section>
      <section>
        <SectionTitle title="Ranking Weights" />
        <div className="filter-grid">
          <NumberField label="Revenue Growth Points" value={weights.revenue_growth_yoy} onChange={(v) => setPath(["criteria", "ranking_weights", "revenue_growth_yoy"], v)} />
          <NumberField label="Profit Margin Points" value={weights.profit_margin} onChange={(v) => setPath(["criteria", "ranking_weights", "profit_margin"], v)} />
          <NumberField label="EPS Consistency Points" value={weights.eps_consistency} onChange={(v) => setPath(["criteria", "ranking_weights", "eps_consistency"], v)} />
          <NumberField label="Debt/Equity Points" value={weights.debt_to_equity} onChange={(v) => setPath(["criteria", "ranking_weights", "debt_to_equity"], v)} />
        </div>
        <div className="mt-4 rounded-md bg-teal-50 p-3 text-sm text-teal-900">
          One failed hard filter still rejects the stock. Weights only rank stocks that pass every mandatory criterion.
        </div>
      </section>
    </div>
  );
}

function SectionTitle({ title }) {
  return <div className="mb-3 text-xs font-semibold uppercase text-zinc-500">{title}</div>;
}

function NumberField({ label, value, onChange, step = "1" }) {
  return (
    <label className="field-label">
      <span>{label}</span>
      <input className="input w-full" type="number" step={step} value={value ?? ""} onChange={(e) => onChange(Number(e.target.value))} />
    </label>
  );
}

function Toggle({ label, checked, onChange }) {
  return (
    <label className="toggle-row">
      <span>{label}</span>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
    </label>
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
  return <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm"><div className="mb-4 flex items-center gap-2 text-base font-semibold text-zinc-900"><Icon size={18} className="text-teal-800" /> {title}</div>{children}</section>;
}

function Metric({ label, value }) {
  return <div className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm"><div className="text-xs font-medium uppercase text-zinc-500">{label}</div><div className="mt-2 text-2xl font-semibold tracking-tight">{value}</div></div>;
}

function Badge({ ok, text }) {
  return <span className={`inline-flex rounded px-2 py-1 text-xs font-semibold ${ok ? "bg-teal-100 text-teal-800" : "bg-red-100 text-red-800"}`}>{text}</span>;
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
