from dataclasses import dataclass

import numpy as np
from scipy.stats import chi2, norm


@dataclass(frozen=True)
class DifferenceInMeans:
    control_rate: float
    treatment_rate: float
    absolute_effect: float
    relative_effect: float
    standard_error: float
    ci_low: float
    ci_high: float
    p_value: float


def difference_in_proportions(y_t: float, n_t: int, y_c: float, n_c: int) -> DifferenceInMeans:
    if min(n_t, n_c) <= 0:
        raise ValueError("Both experiment arms must contain observations")
    p_t, p_c = y_t / n_t, y_c / n_c
    effect = p_t - p_c
    se = np.sqrt(p_t * (1 - p_t) / n_t + p_c * (1 - p_c) / n_c)
    z = effect / se if se else 0.0
    relative = effect / p_c if p_c else np.nan
    return DifferenceInMeans(
        control_rate=float(p_c),
        treatment_rate=float(p_t),
        absolute_effect=float(effect),
        relative_effect=float(relative),
        standard_error=float(se),
        ci_low=float(effect - 1.96 * se),
        ci_high=float(effect + 1.96 * se),
        p_value=float(2 * norm.sf(abs(z))),
    )


def srm_test(n_t: int, n_c: int, expected_treatment_share: float) -> tuple[float, float]:
    total = n_t + n_c
    expected = np.array([total * expected_treatment_share, total * (1 - expected_treatment_share)])
    observed = np.array([n_t, n_c])
    statistic = float(np.sum((observed - expected) ** 2 / expected))
    return statistic, float(chi2.sf(statistic, df=1))


def standardized_mean_difference(mean_t, sd_t, mean_c, sd_c) -> float:
    pooled = np.sqrt((sd_t**2 + sd_c**2) / 2)
    return float((mean_t - mean_c) / pooled) if pooled else 0.0


def ipw_subgroup_effect(y, treatment, selected, propensity: float) -> tuple[float, float, int]:
    y = np.asarray(y, dtype=float)
    treatment = np.asarray(treatment, dtype=float)
    selected = np.asarray(selected, dtype=bool)
    propensity = np.asarray(propensity, dtype=float)
    if propensity.ndim == 0:
        propensity = np.full_like(y, propensity)
    score = treatment * y / propensity - (1 - treatment) * y / (1 - propensity)
    chosen = score[selected]
    if chosen.size < 2:
        return np.nan, np.nan, int(chosen.size)
    return float(chosen.mean()), float(chosen.std(ddof=1) / np.sqrt(chosen.size)), int(chosen.size)
