# 04 — Decision memo

**Decision:** proceed only after inserting real treatment cost and outcome value.
The causal evidence supports benefit; it does not by itself choose broad versus
targeted deployment.

## What we know

- Aggregate assignment is healthy at exactly 85/15 and control exposure is zero.
- Pooled ITT is +1.034 pp visits and +0.115 pp conversions.
- Cross-fitted adjustment remains positive at +0.728 pp and +0.096 pp.
- Top-decile holdout visit uplift is +5.79 pp.
- Broad treatment produces the largest total visit gain in this source population;
  targeting produces substantially greater gain per treated unit.

## Recommendation by operating constraint

| Situation | Action |
|---|---|
| Treatment is cheap, safe, unconstrained | staged broad rollout |
| Capacity is capped near 10% | deploy top-decile policy with persistent holdout |
| Treatment cost is meaningful | select capacity using lower-bound net value |
| Harm/guardrail data are missing | do not launch until instrumented |
| Ranking fails independent replication | fall back to broad treatment or stop |

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

