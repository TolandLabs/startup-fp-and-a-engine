# Startup FP&A Engine

A transparent, interactive 24-month financial planning model for a fictional venture-backed SaaS startup. Built as a hands-on portfolio project by James L. Toland / TolandLabs.

## Features

- Forecasts MRR, ARR, churn, revenue, COGS, gross profit, payroll, operating result and cash over 24 months
- Models hiring and fully loaded employee costs
- Compares base, upside and downside revenue/churn scenarios
- Calculates illustrative CAC, LTV/CAC, burn multiple and modeled cash depletion
- Exports forecast data from a Streamlit dashboard
- Runs unit tests with GitHub Actions

## Run locally

```bash
git clone https://github.com/TolandLabs/startup-fp-and-a-engine.git
cd startup-fp-and-a-engine
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\Scripts\activate`.

Run tests:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Project layout

- `fpa/model.py`: deterministic SaaS operating model and financial metrics
- `app.py`: interactive Streamlit UI
- `data/synthetic_assumptions.csv`: fictional reference assumptions
- `tests/test_model.py`: automated tests
- `.github/workflows/tests.yml`: CI workflow

## Assumptions and limitations

This is an illustrative operating model, not an accounting system or validated investment forecast. Revenue is approximated using average beginning- and end-of-month MRR. Gross margin is assumed, not reconciled to cloud invoices. Headcount grows at the beginning of each subsequent month. Cash changes equal modeled operating results; there is no working capital, capital expenditure, financing, taxes, debt, or deferred revenue. LTV is a simplified steady-state estimate. CAC uses acquisition spend divided by new customers, while new MRR and new-customer assumptions are independently configurable. Scenarios are deterministic sensitivity cases, not probability forecasts.

## Data protection

All example numbers are fictional and synthetic. No actual Eighth Judicial District Courts of New Mexico data, employee information, financial records or credentials are used. No financial systems or APIs are connected.

## License

MIT — see [LICENSE](LICENSE).
