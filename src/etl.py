import os
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path('data/raw')
OUT = Path('data/processed')
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(name):
    candidates = list(RAW.glob(f"{name}*.csv"))
    if not candidates:
        raise FileNotFoundError(f"Could not find CSV for: {name} in {RAW.resolve()}")
    return pd.read_csv(candidates[0])

def main():
    # --- Load ---
    orders = read_csv('olist_orders_dataset')
    customers = read_csv('olist_customers_dataset')
    payments = read_csv('olist_order_payments_dataset')
    items = read_csv('olist_order_items_dataset')
    products = read_csv('olist_products_dataset')

    # --- Clean / types ---
    date_cols = ['order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_estimated_delivery_date']
    for c in date_cols:
        if c in orders.columns:
            orders[c] = pd.to_datetime(orders[c], errors='coerce')

    # --- Furthest stage ---
    def furthest_stage(row):
        stages = [
            ('created', pd.notna(row.get('order_purchase_timestamp'))),
            ('approved', pd.notna(row.get('order_approved_at'))),
            ('delivered_carrier', pd.notna(row.get('order_delivered_carrier_date'))),
            ('delivered_customer', pd.notna(row.get('order_delivered_customer_date'))),
        ]
        last = 'created'
        for name, ok in stages:
            if ok:
                last = name
        return last

    orders['status_stage'] = orders.apply(furthest_stage, axis=1)
    orders['order_purchase_date'] = orders['order_purchase_timestamp'].dt.date
    orders['order_purchase_week'] = orders['order_purchase_timestamp'].dt.to_period('W').dt.start_time
    orders['order_purchase_month'] = orders['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()

    # SLA (in days) from approved to delivered to customer
    orders['sla_days'] = (orders['order_delivered_customer_date'] - orders['order_approved_at']).dt.total_seconds() / (3600*24)

    # --- Payments summary per order ---
    pay = payments.groupby('order_id').agg(total_paid=('payment_value','sum')).reset_index()

    # payment_type distribution (value-weighted and count-weighted)
    pay_type_value = payments.groupby('payment_type').agg(total=('payment_value','sum'),
                                                          n=('payment_value','count')).reset_index()
    pay_type_value.to_parquet(OUT / 'payment_type_summary.parquet', index=False)

    # --- Items summary per order ---
    items['revenue'] = items['price'] + items['freight_value']
    it = items.groupby('order_id').agg(items=('order_item_id','count'),
                                       revenue=('revenue','sum')).reset_index()

    # Category revenue (delivered only will be filtered later on dashboard side)
    cat = (items.merge(products[['product_id','product_category_name']], on='product_id', how='left')
                .assign(product_category_name=lambda d: d['product_category_name'].fillna('unknown'))
                .groupby('product_category_name', as_index=False)
                .agg(revenue=('revenue','sum'), items=('order_item_id','count')))
    cat.to_parquet(OUT / 'category_revenue.parquet', index=False)

    # --- Master orders table ---
    m = (orders
         .merge(customers[['customer_id','customer_unique_id','customer_city','customer_state']], on='customer_id', how='left')
         .merge(pay, on='order_id', how='left')
         .merge(it, on='order_id', how='left'))

    # --- Cohort month ---
    first = (m.groupby('customer_unique_id')['order_purchase_month']
               .min()
               .rename('cohort_month')
               .reset_index())
    m = m.merge(first, on='customer_unique_id', how='left')

    # --- Save processed tables ---
    m.to_parquet(OUT / 'orders_master.parquet', index=False)
    print("Wrote:", (OUT / 'orders_master.parquet').resolve())

if __name__ == '__main__':
    main()