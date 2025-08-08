import pandas as pd
from pathlib import Path

def main():
    df = pd.read_parquet('data/processed/orders_master.parquet')
    # Tidy orders table
    df.to_csv('assets/csv/orders_master.csv', index=False)
    # Weekly KPIs
    wk = (df.groupby('order_purchase_week')
            .agg(orders=('order_id','nunique'),
                 delivered=('order_delivered_customer_date', lambda s: s.notna().sum()),
                 revenue=('revenue','sum'))
            .reset_index())
    wk.to_csv('assets/csv/weekly_kpis.csv', index=False)
    # Delivered geo
    delivered = df[df['status_stage']=='delivered_customer']
    geo = (delivered.groupby(['customer_state','customer_city'])
                .agg(revenue=('revenue','sum'),
                     orders=('order_id','nunique'))
                .reset_index()
                .sort_values('revenue', ascending=False))
    geo.to_csv('assets/csv/geo_delivered.csv', index=False)
    print('CSV exported to assets/csv')

if __name__ == '__main__':
    main()