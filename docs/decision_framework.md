# Decision framework

## Required inputs from the business owner

- Value of an incremental visit and conversion.
- Variable treatment cost per assigned and exposed unit.
- Maximum treatment capacity.
- Acceptable harm threshold for customer experience and brand outcomes.
- Operational cost of maintaining a targeting model.

## Break-even logic

For a population segment `S`, treatment is economically attractive when:

```text
visit_ITT(S) × value_per_visit
+ conversion_ITT(S) × incremental_value_per_conversion
> cost_per_assignment(S) + expected_harm_cost(S)
```

Because those monetary inputs are absent, the repo reports incremental outcomes
per 100,000 assignments at multiple capacity levels. It does not manufacture a
currency impact.

## Recommended decision sequence

1. Reject the readout if assignment, schema, or contamination checks fail.
2. Use ITT for the broad deployment decision.
3. Use conversion to check whether visit lift translates downstream.
4. Compare broad and targeted policy value on the untouched holdout.
5. Target only if the incremental benefit pays for complexity and is stable.
6. Ramp gradually and retain a holdout when long-run effects matter.

## What would reverse a recommendation

- A corrected assignment ratio showing implementation failure.
- Negative delayed conversion, cancellation, or customer-harm outcomes.
- A treatment cost above the lower confidence bound of economic value.
- Failure of uplift ranking in a second trial or later time period.
- Material delivery drift between offline evaluation and launch.

