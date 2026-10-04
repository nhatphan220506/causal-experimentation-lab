# Production experimentation platform design

The public dataset supports an offline causal study. This design document explains
what would be required to make the same decision safely in production.

## Control plane

```text
Experiment registry
  ├── hypothesis, owner, decision deadline
  ├── unit, eligibility, namespaces, exclusions
  ├── allocation, stratification, ramp schedule
  ├── primary/secondary/guardrail metric versions
  └── pre-specified decision and rollback rules
             ↓
Deterministic assignment service
             ↓
Treatment delivery and exposure logging
```

Assignment must be deterministic from a stable unit key, experiment ID, salt, and
version. Mutually exclusive namespaces prevent incompatible treatments. Allocation
changes create new versions rather than rewriting history.

## Data plane

Minimum event contracts:

| Event | Required fields | Purpose |
|---|---|---|
| assignment | unit, experiment, variant, version, timestamp | ITT denominator |
| exposure | assignment ID, treatment rendered, timestamp | delivery diagnosis |
| outcome | unit, metric event, value, timestamp | decision metrics |
| quality | client/server version, error, latency | guardrails |

The metric layer must freeze window, attribution, deduplication, late-arrival,
timezone, bot, refund, and identity rules. Metric definitions are versioned code,
not editable dashboard labels.

## Automated trust gates

1. Pre-launch A/A test and event-contract validation.
2. SRM alert by assignment version and major platform slice.
3. Assignment/exposure crossover and missing-event monitoring.
4. Pre-treatment balance used diagnostically, never to hunt for a favourable sample.
5. Novelty, weekday, and delayed-outcome maturity checks.
6. Guardrail alerts evaluated under an explicit multiple-testing policy.

No outcome claim is released while a critical trust gate is red.

## Sequential decision policy

Repeatedly checking a fixed-horizon p-value inflates false positives. The registry
therefore requires either:

- a fixed sample/runtime with only operational monitoring; or
- a preconfigured group-sequential/always-valid procedure with spending boundaries.

Stopping for harm is separate from stopping for benefit and is owned by a named
product/engineering decision maker.

## Rollout after the test

- 5% → 25% → 50% → 100% ramp with automated rollback on delivery or guardrail harm.
- Persistent holdout when long-term effects, learning, or cannibalisation matter.
- Model and policy monitoring for population drift, calibration, treatment cost,
  and realised incremental outcomes.
- A post-decision record containing the chosen action, dissent, uncertainty, and
  what observation would reverse the decision.

## What this repo implements versus specifies

Implemented: offline data audit, ITT, IV sensitivity, honest holdout uplift
evaluation, capacity frontier, tests, and reproducible reporting.

Specified but not falsely simulated: live identity resolution, assignment service,
streaming telemetry, late conversions, refunds, sequential monitoring, ramp and
rollback, stakeholder approval, and incident response.

