from __future__ import annotations


def analyze(snapshot) -> dict:
    raw = snapshot.raw_json or {}
    rows = []
    eps = raw.get("eps_history", [])
    revenue = raw.get("revenue_growth_history", [])
    cfo = raw.get("cash_flow_history", [])
    for i in range(min(len(eps), len(revenue), len(cfo))):
        rows.append([float(eps[i]), float(revenue[i]), float(cfo[i])])
    current = [[float(snapshot.eps or 0), float(snapshot.revenue_growth_yoy or 0), float(snapshot.cash_flow_from_operations or 0)]]
    if len(rows) < 3:
        return {"is_anomaly": False, "score": 0.0, "explanation": "Not enough history for a robust Isolation Forest; treated as normal."}
    try:
        from sklearn.ensemble import IsolationForest

        model = IsolationForest(contamination=0.2, random_state=42)
        model.fit(rows)
        score = float(model.decision_function(current)[0])
        is_anomaly = bool(model.predict(current)[0] == -1)
        return {
            "is_anomaly": is_anomaly,
            "score": round(score, 4),
            "explanation": "Current EPS, revenue growth, and operating cash flow are unusual versus the 5-year baseline." if is_anomaly else "Current fundamentals look consistent with the 5-year baseline.",
        }
    except Exception:
        return {"is_anomaly": False, "score": 0.0, "explanation": "ML dependency unavailable; anomaly check used a neutral fallback."}
