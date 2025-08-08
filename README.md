
# E-commerce Sales Funnel Dashboard (Olist / Kaggle)

A hands-on data analysis project that builds an end-to-end **sales funnel dashboard** on top of the popular **Brazilian E-Commerce Olist** dataset (Kaggle). It showcases:
- Clean **ETL** from raw CSVs → tidy tables (`orders`, `payments`, `items`, `customers`)
- Core **funnel metrics**: orders created → approved (paid) → delivered carrier → delivered customer
- **Conversion rates, AOV, revenue**, weekly trends, and **cohort retention**
- A **static, shareable Plotly HTML dashboard** (no server!) that you can host on **GitHub Pages**

> Perfect as a first portfolio project for @kachowska: clear business questions, transparent pipeline, and shareable outputs.

---

## 1) Dataset (Kaggle)

We use the **Brazilian E-Commerce Public Dataset by Olist** on Kaggle.

- Kaggle page: `olistbr/brazilian-ecommerce`
- Download with the Kaggle CLI (after setting up your `~/.kaggle/kaggle.json`):
  ```bash
  mkdir -p data/raw
  kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw
  cd data/raw && unzip brazilian-ecommerce.zip && cd ../..
  ```

> If you prefer a lighter dataset, you can swap to **Online Retail II (UCI)**, but all code here is prepared for Olist.

---

## 2) Quickstart

Create a virtual environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

Run ETL and generate the dashboard:

```bash
python src/etl.py
python dashboards/generate_dashboard.py
```

Open the dashboard:
- Local file: `docs/index.html`
- Or enable **GitHub Pages** → serve from `/docs` branch folder → share the public URL.

---

## 3) Repository structure

```
.
├── assets/
├── dashboards/
│   └── generate_dashboard.py
├── data/
│   ├── processed/               # parquet outputs
│   └── raw/                     # put Kaggle CSVs here
├── docs/                        # GitHub Pages output (index.html)
├── notebooks/
│   └── 01_olist_exploration.ipynb
├── src/
│   ├── etl.py
│   └── metrics.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 4) What the dashboard shows

- **Funnel counts & CR**: created → approved → delivered_carrier → delivered_customer  
- **AOV & revenue** over time (by week/month)  
- **Top states/cities** by delivered revenue  
- **Cohort analysis**: first-order month → repeat buyers

All figures are exported to a single `docs/index.html` (Plotly); you can open in any browser and embed into your portfolio.

---

## 5) Business questions answered

1. Where do orders drop off most often in the delivery funnel?
2. What’s our overall conversion from *created* to *delivered to customer*?
3. How do AOV and revenue trend weekly?
4. Which customer geographies contribute the most revenue?
5. Do new customer cohorts come back for repeat purchases?

---

## 6) Re-run & extend

- Replace visual themes, add more breakdowns (payment type, product category).
- Add **AB-test** mock analysis for promo banners (extend `metrics.py`).  
- Swap to **Tableau/Looker Studio** using the processed parquet files.

---

## 7) License

Code is MIT. Data follows the Kaggle dataset license terms — do **not** commit raw data.

---


---

## 8) Live links (replace after you push)
- **GitHub Repo:** https://github.com/kachowska/olist-funnel-dashboard
- **GitHub Pages (Dashboard):** https://kachowska.github.io/olist-funnel-dashboard/
- **Streamlit (local):** `streamlit run app.py`

## 9) Generate A/B Test mock report
```bash
python src/etl.py                  # if not yet
python dashboards/generate_abtest_mock.py
# open docs/abtest.html
```

---

## 10) Tidy CSV exports (for Tableau/Looker)
```bash
python src/export_csvs.py
# files in assets/csv/
```

## 11) PNG previews (for portfolio thumbnails)
```bash
python src/export_pngs.py
# files in assets/img/
```

## 12) Streamlit with filters
Run `streamlit run app.py` and use the sidebar to filter by date range, state, categories.
