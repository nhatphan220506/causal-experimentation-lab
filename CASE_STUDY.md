# Causal Experimentation Lab — full case study

## Executive brief

This project analyses the corrected Criteo Uplift Prediction Dataset v2.1: nearly
14 million observations from real randomized advertising incrementality tests.
It asks a practical decision question:

> Does assignment create incremental outcomes, and if treatment is costly or
> capacity-constrained, can an honest targeting policy improve efficiency?

The answer is nuanced. Assignment increases both visits and conversions under
unadjusted and cross-fitted adjusted estimators. Raw holdout ITT reconciles with the
full sample, but adjusted visit magnitude is materially smaller. A holdout-validated
model finds a high-response top decile but fails to identify a harmed bottom decile.
Those are explicit promotion blockers, not details hidden behind a leaderboard.

## Evidence chain

| Stage | Evidence | Decision use | What it does not prove |
|---|---|---|---|
| Provenance | corrected official v2.1, 13.98M rows | avoid known old-release leakage | the data transport to another product |
| Assignment audit | 85/15, SRM p=0.999, no control exposure | trust aggregate assignment | every hidden trial has identical propensity |
| Balance | max absolute SMD 0.049 | no large marginal imbalance | no nonlinear or trial-mixture imbalance |
| Raw ITT | +1.034 pp visit, +0.115 pp conversion | treatment is beneficial on average | treatment is profitable |
| Holdout reconciliation | raw +1.016 pp visit, adjusted +0.722 pp | direction survives; magnitude does not reconcile | adjustment automatically improves truth |
| Honest uplift | top-decile holdout effect +8.53 pp | candidate for a new capacity test | individual effects are observed |
| Policy frontier | 10% is efficient; 100% has more total gain | choose using constraints | ROI without cost/value inputs |
| Platform design | assignment, exposure, metrics, gates, ramp | production implementation contract | this repo served live users |

## 1. Begin with the estimand

The causal variable is random assignment, not actual exposure. ITT keeps the
experiment intact and answers the deployment-policy question. Observed exposure
occurs after assignment and can be affected by ad delivery, eligibility, and user
opportunity; filtering on it would select a non-random population.

Visit is the fixed primary outcome for policy learning because conversion is very
sparse. Conversion remains the downstream business outcome. No revenue metric is
invented because value and cost are absent.

See [`docs/experiment_charter.md`](docs/experiment_charter.md).

## 2. Audit before outcomes

The file passes count, missingness, logical nesting, assignment-ratio, contamination
and balance checks. A non-obvious issue appears later: physical rows are ordered in
treatment blocks. Naively taking the first N records gives a single-arm sample.
The modelling pipeline therefore uses stable hash partitions plus stratified
reservoir sampling.

This matters because reproducible code can still be reproducibly wrong when it
assumes random file order.

See [`reports/01_data_audit.md`](reports/01_data_audit.md).

## 3. Estimate average impact two ways

The full pooled difference estimates a +1.034-point visit ITT and +0.115-point
conversion ITT. Both are extremely precise. Yet precision is not the same as
robustness: the source combines several tests without trial IDs.

The raw 3-million-row holdout estimate is +1.016 points for visits, consistent with
the pooled result. Cross-fitted outcome adjustment using the known 85/15 assignment
probability produces +0.722 points for visits and +0.097 for conversions. The
diagnostic learned-propensity estimate is +0.728 points, so propensity fitting does
not explain the gap. Because trial IDs and randomization strata are absent, the gap
cannot be resolved from this file and blocks production promotion.

See [`reports/02_average_treatment_effects.md`](reports/02_average_treatment_effects.md).

## 4. Separate prediction from causal ranking

Two outcome models learn potential-response surfaces from 3 million training rows.
Predicted uplift ranks a separate 3 million-row evaluation set. The ranking is not
validated with ordinary AUC; effects are re-estimated inside holdout deciles using
randomized-assignment weights.

The top decile's +8.53-point visit effect is much larger than the population
average. However, the model predicts −0.74 points for the bottom decile while the
holdout observes +0.35 points. It therefore cannot identify negative impact. The
source also has no second time period or experiment ID for external replication.
The ranking is a hypothesis for another randomized test, not a production policy.

See [`reports/03_uplift_and_policy.md`](reports/03_uplift_and_policy.md).

## 5. Make the business trade-off explicit

At 10% capacity, the model estimates about 8,536 incremental visits per 100,000
treated—or 854 per 100,000 eligible. Treating everyone estimates about 1,016 per
100,000 eligible. The targeted policy is far more efficient; broad treatment has
greater total impact.

No unique optimum exists until the owner supplies treatment cost, visit/conversion
value, capacity and harm thresholds. The project provides the frontier and the
break-even equation rather than fabricating ROI.

See [`reports/04_decision_memo.md`](reports/04_decision_memo.md).

## 6. Translate analysis into a production contract

The platform design covers experiment registration, deterministic assignment,
exposure semantics, metric versioning, SRM and data-quality gates, sequential
decision rules, staged ramps, rollback and persistent holdouts. Components that
cannot be demonstrated from this offline source remain specifications rather than
synthetic claims of production ownership.

See [`docs/experiment_platform_design.md`](docs/experiment_platform_design.md).

## Final recommendation

The evidence supports average treatment benefit, but not a production launch from
this pooled file. Run a new staged experiment with known strata, cost, delayed
conversion and harm metrics. If capacity binds, preregister the top-decile policy as
a challenger and retain randomized control. Require estimator reconciliation and a
second-period replication before treating the uplift ranking as durable.

## Honest limitations

Advertising context, anonymised features, absent trial/user/time identifiers,
unknown cost/value, sparse conversion and model dependence limit transport and
product interpretation. Full claim boundaries are documented in
[`docs/limitations.md`](docs/limitations.md).
