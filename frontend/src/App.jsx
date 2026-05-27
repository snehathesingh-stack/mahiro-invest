import {
  LayoutDashboard,
  Wallet,
  Bell,
  LineChart,
  User,
} from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex">
      
      {/* SIDEBAR */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6 hidden md:flex flex-col">
        <h1 className="text-2xl font-bold mb-10">
          Mahiro Invest
        </h1>

        <nav className="space-y-3">
          <NavItem icon={<LayoutDashboard size={18} />} label="Dashboard" active />
          <NavItem icon={<Wallet size={18} />} label="Portfolio" />
          <NavItem icon={<LineChart size={18} />} label="Analytics" />
          <NavItem icon={<Bell size={18} />} label="Alerts" />
          <NavItem icon={<User size={18} />} label="Profile" />
        </nav>
      </aside>

      {/* MAIN */}
      <main className="flex-1 p-6">

        {/* TOPBAR */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold">
              Dashboard
            </h2>

            <p className="text-slate-400 mt-1">
              Welcome back, Sneha 👋
            </p>
          </div>

          <button className="bg-emerald-500 hover:bg-emerald-400 transition px-4 py-2 rounded-lg text-black font-semibold">
            + Add Stock
          </button>
        </div>

        {/* OVERVIEW CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          <Card
            title="Portfolio Value"
            value="$124,532"
            change="+12.4%"
          />

          <Card
            title="Today's Gain"
            value="+$2,430"
            change="+1.92%"
          />

          <Card
            title="Risk Score"
            value="Moderate"
            change="Stable"
          />

        </div>

        {/* AI INSIGHTS */}
        <div className="mt-8 bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-semibold mb-4">
            AI Portfolio Insights
          </h3>

          <div className="space-y-4">

            <Insight
              text="Your portfolio is heavily concentrated in technology stocks."
            />

            <Insight
              text="NVIDIA and Tesla together contribute 48% of your volatility."
            />

            <Insight
              text="Consider increasing diversification into ETFs or defensive sectors."
            />

          </div>
        </div>

      </main>
    </div>
  );
}

function NavItem({ icon, label, active }) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition ${
        active
          ? "bg-emerald-500 text-black font-semibold"
          : "hover:bg-slate-800 text-slate-300"
      }`}
    >
      {icon}
      <span>{label}</span>
    </div>
  );
}

function Card({ title, value, change }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <p className="text-slate-400 text-sm mb-2">
        {title}
      </p>

      <h3 className="text-3xl font-bold mb-2">
        {value}
      </h3>

      <p className="text-emerald-400 text-sm">
        {change}
      </p>
    </div>
  );
}

function Insight({ text }) {
  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300">
      {text}
    </div>
  );
}