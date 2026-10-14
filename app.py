"""Interactive synthetic-data SaaS financial planning dashboard."""
import streamlit as st
import plotly.express as px
from fpa.model import Assumptions, project, metrics, scenarios

st.set_page_config(page_title="Startup FP&A Engine", layout="wide")
st.title("Startup FP&A Engine")
st.caption("Illustrative SaaS model • synthetic assumptions • not accounting or investment advice")

with st.sidebar:
    st.header("Operating assumptions")
    cash = st.number_input("Starting cash ($)", min_value=0, value=2_500_000, step=100_000)
    mrr = st.number_input("Starting MRR ($)", min_value=0, value=120_000, step=5_000)
    new_mrr = st.number_input("New MRR added each month ($)", min_value=0, value=15_000, step=1_000)
    churn = st.slider("Monthly MRR churn (%)", 0.0, 20.0, 2.5, 0.5) / 100
    gm = st.slider("Gross margin (%)", 0, 100, 78) / 100
    hc = st.number_input("Starting headcount", min_value=0, value=12)
    hires = st.number_input("New hires per month", min_value=0, value=1)
    cost = st.number_input("Monthly fully loaded cost per employee ($)", min_value=0, value=11_000, step=500)
    other = st.number_input("Other monthly operating expenses ($)", min_value=0, value=55_000, step=5_000)
    marketing = st.number_input("Monthly acquisition spend ($)", min_value=0, value=30_000, step=5_000)
    customers = st.number_input("New customers per month", min_value=0, value=15)
    arpa = st.number_input("Monthly revenue per customer ($)", min_value=0, value=800, step=50)

a = Assumptions(starting_cash=cash, starting_mrr=mrr, new_mrr=new_mrr,
                monthly_churn=churn, gross_margin=gm, starting_headcount=hc,
                monthly_hires=hires, monthly_loaded_cost=cost,
                monthly_nonpayroll_opex=other, cac_spend=marketing,
                new_customers=customers, arpa=arpa)
df = project(a)
k = metrics(a, df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ending ARR", f"${k['ending_arr']:,.0f}")
c2.metric("Ending cash", f"${k['ending_cash']:,.0f}")
c3.metric("CAC", f"${k['cac']:,.0f}" if k["cac"] is not None else "N/A")
c4.metric("LTV / CAC", f"{k['ltv_cac']:.1f}x" if k["ltv_cac"] is not None else "N/A")
st.info(f"Modeled cash depletion: month {k['runway_month']}" if k["runway_month"] else "Cash does not deplete within the 24-month model horizon.")
cases = scenarios(a)
case_data = []
for name, frame in cases.items():
    for _, row in frame.iterrows():
        case_data.append({"Scenario": name, "Month": int(row.month),
                          "Ending cash": float(row.ending_cash),
                          "ARR": float(row.arr)})
import pandas as pd
long = pd.DataFrame(case_data)
tab1, tab2, tab3 = st.tabs(["Cash scenarios", "ARR scenarios", "Monthly model"])
with tab1:
    st.plotly_chart(px.line(long, x="Month", y="Ending cash", color="Scenario"), use_container_width=True)
with tab2:
    st.plotly_chart(px.line(long, x="Month", y="ARR", color="Scenario"), use_container_width=True)
with tab3:
    st.dataframe(df.style.format(precision=2), use_container_width=True)
    st.download_button("Download model CSV", df.to_csv(index=False),
                       file_name="synthetic_startup_forecast.csv", mime="text/csv")
st.caption("Revenue uses average beginning/ending MRR; cash equals cumulative operating result. Excludes working capital, taxes, debt and fundraising. LTV is simplified ARPA × gross margin / churn.")
