import json
import os

os.environ.setdefault("MPLCONFIGDIR", ".cache/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES_DIR, GENERATED_DIR, ensure_output_dirs

COLORS = {"ink": "#172554", "blue": "#2563EB", "teal": "#0F766E", "coral": "#EA580C"}


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()


def main() -> None:
    ensure_output_dirs()
    audit = json.loads((GENERATED_DIR / "data_audit.json").read_text())
    ate = json.loads((GENERATED_DIR / "ate_results.json").read_text())
    uplift = json.loads((GENERATED_DIR / "uplift_policy_results.json").read_text())

    labels = ["Visit", "Conversion"]
    effects = [ate["visit"]["absolute_effect"] * 100, ate["conversion"]["absolute_effect"] * 100]
    lows = [ate["visit"]["ci_low"] * 100, ate["conversion"]["ci_low"] * 100]
    highs = [ate["visit"]["ci_high"] * 100, ate["conversion"]["ci_high"] * 100]
    plt.figure(figsize=(8, 4.6))
    plt.errorbar(effects, labels, xerr=[np.array(effects) - lows, np.array(highs) - effects],
                 fmt="o", color=COLORS["blue"], capsize=5, markersize=8)
    plt.axvline(0, color="#94A3B8", linewidth=1)
    plt.xlabel("Intent-to-treat effect (percentage points)")
    plt.title("Randomized assignment increases both outcomes")
    save("01_itt_effects.png")

    balance = pd.DataFrame(audit["covariate_balance"])
    plt.figure(figsize=(8, 5))
    plt.barh(balance.feature, balance.smd, color=COLORS["teal"])
    plt.axvline(-0.1, color="#CBD5E1", linestyle="--")
    plt.axvline(0.1, color="#CBD5E1", linestyle="--")
    plt.xlabel("Standardized mean difference: treatment − control")
    plt.title("Pre-treatment features are balanced across assignment arms")
    save("02_covariate_balance.png")

    deciles = pd.DataFrame(uplift["deciles"])
    plt.figure(figsize=(9, 5))
    plt.errorbar(
        range(1, 11), deciles.ipw_observed_effect * 100,
        yerr=1.96 * deciles.standard_error * 100,
        fmt="o-", color=COLORS["coral"], capsize=3,
    )
    plt.axhline(0, color="#94A3B8", linewidth=1)
    plt.xticks(range(1, 11), ["Top"] + [str(i) for i in range(2, 10)] + ["Bottom"])
    plt.ylabel("Holdout IPW effect (percentage points)")
    plt.xlabel("Predicted-uplift decile")
    plt.title("Heterogeneity claims are checked on an untouched randomized holdout")
    save("03_holdout_uplift_deciles.png")

    policy = pd.DataFrame(uplift["policy_curve"])
    _, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    axes[0].plot(
        policy.target_fraction * 100,
        policy.incremental_visits_per_100k_targeted,
        marker="o",
        color=COLORS["blue"],
    )
    axes[0].set_xlabel("Population targeted (%)")
    axes[0].set_ylabel("Visits per 100k treated")
    axes[0].set_title("Efficiency falls with reach")
    axes[1].plot(
        policy.target_fraction * 100,
        policy.incremental_visits_per_100k_eligible,
        marker="o",
        color=COLORS["teal"],
    )
    axes[1].set_xlabel("Population targeted (%)")
    axes[1].set_ylabel("Visits per 100k eligible")
    axes[1].set_title("Total impact rises with reach")
    plt.suptitle("Targeting is a cost/capacity decision, not a model leaderboard")
    save("04_policy_value.png")


if __name__ == "__main__":
    main()
