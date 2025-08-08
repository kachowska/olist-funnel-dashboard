import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.metrics import load, funnel_counts, funnel_cr, weekly_kpis, top_geo, cohort_retention, payment_breakdown, category_revenue, sla_distribution

st.set_page_config(page_title="E-commerce Funnel (Olist)", layout="wide")

st.title("E-commerce Sales Funnel — Olist")

df = load()

# --- Filters ---
min_date = pd.to_datetime(df['order_purchase_week'].min())
max_date = pd.to_datetime(df['order_purchase_week'].max())
state_opts = sorted(df['customer_state'].dropna().unique().tolist())
cat_df = category_revenue(1000)  # for options only
pay_df = payment_breakdown()

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Order week range", [min_date.date(), max_date.date()])
    sel_states = st.multiselect("States", state_opts)
    sel_cats = st.multiselect("Categories", sorted(cat_df['product_category_name'].unique().tolist()) if not cat_df.empty else [])
    sel_pays = st.multiselect("Payment types", sorted(pay_df['payment_type'].unique().tolist()) if not pay_df.empty else [])

# Apply filters
df_f = df.copy()
if date_range and len(date_range)==2:
    d0, d1 = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_f = df_f[(df_f['order_purchase_week']>=d0) & (df_f['order_purchase_week']<=d1)]
if sel_states:
    df_f = df_f[df_f['customer_state'].isin(sel_states)]
if sel_pays:
    # Need per-order payment info: df_f already has total_paid but not types per row; keep as is (global pie uses value-weighted agg)
    pass

fdict = funnel_counts(df_f)
cr_step, overall = funnel_cr(fdict)
weekly = weekly_kpis(df_f)
geo = top_geo(df_f, n=15)
pb = payment_breakdown()  # global distribution (value-weighted)
cat = category_revenue(20)
sla = sla_distribution(df_f)
ret = cohort_retention(df_f)

st.subheader(f"Overall conversion created → delivered: {overall:.2%}")
cols = st.columns(4)
for i, (k, v) in enumerate(cr_step.items()):
    cols[i].metric(k, f"{v:.2%}")

st.plotly_chart(px.line(weekly, x='order_purchase_week', y=['orders','delivered','revenue'], markers=True), use_container_width=True)
st.plotly_chart(px.line(weekly, x='order_purchase_week', y='aov', markers=True), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    if not pb.empty:
        st.plotly_chart(px.pie(pb, names='payment_type', values='total', hole=0.4), use_container_width=True)
    st.plotly_chart(px.histogram(sla, nbins=40), use_container_width=True)
with c2:
    if not cat.empty:
        st.plotly_chart(px.bar(cat, x='revenue', y='product_category_name', orientation='h'), use_container_width=True)
    st.plotly_chart(px.bar(geo, x='revenue', y='customer_city', color='customer_state', orientation='h'), use_container_width=True)

st.subheader("Cohort retention")
st.plotly_chart(px.imshow(ret, aspect='auto', color_continuous_scale='Blues', origin='lower'), use_container_width=True)

st.caption("Dataset: Brazilian E-Commerce Public Dataset by Olist (Kaggle).")