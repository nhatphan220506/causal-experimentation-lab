import math

from src.config import EXPECTED_TREATMENT_SHARE, FEATURES, GENERATED_DIR, ensure_output_dirs
from src.io_utils import connection, relation_sql, write_json
from src.statistics import srm_test, standardized_mean_difference


def safe(value):
    return None if isinstance(value, float) and (math.isnan(value) or math.isinf(value)) else value


def main() -> None:
    ensure_output_dirs()
    conn = connection()
    rel = relation_sql()
    overall = conn.execute(
        f"""
        SELECT count(*) n,
               sum(treatment) n_treatment,
               count(*) - sum(treatment) n_control,
               avg(treatment) treatment_share,
               avg(visit) visit_rate,
               avg(conversion) conversion_rate,
               avg(exposure) exposure_rate,
               sum(CASE WHEN treatment = 0 AND exposure = 1 THEN 1 ELSE 0 END) control_exposed,
               sum(CASE WHEN conversion = 1 AND visit = 0 THEN 1 ELSE 0 END) conversion_without_visit
        FROM {rel}
        """
    ).fetchone()
    cols = [item[0] for item in conn.description]
    summary = dict(zip(cols, overall))
    n_t, n_c = int(summary["n_treatment"]), int(summary["n_control"])
    srm_stat, srm_p = srm_test(n_t, n_c, EXPECTED_TREATMENT_SHARE)

    aggregate_fields = []
    for feature in FEATURES:
        for arm, label in ((0, "c"), (1, "t")):
            aggregate_fields.extend(
                [
                    f"avg({feature}) FILTER (WHERE treatment={arm}) AS {feature}_{label}_mean",
                    f"stddev_samp({feature}) FILTER (WHERE treatment={arm}) AS {feature}_{label}_sd",
                    f"count(*) FILTER (WHERE treatment={arm} AND {feature} IS NULL) AS {feature}_{label}_missing",
                ]
            )
    values = conn.execute(f"SELECT {', '.join(aggregate_fields)} FROM {rel}").fetchone()
    names = [item[0] for item in conn.description]
    aggregates = dict(zip(names, values))

    balance = []
    for feature in FEATURES:
        smd = standardized_mean_difference(
            aggregates[f"{feature}_t_mean"],
            aggregates[f"{feature}_t_sd"],
            aggregates[f"{feature}_c_mean"],
            aggregates[f"{feature}_c_sd"],
        )
        balance.append(
            {
                "feature": feature,
                "control_mean": safe(aggregates[f"{feature}_c_mean"]),
                "treatment_mean": safe(aggregates[f"{feature}_t_mean"]),
                "smd": smd,
                "control_missing": int(aggregates[f"{feature}_c_missing"]),
                "treatment_missing": int(aggregates[f"{feature}_t_missing"]),
            }
        )

    payload = {
        "source": "Criteo Uplift Prediction Dataset v2.1 (corrected)",
        "summary": {key: safe(value) for key, value in summary.items()},
        "srm": {
            "expected_treatment_share": EXPECTED_TREATMENT_SHARE,
            "chi_square": srm_stat,
            "p_value": srm_p,
            "note": "The published assignment ratio is approximate; inspect practical deviation with p-value.",
        },
        "covariate_balance": balance,
        "max_absolute_smd": max(abs(item["smd"]) for item in balance),
    }
    write_json(payload, GENERATED_DIR / "data_audit.json")
    print(f"rows={summary['n']:,}; treatment_share={summary['treatment_share']:.6f}")
    print(f"max_abs_smd={payload['max_absolute_smd']:.6f}; srm_p={srm_p:.6g}")


if __name__ == "__main__":
    main()
