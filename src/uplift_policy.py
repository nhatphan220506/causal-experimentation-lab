import argparse

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, roc_auc_score

from src.config import (
    FEATURES,
    GENERATED_DIR,
    RANDOM_SEED,
    ensure_output_dirs,
)
from src.io_utils import connection, relation_sql, write_json
from src.statistics import ipw_subgroup_effect


def load_split(limit: int, split: int) -> pd.DataFrame:
    conn = connection()
    columns = ", ".join(FEATURES + ["treatment", "visit", "conversion"])
    n_treatment = int(limit * 0.85)
    n_control = limit - n_treatment
    # The source is ordered in treatment blocks. A row-position LIMIT would create
    # a single-arm training set, so deterministic hash partitions are mandatory.
    return conn.execute(
        f"""
        SELECT * FROM (
            SELECT {columns} FROM {relation_sql()}
            WHERE treatment = 1 AND hash(row_id) % 2 = {int(split)}
        ) USING SAMPLE reservoir({n_treatment} ROWS) REPEATABLE({RANDOM_SEED + split})
        UNION ALL
        SELECT * FROM (
            SELECT {columns} FROM {relation_sql()}
            WHERE treatment = 0 AND hash(row_id) % 2 = {int(split)}
        ) USING SAMPLE reservoir({n_control} ROWS) REPEATABLE({RANDOM_SEED + 10 + split})
        """
    ).fetch_df()


def fit_t_learner(train: pd.DataFrame, outcome: str):
    models = {}
    for arm in (0, 1):
        subset = train[train.treatment == arm]
        model = HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=120,
            max_leaf_nodes=24,
            min_samples_leaf=250,
            l2_regularization=1.0,
            random_state=RANDOM_SEED + arm,
        )
        model.fit(subset[FEATURES], subset[outcome])
        models[arm] = model
    return models


def fit_propensity_model(train: pd.DataFrame):
    model = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=100,
        max_leaf_nodes=24,
        min_samples_leaf=500,
        l2_regularization=2.0,
        random_state=RANDOM_SEED + 99,
    )
    model.fit(train[FEATURES], train["treatment"])
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-rows", type=int, default=3_000_000)
    parser.add_argument("--eval-rows", type=int, default=3_000_000)
    args = parser.parse_args()
    ensure_output_dirs()
    train = load_split(args.train_rows, 0)
    evaluate = load_split(args.eval_rows, 1)
    models = fit_t_learner(train, "visit")
    conversion_models = fit_t_learner(train, "conversion")
    propensity_model = fit_propensity_model(train)

    p0 = models[0].predict_proba(evaluate[FEATURES])[:, 1]
    p1 = models[1].predict_proba(evaluate[FEATURES])[:, 1]
    uplift = p1 - p0
    observed = np.where(evaluate.treatment.to_numpy() == 1, p1, p0)
    outcome = evaluate.visit.to_numpy()
    conversion = evaluate.conversion.to_numpy()
    treatment = evaluate.treatment.to_numpy()
    marginal_propensity = float(treatment.mean())
    propensity = np.clip(
        propensity_model.predict_proba(evaluate[FEATURES])[:, 1], 0.02, 0.98
    )

    evaluate = evaluate.assign(predicted_uplift=uplift)
    evaluate["uplift_decile"] = pd.qcut(
        evaluate.predicted_uplift.rank(method="first"), 10, labels=False
    )
    deciles = []
    for decile in range(9, -1, -1):
        subset = evaluate.uplift_decile.to_numpy() == decile
        effect, se, n = ipw_subgroup_effect(
            outcome, treatment, subset, propensity
        )
        deciles.append(
            {
                "decile": int(decile + 1),
                "n": n,
                "mean_predicted_uplift": float(uplift[subset].mean()),
                "ipw_observed_effect": effect,
                "standard_error": se,
            }
        )

    ranking = np.argsort(-uplift)
    policy_curve = []
    for fraction in np.linspace(0.1, 1.0, 10):
        selected = np.zeros(len(evaluate), dtype=bool)
        selected[ranking[: int(len(evaluate) * fraction)]] = True
        effect, se, n = ipw_subgroup_effect(
            outcome, treatment, selected, propensity
        )
        policy_curve.append(
            {
                "target_fraction": float(fraction),
                "subgroup_ate": effect,
                "standard_error": se,
                "n": n,
                "incremental_visits_per_100k_targeted": effect * 100_000,
                "incremental_visits_per_100k_eligible": effect * fraction * 100_000,
            }
        )

    dr_score = (
        p1
        - p0
        + treatment * (outcome - p1) / propensity
        - (1 - treatment) * (outcome - p0) / (1 - propensity)
    )
    c0 = conversion_models[0].predict_proba(evaluate[FEATURES])[:, 1]
    c1 = conversion_models[1].predict_proba(evaluate[FEATURES])[:, 1]
    conversion_dr_score = (
        c1
        - c0
        + treatment * (conversion - c1) / propensity
        - (1 - treatment) * (conversion - c0) / (1 - propensity)
    )
    diagnostics = {
        "train_rows": len(train),
        "evaluation_rows": len(evaluate),
        "evaluation_marginal_propensity": marginal_propensity,
        "propensity_auc": float(roc_auc_score(treatment, propensity)),
        "propensity_p01": float(np.quantile(propensity, 0.01)),
        "propensity_p99": float(np.quantile(propensity, 0.99)),
        "out_of_sample_observed_auc": float(roc_auc_score(outcome, observed)),
        "out_of_sample_observed_log_loss": float(log_loss(outcome, observed)),
        "cross_fitted_dr_ate": float(dr_score.mean()),
        "cross_fitted_dr_standard_error": float(dr_score.std(ddof=1) / np.sqrt(len(dr_score))),
        "cross_fitted_conversion_dr_ate": float(conversion_dr_score.mean()),
        "cross_fitted_conversion_dr_standard_error": float(
            conversion_dr_score.std(ddof=1) / np.sqrt(len(conversion_dr_score))
        ),
        "uplift_correlation_with_ipw_score": float(
            np.corrcoef(
                uplift,
                treatment * outcome / propensity
                - (1 - treatment) * outcome / (1 - propensity),
            )[0, 1]
        ),
        "warning": (
            "Individual uplift is not directly observed. Ranking is evaluated only on the untouched "
            "holdout with randomized-treatment IPW estimates; decile noise must remain visible."
        ),
    }
    write_json(
        {"diagnostics": diagnostics, "deciles": deciles, "policy_curve": policy_curve},
        GENERATED_DIR / "uplift_policy_results.json",
    )
    pd.DataFrame(deciles).to_csv(GENERATED_DIR / "uplift_deciles.csv", index=False)
    pd.DataFrame(policy_curve).to_csv(GENERATED_DIR / "policy_curve.csv", index=False)
    print(f"holdout_auc={diagnostics['out_of_sample_observed_auc']:.4f}")
    print(f"top_decile_effect={deciles[0]['ipw_observed_effect']:.6%}")


if __name__ == "__main__":
    main()
