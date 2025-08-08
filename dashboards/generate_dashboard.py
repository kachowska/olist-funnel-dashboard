# dashboards/generate_dashboard.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- make project root importable ---
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.metrics import (
    load,
    funnel_counts,
    funnel_cr,
    weekly_kpis,
    top_geo,
    cohort_retention,
    payment_breakdown,
    category_revenue,
    sla_distribution,
)

OUT_HTML = Path("docs/index.html")
REPO_URL = "https://github.com/kachowska/olist-funnel-dashboard"


# -------------------------- figures --------------------------

def funnel_fig(fdict: dict) -> go.Figure:
    stages = ["created", "approved", "delivered_carrier", "delivered_customer"]
    values = [fdict.get(s, 0) for s in stages]
    fig = go.Figure(go.Funnel(y=stages, x=values, textinfo="value+percent previous"))
    fig.update_layout(title="Order Funnel")
    return fig


def weekly_fig(dfw: pd.DataFrame) -> go.Figure:
    fig = px.line(dfw, x="order_purchase_week", y=["orders", "delivered", "revenue"], markers=True)
    fig.update_layout(title="Weekly Orders, Deliveries, and Revenue")
    return fig


def aov_fig(dfw: pd.DataFrame) -> go.Figure:
    fig = px.line(dfw, x="order_purchase_week", y="aov", markers=True)
    fig.update_layout(title="Average Order Value (Weekly)")
    return fig


def geo_fig(geo: pd.DataFrame) -> go.Figure:
    fig = px.bar(geo, x="revenue", y="customer_city", color="customer_state", orientation="h")
    fig.update_layout(title="Top Cities by Delivered Revenue")
    return fig


def payment_fig(pb: pd.DataFrame) -> go.Figure:
    if pb.empty:
        return go.Figure()
    fig = px.pie(pb, names="payment_type", values="total", hole=0.4)
    fig.update_layout(title="Payment Methods (value share)")
    return fig


def category_fig(cat: pd.DataFrame) -> go.Figure:
    if cat.empty:
        return go.Figure()
    fig = px.bar(cat, x="revenue", y="product_category_name", orientation="h")
    fig.update_layout(title="Top Categories by Revenue")
    return fig


def sla_fig(dist: pd.Series) -> go.Figure:
    if dist.empty:
        return go.Figure()
    fig = px.histogram(dist, nbins=40)
    fig.update_layout(title="Delivery SLA (days) — Histogram")
    return fig


def cohort_fig(retention: pd.DataFrame) -> go.Figure:
    fig = px.imshow(retention, aspect="auto", color_continuous_scale="Blues", origin="lower")
    fig.update_layout(
        title="Cohort Retention (share of original cohort)",
        xaxis_title="Months since first order",
        yaxis_title="Cohort month",
    )
    return fig


# -------------------------- build page --------------------------

def main():
    # data & metrics
    df = load()
    fdict = funnel_counts(df)
    cr_step, overall = funnel_cr(fdict)
    weekly = weekly_kpis(df)
    geo = top_geo(df, n=12)
    retention = cohort_retention(df)
    pb = payment_breakdown()
    cat = category_revenue(15)
    sla = sla_distribution(df)

    # figures to html fragments
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
    figs_html = "\n".join(fig.to_html(full_html=False, include_plotlyjs="cdn") for fig in figs)

    # intro block with KPIs
    intro_html = (
        f"<section>"
        f"<h1 style='margin:0 0 8px 0'>E-commerce Sales Funnel Dashboard</h1>"
        f"<p style='margin:0 0 12px 0'>Overall conversion (created → delivered_customer): "
        f"<b>{overall:.2%}</b></p>"
        + "<ul style='margin:0 0 24px 18px'>"
        + "".join(f"<li>{k}: <b>{v:.2%}</b></li>" for k, v in cr_step.items())
        + "</ul>"
        f"</section>"
    )

    # full static page with top nav
    page_html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Olist Funnel Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      :root {{ --maxw: 1200px; }}
      body {{
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
        margin: 24px;
      }}
      .wrap {{ max-width: var(--maxw); margin: 0 auto; }}
      header.nav {{
        display: flex; gap: 16px; align-items: center; justify-content: space-between;
        padding: 8px 0 16px 0; border-bottom: 1px solid #e5e7eb; margin-bottom: 16px;
      }}
      header.nav .brand {{ font-weight: 700; font-size: 18px; }}
      header.nav nav a {{ margin-left: 16px; text-decoration: none; color: #1f2937; }}
      header.nav nav a:hover {{ text-decoration: underline; }}
      footer {{ color:#6b7280; margin: 24px 0; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header class="nav">
        <div class="brand">E-commerce Funnel (Olist)</div>
        <nav>
          <a href="index.html">Dashboard</a>
          <a href="abtest.html">A/B test report</a>
          <a href="{REPO_URL}">Repository</a>
        </nav>
      </header>

      {intro_html}

      {figs_html}

      <footer>
        Dataset: Brazilian E-Commerce Public Dataset by Olist (Kaggle).
      </footer>
    </div>
  </body>
</html>"""

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(page_html, encoding="utf-8")
    print("Wrote", OUT_HTML.resolve())


if __name__ == "__main__":
    main()
