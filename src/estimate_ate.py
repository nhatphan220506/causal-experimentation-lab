from dataclasses import asdict

from scipy.stats import norm

from src.config import GENERATED_DIR, ensure_output_dirs
from src.io_utils import connection, relation_sql, write_json
from src.statistics import difference_in_proportions


def main() -> None:
    ensure_output_dirs()
    conn = connection()
    rel = relation_sql()
    rows = conn.execute(
        f"""
        SELECT treatment, count(*) n, sum(visit) visits, sum(conversion) conversions,
               sum(exposure) exposures
        FROM {rel}
        GROUP BY treatment ORDER BY treatment
        """
    ).fetchall()
    control, treatment = rows
    results = {}
    for outcome, index in (("visit", 2), ("conversion", 3)):
        estimate = difference_in_proportions(treatment[index], treatment[1], control[index], control[1])
        results[outcome] = asdict(estimate)
        baseline = results[outcome]["control_rate"]
        mde_80 = (norm.ppf(0.975) + norm.ppf(0.80)) * (
            baseline * (1 - baseline) * (1 / treatment[1] + 1 / control[1])
        ) ** 0.5
        results[outcome]["mde_80_power_absolute"] = float(mde_80)
        results[outcome]["incremental_outcomes_per_100k_assigned"] = float(
            estimate.absolute_effect * 100_000
        )
        results[outcome]["number_needed_to_assign"] = float(1 / estimate.absolute_effect)

    exposure_first_stage = treatment[4] / treatment[1] - control[4] / control[1]
    results["exposure_first_stage"] = exposure_first_stage
    results["iv_complier_effect"] = {
        outcome: results[outcome]["absolute_effect"] / exposure_first_stage
        for outcome in ("visit", "conversion")
    }
    results["interpretation"] = {
        "itt": "Primary causal estimate: effect of assignment, preserving randomization.",
        "iv": "Wald scaling is descriptive and requires exclusion, monotonicity, and instrument relevance assumptions.",
        "per_protocol": "Not reported as causal because observed exposure is post-treatment selection.",
    }
    write_json(results, GENERATED_DIR / "ate_results.json")
    for outcome in ("visit", "conversion"):
        result = results[outcome]
        print(
            f"{outcome}: {result['absolute_effect']:.6%} "
            f"({result['ci_low']:.6%}, {result['ci_high']:.6%})"
        )


if __name__ == "__main__":
    main()
