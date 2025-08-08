import pandas as pd
from pathlib import Path

INP = Path('data/processed/orders_master.parquet')

def load():
    return pd.read_parquet(INP)

def funnel_counts(df):
    order_stage = df.groupby('status_stage').size().reindex(['created','approved','delivered_carrier','delivered_customer']).fillna(0).astype(int)
    return order_stage.to_dict()

def funnel_cr(funnel_dict):
    stages = ['created','approved','delivered_carrier','delivered_customer']
    counts = [funnel_dict.get(s,0) for s in stages]
    cr_step = {}
    for i in range(1, len(stages)):
        prev, cur = counts[i-1], counts[i]
        cr_step[f"{stages[i-1]}→{stages[i]}"] = (cur/prev) if prev else 0.0
    overall = (counts[-1]/counts[0]) if counts[0] else 0.0
    return cr_step, overall

def weekly_kpis(df):
    weekly = (df.groupby('order_purchase_week')
                .agg(orders=('order_id','nunique'),
                     delivered=('order_delivered_customer_date', lambda s: s.notna().sum()),
                     revenue=('revenue','sum'),
                     aov=('revenue', lambda s: s.sum()/max(1, s.count())))
                .reset_index())
    return weekly

def top_geo(df, n=10):
    delivered = df[df['status_stage']=='delivered_customer']
    geo = (delivered.groupby(['customer_state','customer_city'])
                  .agg(revenue=('revenue','sum'),
                       orders=('order_id','nunique'))
                  .reset_index()
                  .sort_values('revenue', ascending=False)
                  .head(n))
    return geo

def cohort_retention(df):
    d = df.dropna(subset=['order_purchase_month','cohort_month']).copy()
    d['period_index'] = ((d['order_purchase_month'].dt.to_period('M').view('i8') -
                          d['cohort_month'].dt.to_period('M').view('i8'))).astype(int)
    pivot = (d.groupby(['cohort_month','period_index'])['customer_unique_id']
               .nunique()
               .reset_index()
               .pivot(index='cohort_month', columns='period_index', values='customer_unique_id'))
    cohort_sizes = pivot[0]
    retention = pivot.divide(cohort_sizes, axis=0).fillna(0.0)
    return retention

def payment_breakdown():
    p = Path('data/processed/payment_type_summary.parquet')
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame(columns=['payment_type','total','n'])

def category_revenue(top_n=15):
    p = Path('data/processed/category_revenue.parquet')
    if not p.exists():
        return pd.DataFrame(columns=['product_category_name','revenue','items'])
    df = pd.read_parquet(p).sort_values('revenue', ascending=False).head(top_n)
    return df

def sla_distribution(df):
    d = df['sla_days'].dropna()
    return d