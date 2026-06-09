# Contributing To Mahiro Invest

Mahiro Invest is a full-stack AI/ML FinTech app. Contributions should improve the product in ways that help investors understand their own screening rules, data quality, portfolio risk, or deployment path.

## Good First Contributions

- Add focused backend tests for auth, personas, screener runs, saved screens, watchlists, and portfolio endpoints.
- Improve mobile layout for the screener table and filter sidebar.
- Add clearer empty states and loading states.
- Improve data-quality labels for NSE/yfinance fallback data.
- Add README screenshots after each major UI update.
- Add deployment checklists for Vercel, Render, Railway, and managed PostgreSQL.

## Development Workflow

1. Keep changes focused.
2. Run backend compile checks before committing Python changes:

```powershell
python -m compileall backend\app backend\scripts
```

3. Run frontend build checks before committing React changes:

```powershell
cd frontend
npm run build
```

4. Commit with a clear message that explains the real improvement.

## Code Style

- Prefer existing project patterns before adding new abstractions.
- Keep business rules explicit and easy to audit.
- Do not weaken hard-filter behavior unless the product requirement changes.
- Keep financial wording careful: forecasts and scores are analysis, not guaranteed advice.
- Add comments only where they clarify non-obvious logic.

## Product Rules To Preserve

- A stock fails if it violates any enabled hard filter.
- Debtor days rules apply uniformly unless a user-created persona explicitly changes the threshold.
- Portfolio alerts should clearly show which filters were violated.
- Predictions, anomaly scores, and AI explanations must show uncertainty and data-quality context.

## Daily Contribution Habit

Use the roadmap in `docs/daily-contribution-roadmap.md` to make small, useful commits. Good GitHub activity comes from steady product progress: tests, docs, deployment improvements, UI fixes, and real features.
