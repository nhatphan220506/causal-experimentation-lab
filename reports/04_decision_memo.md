# 04 — Decision memo

**Decision:** keep the uplift policy offline. The causal evidence supports average
benefit, but production promotion is blocked until the adjusted-estimator gap can be
resolved with trial-level assignment metadata and the ranking replicates independently.

## What we know

- Aggregate assignment is healthy at exactly 85/15 and control exposure is zero.
- Pooled ITT is +1.034 pp visits and +0.115 pp conversions.
- Raw holdout visit ITT is +1.016 pp, reconciling with the pooled estimate.
- Cross-fitted adjustment remains positive at +0.722 pp and +0.097 pp, but the
  visit magnitude does not reconcile with raw ITT.
- Top-decile holdout visit uplift is +8.53 pp.
- The bottom predicted decile is negative in prediction (−0.74 pp) but positive in
  observed holdout outcomes (+0.35 pp); the model cannot identify harm.
- Broad treatment produces the largest total visit gain in this source population;
  targeting produces substantially greater gain per treated unit.

## Recommendation by operating constraint

| Situation | Action |
|---|---|
| Treatment is cheap, safe, unconstrained | new staged experiment; do not infer launch from this file alone |
| Capacity is capped near 10% | validate top-decile policy in a new randomized holdout |
| Treatment cost is meaningful | select capacity using lower-bound net value |
| Harm/guardrail data are missing | do not launch until instrumented |
| Estimators do not reconcile or ranking fails replication | do not promote the policy |

## Launch contract for a real system

1. Register unit, eligibility, assignment version, outcome windows, costs and
   guardrails before exposure.
2. Run A/A and validate assignment, exposure, and late-outcome pipelines.
3. Start at 5%, then 25%, 50%, and 100% only while trust and harm gates remain green.
4. Maintain a persistent control if delayed conversion or long-run harm matters.
5. Re-estimate policy value by model version and monitor population drift.
6. Record the final decision, uncertainty, dissent, and reversal conditions.

## Reversal conditions

Negative delayed conversion, customer harm, cost above conservative incremental
value, assignment failure, or non-replication of the targeting frontier reverses
the recommendation.
