import pytest
from dataclasses import replace
from fpa.model import Assumptions, project, metrics, scenarios


def test_24_month_forecast_and_cash_rollforward():
    a = Assumptions()
    df = project(a)
    assert len(df) == 24
    assert df.iloc[0].ending_cash == pytest.approx(a.starting_cash + df.iloc[0].operating_result)
    assert df.iloc[-1].ending_cash == pytest.approx(a.starting_cash + df.operating_result.sum())


def test_mrr_rollforward_and_arr():
    a = Assumptions()
    row = project(a).iloc[0]
    assert row.ending_mrr == pytest.approx(a.starting_mrr * (1-a.monthly_churn) + a.new_mrr)
    assert row.arr == pytest.approx(row.ending_mrr * 12)


def test_scenarios_rank_arr():
    a = Assumptions()
    s = scenarios(a)
    assert s["Upside"].iloc[-1].arr > s["Base"].iloc[-1].arr > s["Downside"].iloc[-1].arr


def test_no_customers_yields_undefined_cac():
    a = replace(Assumptions(), new_customers=0)
    assert metrics(a, project(a))["cac"] is None


def test_zero_churn_yields_undefined_ltv():
    a = replace(Assumptions(), monthly_churn=0)
    assert metrics(a, project(a))["ltv"] is None


def test_invalid_assumptions():
    with pytest.raises(ValueError):
        project(replace(Assumptions(), gross_margin=1.2))
    with pytest.raises(ValueError):
        project(replace(Assumptions(), starting_cash=-1))


def test_runway_month_detects_depletion():
    a = replace(Assumptions(), starting_cash=1, starting_mrr=0, new_mrr=0)
    assert metrics(a, project(a))["runway_month"] == 1
