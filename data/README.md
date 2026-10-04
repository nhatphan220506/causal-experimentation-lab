# Data contract

The raw file is the corrected **Criteo Uplift Prediction Dataset v2.1**. It is not
committed to Git. Run `python -m src.download_data` to retrieve the official
311,422,618-byte gzip file.

## Schema

| Field | Role | Interpretation |
|---|---|---|
| `f0`–`f11` | pre-treatment covariates | anonymised continuous features |
| `treatment` | random assignment | eligibility for advertising treatment |
| `exposure` | post-assignment event | whether the ad was actually served |
| `visit` | outcome | site visit after assignment |
| `conversion` | outcome | downstream conversion after assignment |

The unit is an anonymised experimental observation. There is no timestamp,
user identifier, spend, margin, campaign, geography, device label, or treatment
cost. Consequently this project does not invent retention, sequential testing,
revenue, or cluster-robust analyses that the source cannot support.

## Causal ordering

```text
pre-treatment features → random assignment → observed exposure → outcomes
```

Assignment is the valid randomized instrument. Exposure is post-treatment and
therefore must not be conditioned on as though it were randomized.

