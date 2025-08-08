
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.metrics import load, funnel_counts, funnel_cr, weekly_kpis, top_geo, cohort_retention, payment_breakdown, category_revenue, sla_distribution

from src.metrics import load, funnel_counts, funnel_cr, weekly_kpis, top_geo, cohort_retention, payment_breakdown, category_revenue, sla_distribution

OUT_HTML = Path('docs/index.html')

def funnel_fig(fdict):
    stages = ['created','approved','delivered_carrier','delivered_customer']
    values = [fdict.get(s,0) for s in stages]
    fig = go.Figure(go.Funnel(y=stages, x=values, textinfo="value+percent previous"))
    fig.update_layout(title='Order Funnel')
    return fig

def weekly_fig(dfw):
    fig = px.line(dfw, x='order_purchase_week', y=['orders','delivered','revenue'], markers=True)
    fig.update_layout(title='Weekly Orders, Deliveries, and Revenue')
    return fig

def aov_fig(dfw):
    fig = px.line(dfw, x='order_purchase_week', y='aov', markers=True)
    fig.update_layout(title='Average Order Value (Weekly)')
    return fig

def geo_fig(geo):
    fig = px.bar(geo, x='revenue', y='customer_city', color='customer_state', orientation='h')
    fig.update_layout(title='Top Cities by Delivered Revenue')
    return fig

def payment_fig(pb):
    if pb.empty:
        return go.Figure()
    fig = px.pie(pb, names='payment_type', values='total', hole=0.4)
    fig.update_layout(title='Payment Methods (value share)')
    return fig

def category_fig(cat):
    if cat.empty:
        return go.Figure()
    fig = px.bar(cat, x='revenue', y='product_category_name', orientation='h')
    fig.update_layout(title='Top Categories by Revenue')
    return fig

def sla_fig(dist):
    if dist.empty:
        return go.Figure()
    fig = px.histogram(dist, nbins=40)
    fig.update_layout(title='Delivery SLA (days) — Histogram')
    return fig

def cohort_fig(retention):
    fig = px.imshow(retention, aspect='auto', color_continuous_scale='Blues', origin='lower')
    fig.update_layout(title='Cohort Retention (share of original cohort)',
                      xaxis_title='Months since first order',
                      yaxis_title='Cohort month')
    return fig

def main():
    df = load()
    fdict = funnel_counts(df)
    cr_step, overall = funnel_cr(fdict)
    weekly = weekly_kpis(df)
    geo = top_geo(df, n=12)
    retention = cohort_retention(df)
    pb = payment_breakdown()
    cat = category_revenue(15)
    sla = sla_distribution(df)

    figs = [
        funnel_fig(fdict),
        weekly_fig(weekly),
        aov_fig(weekly),
        payment_fig(pb),
        category_fig(cat),
        sla_fig(sla),
        geo_fig(geo),
        cohort_fig(retention),
    ]

    parts = [f"""
    <h1 style='font-family:system-ui,Segoe UI,Roboto'>E-commerce Sales Funnel Dashboard</h1>
    <p>Overall conversion (created → delivered_customer): <b>{overall:.2%}</b></p>
    <ul>
      {''.join(f'<li>{k}: <b>{v:.2%}</b></li>' for k, v in cr_step.items())}
    </ul>
    """]
    for fig in figs:
        parts.append(fig.to_html(full_html=False, include_plotlyjs='cdn'))

    html = """
<!doctype html>
<html><head><meta charset='utf-8'><title>Olist Funnel Dashboard</title></head>
<body style='margin:24px;max-width:1200px;margin-left:auto;margin-right:auto'>
%s
</body></html>
""" % ("\n".join(parts))

    OUT_HTML.write_text(html, encoding='utf-8')
    print("Wrote", OUT_HTML.resolve())

if __name__ == '__main__':
    main()