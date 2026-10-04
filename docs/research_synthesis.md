# Research synthesis

This file records how external methodological guidance changed the analysis,
rather than serving as a list of links.

## Dataset provenance and correction

Criteo describes the source as several incrementality tests in which a random
control population was prevented from receiving advertising. The corrected v2
release contains roughly 13.98 million rows, 12 anonymised features, assignment,
exposure, visit, and conversion labels. The original release contained leakage
from an advertiser treatment policy; this project uses only v2.1.

- Criteo AI Lab dataset card: https://ailab.criteo.com/criteo-uplift-prediction-dataset/
- Dataset benchmark paper: https://arxiv.org/abs/2111.10106

**Project consequence:** version and provenance are part of the data contract.
No analysis uses the superseded release.

## Assignment, exposure, and estimands

Random assignment identifies an intention-to-treat effect. Actual exposure is a
post-assignment variable affected by delivery and eligibility; filtering to
exposed rows destroys the original exchangeability. Instrumental-variable scaling
can be informative, but only under stronger assumptions than randomization alone.

- Hernán & Robins, *Causal Inference: What If*: https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/
- CONSORT treatment estimand discussion: https://www.consort-statement.org/

**Project consequence:** ITT is the headline result; exposed/unexposed comparisons
are explicitly rejected as causal. The Wald ratio is labelled sensitivity analysis.

## Balance and sample-ratio mismatch

Randomization justifies inference by design, while covariate balance checks can
surface implementation failures. Balance is not established by a series of
p-values whose magnitude scales with sample size. Standardised differences show
practical imbalance on a common scale. Assignment counts are also compared with
the intended allocation separately from outcome analysis.

- Microsoft ExP SRM guidance: https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/
- Austin on standardised differences: https://doi.org/10.1002/sim.3697

**Project consequence:** the audit reports one SRM diagnostic and 12 standardised
differences. A large sample is not allowed to turn a negligible feature difference
into a dramatic causal story.

## Heterogeneous treatment effects

Because individual treatment effects are never observed, flexible uplift models
are especially vulnerable to overfitting. Model fit for the observed outcome is
not proof of treatment-effect ranking. Evaluation must occur on untouched
randomized observations using transformed outcomes, uplift/Qini-style ranking,
or policy-value estimators.

- Athey & Imbens on recursive partitioning for heterogeneous causal effects:
  https://doi.org/10.1073/pnas.1510489113
- Gutierrez & Gérardy on causal inference and uplift modelling:
  https://proceedings.mlr.press/v67/gutierrez17a.html

**Project consequence:** nuisance models train on one block and all heterogeneity
claims use a disjoint holdout. The report keeps uncertainty visible by decile and
does not assign narrative labels to anonymised features.

## Decision value, not model theatre

A targeting model matters only if it improves a policy under a real constraint.
The relevant output is incremental outcome per population treated, not merely
classification AUC. Without treatment cost, this project presents a policy frontier
rather than fabricating an ROI optimum.

- Venkatasubramaniam et al. on policy learning and evaluation:
  https://doi.org/10.48550/arXiv.2304.10584

**Project consequence:** the analysis estimates holdout policy value at ten
capacity levels and leaves the break-even cost as an explicit decision input.

## External validity

Randomization protects internal validity for the trials represented in the file;
it does not guarantee that the effect transports to another advertiser, product,
channel, or period. The absence of trial identifiers also prevents leave-one-trial-
out validation and experiment-level meta-analysis.

**Project consequence:** conclusions are phrased as effects in the observed study
population, not universal truths about advertising or product engagement.

