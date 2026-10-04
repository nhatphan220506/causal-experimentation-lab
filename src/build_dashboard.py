import json
from pathlib import Path

from src.config import GENERATED_DIR, ROOT


def pct(value, digits=2):
    return f"{value * 100:.{digits}f}%"


def main() -> None:
    audit = json.loads((GENERATED_DIR / "data_audit.json").read_text())
    ate = json.loads((GENERATED_DIR / "ate_results.json").read_text())
    uplift = json.loads((GENERATED_DIR / "uplift_policy_results.json").read_text())
    summary = audit["summary"]
    visit, conversion = ate["visit"], ate["conversion"]
    diagnostics = uplift["diagnostics"]
    top = uplift["deciles"][0]
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Causal Experimentation Lab</title>
<style>
:root{{--ink:#10213d;--muted:#627089;--blue:#2563eb;--teal:#0f766e;--paper:#f6f8fc;--line:#dbe3ef}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Inter,system-ui,sans-serif}}
main{{max-width:1120px;margin:auto;padding:54px 24px 80px}} .eyebrow{{color:var(--blue);font-weight:750;letter-spacing:.1em;text-transform:uppercase;font-size:12px}}
h1{{font-size:clamp(36px,6vw,68px);line-height:1.02;letter-spacing:-.045em;margin:12px 0 18px;max-width:900px}} h2{{font-size:26px;margin-top:48px}}
.lead{{font-size:20px;color:var(--muted);max-width:800px}} .grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:34px 0}}
.card,.panel{{background:white;border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 8px 28px #10213d0a}}
.value{{font-size:29px;font-weight:780;letter-spacing:-.03em}} .label{{color:var(--muted);font-size:13px;margin-top:4px}}
.decision{{border-left:5px solid var(--teal);padding:24px 28px;background:#effcf8;border-radius:10px;margin:30px 0}}
.charts{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} .charts img{{width:100%;display:block}}
.panel h3{{margin:0 0 8px}} .panel p{{color:var(--muted)}} code{{background:#e8eef8;padding:2px 6px;border-radius:5px}}
.warning{{background:#fff8ed;border-color:#fed7aa}} footer{{margin-top:56px;color:var(--muted);font-size:13px}}
@media(max-width:800px){{.grid{{grid-template-columns:1fr 1fr}}.charts{{grid-template-columns:1fr}}}}
</style></head><body><main>
<div class="eyebrow">Real randomized evidence · corrected Criteo v2.1</div>
<h1>From average lift to an honest targeting policy.</h1>
<p class="lead">A decision-grade causal readout of {summary['n']:,} randomized observations. Assignment, exposure, outcomes and model-based heterogeneity are kept conceptually separate.</p>
<div class="grid">
 <div class="card"><div class="value">{summary['n']/1e6:.2f}M</div><div class="label">randomized observations</div></div>
 <div class="card"><div class="value">{pct(visit['absolute_effect'])}</div><div class="label">visit ITT, absolute</div></div>
 <div class="card"><div class="value">{pct(conversion['absolute_effect'],3)}</div><div class="label">conversion ITT, absolute</div></div>
 <div class="card"><div class="value">{audit['max_absolute_smd']:.3f}</div><div class="label">maximum |SMD|</div></div>
</div>
<div class="decision"><strong>Decision:</strong> assignment has a positive, precisely estimated average effect on visits and conversions. Broad rollout is causally supported subject to treatment economics. Targeting remains conditional: its extra value must survive the untouched holdout and pay for model complexity.</div>
<h2>Trust before lift</h2>
<div class="charts">
 <div class="panel"><img src="../reports/figures/01_itt_effects.png" alt="Intent-to-treat effects"></div>
 <div class="panel"><img src="../reports/figures/02_covariate_balance.png" alt="Covariate balance"></div>
</div>
<h2>Honest heterogeneous-effect evaluation</h2>
<div class="charts">
 <div class="panel"><img src="../reports/figures/03_holdout_uplift_deciles.png" alt="Holdout uplift deciles"></div>
 <div class="panel"><img src="../reports/figures/04_policy_value.png" alt="Policy capacity frontier"></div>
</div>
<div class="grid">
 <div class="card"><div class="value">{diagnostics['evaluation_rows']/1e6:.1f}M</div><div class="label">untouched evaluation rows</div></div>
 <div class="card"><div class="value">{diagnostics['out_of_sample_observed_auc']:.3f}</div><div class="label">observed-outcome AUC</div></div>
 <div class="card"><div class="value">{pct(diagnostics['cross_fitted_dr_ate'])}</div><div class="label">holdout DR visit ATE</div></div>
 <div class="card"><div class="value">{pct(top['ipw_observed_effect'])}</div><div class="label">top-decile holdout IPW effect</div></div>
</div>
<div class="panel warning"><h3>Claim boundary</h3><p>The treatment was randomized; actual ad exposure was not. ITT is therefore the primary causal estimate. The features are anonymised and the source has no cost, customer identity, experiment ID or time, so this report does not invent personas, ROI, retention or production impact.</p></div>
<footer>See <code>CASE_STUDY.md</code> for the full reasoning chain and <code>docs/experiment_platform_design.md</code> for the production system design.</footer>
</main></body></html>"""
    destination = Path(ROOT / "dashboard" / "index.html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    print(f"dashboard={destination}")


if __name__ == "__main__":
    main()
