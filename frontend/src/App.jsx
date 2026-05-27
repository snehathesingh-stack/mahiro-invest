import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-xl">
        <h1 className="text-2xl font-bold mb-1">Mahiro Invest</h1>

        <p className="text-slate-400 text-sm mb-6">
          Backend connection check
        </p>

        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 text-sm rounded p-3">
            Backend unreachable: {error}
          </div>
        )}

        {health && (
          <div className="space-y-2 text-sm">
            <Row
              label="Status"
              value={health.status}
              ok={health.status === "ok"}
            />

            <Row
              label="Service"
              value={health.service}
              ok={true}
            />

            <Row
              label="DB Connected"
              value={String(health.db_connected)}
              ok={health.db_connected}
            />
          </div>
        )}

        {!health && !error && (
          <p className="text-slate-500 text-sm">
            Checking backend...
          </p>
        )}
      </div>
    </div>
  );
}

function Row({ label, value, ok }) {
  return (
    <div className="flex justify-between items-center border-b border-slate-800 pb-2">
      <span className="text-slate-400">{label}</span>

      <span
        className={
          ok
            ? "text-emerald-400 font-mono"
            : "text-red-400 font-mono"
        }
      >
        {value}
      </span>
    </div>
  );
}