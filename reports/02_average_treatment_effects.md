# 02 — Average treatment effects

## Unadjusted pooled ITT

| Outcome | Control | Treatment | Absolute ITT | 95% CI | Relative lift | Per 100k assigned |
|---|---:|---:|---:|---:|---:|---:|
| Visit | 3.8201% | 4.8543% | +1.0342 pp | +1.0056 to +1.0629 pp | +27.07% | +1,034 |
| Conversion | 0.1938% | 0.3089% | +0.1152 pp | +0.1085 to +0.1219 pp | +59.45% | +115 |

![Intent-to-treat effects](figures/01_itt_effects.png)

The achieved 80%-power MDE is approximately 0.0402 percentage points for visit
and 0.0092 points for conversion under a two-sided 5% test. The study is therefore
precise enough to detect effects far smaller than the observed estimates.

## Covariate-adjusted holdout sensitivity

Separate outcome models are trained on 3 million observations. A propensity model
and doubly robust score are then evaluated on a disjoint 3 million-row holdout.

| Outcome | Cross-fitted DR effect | Approx. 95% CI |
|---|---:|---:|
| Visit | +0.7282 pp | +0.6741 to +0.7822 pp |
| Conversion | +0.0956 pp | +0.0812 to +0.1101 pp |

The propensity model has AUC 0.510, with predicted assignment probability from
0.844 at p01 to 0.896 at p99. Assignment is only weakly predictable, but adjustment
reduces both estimates. The defensible conclusion is not one preferred decimal;
it is that the effect remains positive and decision-relevant under two estimators.

## Assignment versus exposure

Only 3.604% of assigned treatment observations are marked exposed, versus zero in
control. Dividing ITT by this first stage yields Wald estimates of +28.7 pp for
visit and +3.20 pp for conversion among hypothetical compliers.

Those large values are **not** the headline result. They require exclusion,
monotonicity, correct exposure measurement, and a meaningful complier population.
The source does not let us validate those assumptions. A direct exposed/unexposed
comparison is omitted because exposure is post-treatment selection.

## Decision interpretation

- Direction is robust: assignment increases both visit and conversion.
- Magnitude uncertainty from pooled-trial adjustment is more important than the
  tiny sampling error around the raw difference.
- Economic viability still requires treatment cost and outcome value.
- Statistical certainty does not establish transport to a new company or channel.

