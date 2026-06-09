# Daily Contribution Roadmap

This roadmap keeps Mahiro Invest moving with small, real improvements that are useful for the product and visible in GitHub activity.

## Week 1: Make The App Easier To Trust

| Day | Focus | Useful Commit |
| --- | --- | --- |
| 1 | Project docs | Add contribution roadmap and clarify the next build steps. |
| 2 | README polish | Add screenshots, demo login, and feature walkthrough. |
| 3 | Backend tests | Add tests for auth, persona presets, and screener saved screens. |
| 4 | Frontend smoke tests | Add a basic app render test and API client checks. |
| 5 | Data quality | Add clearer copy for Live, Cached, Estimated, and Missing labels. |
| 6 | Stock detail | Improve rejected-filter grouping and raw metric display. |
| 7 | Mobile UI | Polish screener sidebar and results table on small screens. |

## Week 2: Prepare Deployment

| Day | Focus | Useful Commit |
| --- | --- | --- |
| 8 | Backend deployment | Add Render/Railway deployment checklist. |
| 9 | Frontend deployment | Add Vercel deployment checklist and env examples. |
| 10 | Production config | Add stricter CORS and production JWT guidance. |
| 11 | Database migrations | Verify Alembic migrations for fresh production databases. |
| 12 | Seed controls | Add safer production seed behavior. |
| 13 | Monitoring | Add health endpoint details and basic service status checks. |
| 14 | Release notes | Create a first public release note draft. |

## Week 3: Improve Screening Intelligence

| Day | Focus | Useful Commit |
| --- | --- | --- |
| 15 | Saved screens | Add saved screen rename/delete UI. |
| 16 | Watchlists | Add choose-watchlist flow from screener rows. |
| 17 | Portfolio | Add edit/delete holding controls in the UI. |
| 18 | Earnings | Improve portfolio/watchlist earnings filters. |
| 19 | Anomaly view | Show anomaly score explanation on stock detail. |
| 20 | LLM cache | Improve explanation cache labels and loading states. |
| 21 | Screener exports | Add CSV export for filtered results. |

## Week 4: Prediction Center Design

| Day | Focus | Useful Commit |
| --- | --- | --- |
| 22 | Forecast spec | Document 30/90/180-day outlook design. |
| 23 | Risk score | Add a backend risk-score service draft. |
| 24 | Scenario chart | Add frontend scenario chart component. |
| 25 | Earnings risk | Add pre-earnings risk scoring rules. |
| 26 | Confidence labels | Add Low, Medium, High confidence copy. |
| 27 | Backtesting notes | Document how predictions should be validated. |
| 28 | Product polish | Review wording so predictions do not sound like guaranteed advice. |

## Daily Commit Rule

Each commit should change something meaningful:

- A feature improvement.
- A bug fix.
- A test.
- A documentation improvement.
- A deployment or environment improvement.

Avoid empty commits, fake dates, or meaningless file churn. Real progress looks better and is safer for interviews, demos, and long-term project quality.
