import numpy as np
import pytest

from src.statistics import (
    augmented_ipw_score,
    difference_in_proportions,
    ipw_subgroup_effect,
    srm_test,
    standardized_mean_difference,
)


def test_difference_in_proportions_direction_and_interval():
    result = difference_in_proportions(550, 10_000, 500, 10_000)
    assert result.absolute_effect == pytest.approx(0.005)
    assert result.ci_low < result.absolute_effect < result.ci_high
    assert result.relative_effect == pytest.approx(0.1)


def test_srm_flags_large_assignment_failure():
    _, healthy_p = srm_test(8_500, 1_500, 0.85)
    _, broken_p = srm_test(9_000, 1_000, 0.85)
    assert healthy_p == pytest.approx(1.0)
    assert broken_p < 1e-10


def test_standardized_difference_is_scale_free():
    assert standardized_mean_difference(11, 2, 10, 2) == 0.5


def test_ipw_recovers_randomized_effect():
    rng = np.random.default_rng(42)
    n = 300_000
    p = 0.85
    treatment = rng.binomial(1, p, n)
    baseline = rng.binomial(1, 0.10, n)
    treated = rng.binomial(1, 0.13, n)
    outcome = np.where(treatment == 1, treated, baseline)
    effect, se, used = ipw_subgroup_effect(outcome, treatment, np.ones(n, dtype=bool), p)
    assert used == n
    assert abs(effect - 0.03) < 4 * se


def test_aipw_recovers_randomized_effect_with_misspecified_outcome_models():
    rng = np.random.default_rng(7)
    n = 400_000
    propensity = 0.85
    treatment = rng.binomial(1, propensity, n)
    potential_control = rng.binomial(1, 0.08, n)
    potential_treated = rng.binomial(1, 0.11, n)
    outcome = np.where(treatment == 1, potential_treated, potential_control)
    # Deliberately poor nuisance models: known randomization should still protect
    # the AIPW estimate in expectation.
    score = augmented_ipw_score(
        outcome,
        treatment,
        np.full(n, 0.05),
        np.full(n, 0.14),
        propensity,
    )
    standard_error = score.std(ddof=1) / np.sqrt(n)
    assert abs(score.mean() - 0.03) < 4 * standard_error


def test_aipw_rejects_invalid_propensity():
    with pytest.raises(ValueError, match="strictly between"):
        augmented_ipw_score([0, 1], [0, 1], [0.1, 0.1], [0.2, 0.2], 1.0)
