# Experiment charter and estimand contract

## Decision

Should treatment be deployed broadly, targeted to a constrained share of the
population, or withheld pending a better experiment?

The public data do not contain treatment cost or customer harm metrics. The
analysis can estimate incremental visits and conversions, but the final business
policy remains conditional on a break-even value supplied by the decision owner.

## Primary estimands

1. **Visit ITT:** average effect of treatment assignment on the probability of a
   visit. This is the primary outcome because it is less sparse and was fixed
   before heterogeneous-effect modelling.
2. **Conversion ITT:** average effect of assignment on conversion. This is the
   downstream business outcome.
3. **Policy value:** out-of-sample visit ITT inside populations selected by a
   pre-treatment uplift score.

For binary outcome `Y`, assignment `Z`, and propensity `p`:

```text
ATE = E[Y | Z=1] − E[Y | Z=0]
IPW score = ZY/p − (1−Z)Y/(1−p)
Policy value(S) = mean(IPW score | S(X)=1)
```

## Secondary estimand

The Wald ratio `ITT / (E[exposure|Z=1] − E[exposure|Z=0])` is reported only as an
instrumental-variable sensitivity estimate. Interpreting it as a complier effect
requires relevance, exclusion, monotonicity, and random assignment assumptions.
Only relevance and assignment can be partially checked here.

## Explicit non-estimands

- Comparing exposed and unexposed observations is not a causal effect.
- A model prediction for one row is not an observed individual treatment effect.
- The top uplift decile is not a stable customer persona: features are anonymised.
- Revenue lift and ROI cannot be estimated without value and treatment-cost fields.

## Trust checks before outcomes

- File and schema integrity.
- Assignment share versus the published approximate 85/15 design.
- Control contamination in the exposure field.
- Missingness and logical ordering of visit/conversion.
- Standardised differences for all 12 pre-treatment features.
- No train/evaluation overlap for uplift analysis.

## Decision thresholds

Broad rollout is supportable when assignment is trustworthy and both:

- visit ITT is positive with a 95% interval excluding zero;
- conversion ITT is non-negative and economically viable under the owner's
  cost/value assumptions.

Targeting is preferred only if its untouched holdout policy value materially
exceeds broad treatment after considering model maintenance and capacity cost.

