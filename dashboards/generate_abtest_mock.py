# dashboards/generate_abtest_mock.py
import hashlib
import pandas as pd
from pathlib import Path

# --- make project root importable ---
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from statsmodels.stats.proportion import proportions_ztest, proportion_effectsize
from statsmodels.stats.power import NormalIndPower

OUT = Path('docs/abtest.html')

def assign_variant(order_id: str) -> str:
    """Deterministic 50/50 split by hashing order_id."""
    h = hashlib.md5(str(order_id).encode()).hexdigest()
    return 'B' if int(h[:2], 16) % 2 else 'A'

def main():
    df = pd.read_parquet('data/processed/orders_master.parquet')

    # Binary conversion = delivered to customer
    df['converted'] = (df['status_stage'] == 'delivered_customer').astype(int)
    df['variant'] = df['order_id'].apply(assign_variant)

    # Aggregate
    agg = (df.groupby('variant')['converted']
             .agg(conversions='sum', n='count')
             .reindex(['A','B']).fillna(0).astype(int))

    convA, nA = int(agg.loc['A','conversions']), int(agg.loc['A','n'])
    convB, nB = int(agg.loc['B','conversions']), int(agg.loc['B','n'])
    pA = (convA / nA) if nA else 0.0
    pB = (convB / nB) if nB else 0.0
    uplift = pB - pA

    # One-sided z-test: H1: pB > pA
    stat, pval = proportions_ztest([convB, convA], [nB, nA], alternative='larger')

    # Power analysis: n per group for MDE = +2pp over baseline
    baseline = pA if pA > 0 else 0.10
    mde = 0.02
    analysis = NormalIndPower()
    eff = proportion_effectsize(baseline, baseline + mde)
    n_required = analysis.solve_power(effect_size=eff, alpha=0.05, power=0.8, ratio=1.0, alternative='larger')

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Mock A/B Test Report</title>
<style>body{{font-family:system-ui;max-width:860px;margin:24px auto;line-height:1.5}}</style></head>
<body>
<h1>Mock A/B Test — Promo Banner</h1>
<p>Assignment: 50/50 by hashing <code>order_id</code>. Conversion = delivered to customer.</p>
<h2>Results</h2>
<ul>
  <li>A: {convA}/{nA} = {pA:.2%}</li>
  <li>B: {convB}/{nB} = {pB:.2%}</li>
  <li>Uplift: <b>{uplift:.2%}</b></li>
  <li>One-sided z-test p-value (B &gt; A): <b>{pval:.4f}</b></li>
</ul>
<h2>Power analysis</h2>
<p>Baseline = {baseline:.2%}, MDE = +2pp, α = 0.05, power = 0.8 → required n per group ≈ <b>{int(n_required)}</b></p>
<p><i>Note:</i> Mock analysis for portfolio; in production randomize by session/visitor and pre-register the design.</p>
</body></html>"""

    OUT.write_text(html, encoding='utf-8')
    print("Wrote", OUT.resolve())

if __name__ == '__main__':
    main()
