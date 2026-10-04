# Limitations and claim boundaries

1. **Advertising context:** this is an incrementality dataset, not an in-product
   checkout experiment. The causal methods transfer more readily than the effect.
2. **Anonymised features:** useful for method evaluation, weak for customer-facing
   product narratives or actionable persona names.
3. **No experiment identifier:** the file combines several tests but does not expose
   trial membership. Experiment-level heterogeneity and leave-one-trial-out
   transport checks are unavailable.
4. **No time:** novelty, seasonality, delayed outcomes, stopping behaviour, and
   interference over time cannot be tested.
5. **No unit identifier:** repeat observations and clustered dependence cannot be
   independently audited.
6. **No cost or value:** policy curves are outcome frontiers, not profit forecasts.
7. **Sparse conversion:** conversion heterogeneity would require stronger
   regularisation and independent replication; visit is used for ranking.
8. **Model dependence:** T-learner rankings can be unstable. Honest holdout
   evaluation limits but does not remove model-selection risk.
9. **Approximate propensity:** the published treatment ratio is approximately 85%.
   Exact experiment-specific propensities are not provided.
10. **No production ownership claim:** the platform document shows system thinking;
    it is not evidence that this repository served live users.

