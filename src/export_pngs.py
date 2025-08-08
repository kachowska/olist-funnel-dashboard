import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from src.metrics import load, funnel_counts, funnel_cr, weekly_kpis, top_geo, category_revenue

IMG = Path('assets/img'); IMG.mkdir(parents=True, exist_ok=True)

def funnel_png(df):
    fdict = funnel_counts(df)
    stages = ['created','approved','delivered_carrier','delivered_customer']
    values = [fdict.get(s,0) for s in stages]
    fig = go.Figure(go.Funnel(y=stages, x=values, textinfo='value+percent previous'))
    fig.write_image(IMG / 'funnel.png', scale=2, width=1000, height=700)

def weekly_png(dfw):
    fig = px.line(dfw, x='order_purchase_week', y=['orders','delivered','revenue'], markers=True)
    fig.write_image(IMG / 'weekly.png', scale=2, width=1200, height=700)

def categories_png(cat):
    if cat.empty: return
    fig = px.bar(cat.head(15), x='revenue', y='product_category_name', orientation='h')
    fig.write_image(IMG / 'categories.png', scale=2, width=1000, height=800)

def main():
    df = load()
    funnel_png(df)
    weekly_png(weekly_kpis(df))
    categories_png(category_revenue(30))
    print('PNG charts exported to assets/img')

if __name__ == '__main__':
    main()