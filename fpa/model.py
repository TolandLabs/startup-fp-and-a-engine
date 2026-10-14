"""Monthly SaaS operating model using explicit, inspectable assumptions."""
from dataclasses import dataclass, replace
from math import isfinite
import pandas as pd


@dataclass(frozen=True)
class Assumptions:
    starting_cash: float = 2_500_000
    starting_mrr: float = 120_000
    new_mrr: float = 15_000
    monthly_churn: float = 0.025
    gross_margin: float = 0.78
    starting_headcount: int = 12
    monthly_hires: int = 1
    monthly_loaded_cost: float = 11_000
    monthly_nonpayroll_opex: float = 55_000
    cac_spend: float = 30_000
    new_customers: int = 15
    arpa: float = 800
    months: int = 24

    def validate(self):
        if self.months < 1 or self.months > 120:
            raise ValueError("months must be between 1 and 120")
        if self.starting_headcount < 0 or self.monthly_hires < 0 or self.new_customers < 0:
            raise ValueError("headcount, hires and customers must be nonnegative")
        for name in ("starting_cash", "starting_mrr", "new_mrr", "monthly_loaded_cost",
                     "monthly_nonpayroll_opex", "cac_spend", "arpa"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        for name in ("monthly_churn", "gross_margin"):
            value = getattr(self, name)
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")


def project(a: Assumptions) -> pd.DataFrame:
    """Forecast month-end MRR, cash and operating results; no financing/taxes modeled."""
    a.validate()
    mrr, cash, rows = a.starting_mrr, a.starting_cash, []
    for month in range(1, a.months + 1):
        beginning_mrr = mrr
        churned_mrr = beginning_mrr * a.monthly_churn
        mrr = beginning_mrr - churned_mrr + a.new_mrr
        revenue = (beginning_mrr + mrr) / 2  # average recurring revenue during month
        cogs = revenue * (1 - a.gross_margin)
        headcount = a.starting_headcount + a.monthly_hires * (month - 1)
        payroll = headcount * a.monthly_loaded_cost
        opex = payroll + a.monthly_nonpayroll_opex + a.cac_spend
        operating_result = revenue - cogs - opex
        cash += operating_result  # illustrative all-cash assumption
        rows.append(dict(month=month, beginning_mrr=beginning_mrr,
                         churned_mrr=churned_mrr, ending_mrr=mrr, arr=mrr * 12,
                         revenue=revenue, cogs=cogs, gross_profit=revenue-cogs,
                         gross_margin=a.gross_margin, headcount=headcount,
                         payroll=payroll, operating_expenses=opex,
                         operating_result=operating_result, ending_cash=cash,
                         net_burn=max(-operating_result, 0)))
    return pd.DataFrame(rows)


def metrics(a: Assumptions, forecast: pd.DataFrame) -> dict:
    """CAC, LTV, burn multiple and modeled runway; undefined ratios return None."""
    last = forecast.iloc[-1]
    cac = a.cac_spend / a.new_customers if a.new_customers else None
    ltv = (a.arpa * a.gross_margin / a.monthly_churn) if a.monthly_churn else None
    ltv_cac = ltv / cac if ltv is not None and cac and cac > 0 else None
    first = forecast.iloc[0]
    net_new_arr = (last.ending_mrr - a.starting_mrr) * 12
    total_burn = max(a.starting_cash - last.ending_cash, 0)
    burn_multiple = total_burn / net_new_arr if net_new_arr > 0 else None
    depleted = forecast.loc[forecast.ending_cash <= 0, "month"]
    runway_month = int(depleted.iloc[0]) if not depleted.empty else None
    return dict(cac=cac, ltv=ltv, ltv_cac=ltv_cac,
                burn_multiple=burn_multiple, runway_month=runway_month,
                ending_arr=float(last.arr), ending_cash=float(last.ending_cash),
                first_month_result=float(first.operating_result))


def scenarios(a: Assumptions) -> dict[str, pd.DataFrame]:
    """Three explicit operating cases, not statistical predictions."""
    return {
        "Base": project(a),
        "Upside": project(replace(a, new_mrr=a.new_mrr * 1.3,
                                   monthly_churn=a.monthly_churn * 0.8)),
        "Downside": project(replace(a, new_mrr=a.new_mrr * 0.7,
                                     monthly_churn=min(1, a.monthly_churn * 1.4))),
    }
