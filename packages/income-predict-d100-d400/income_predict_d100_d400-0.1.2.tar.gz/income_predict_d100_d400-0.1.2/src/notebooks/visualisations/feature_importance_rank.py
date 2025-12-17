import matplotlib.pyplot as plt
import numpy as np

# GLM feature ranks (1 = most important)
GLM_RANKS = {
    "cat__relationship_Own-child": 1,
    "num__capital_net": 2,
    "cat__relationship_Unmarried": 3,
    "cat__relationship_Not-in-family": 4,
    "cat__relationship_Married": 5,
    "cat__occupation_Farming-fishing": 6,
    "cat__occupation_Other-service": 7,
    "cat__work_class_Self-emp-not-inc": 8,
    "cat__relationship_Other-relative": 9,
    "num__education": 10,
    "cat__occupation_Handlers-cleaners": 11,
    "cat__work_class_State-gov": 12,
    "cat__occupation_None": 13,
    "cat__work_class_None": 14,
    "cat__native_country_Mexico": 15,
    "cat__work_class_Private": 16,
    "cat__work_class_Local-gov": 17,
    "cat__occupation_Exec-managerial": 18,
    "cat__occupation_Machine-op-inspct": 19,
    "cat__native_country_United-States": 20,
    "num__age": 21,
    "cat__native_country_None": 22,
    "cat__occupation_Transport-moving": 23,
    "num__hours_per_week": 24,
    "cat__native_country_Columbia": 25,
    "cat__occupation_Prof-specialty": 26,
    "cat__native_country_South": 27,
    "cat__occupation_Priv-house-serv": 28,
    "cat__occupation_Adm-clerical": 29,
    "cat__work_class_Self-emp-inc": 30,
    "cat__occupation_Tech-support": 31,
    "cat__native_country_Puerto-Rico": 32,
    "cat__native_country_Vietnam": 33,
    "cat__occupation_Craft-repair": 34,
    "cat__native_country_China": 35,
    "cat__native_country_Dominican-Republic": 36,
    "cat__native_country_Poland": 37,
    "cat__native_country_India": 38,
    "cat__native_country_Germany": 39,
    "cat__native_country_El-Salvador": 40,
    "cat__native_country_Peru": 41,
    "cat__work_class_Federal-gov": 42,
    "cat__native_country_Greece": 43,
    "cat__native_country_Nicaragua": 44,
    "cat__native_country_Philippines": 45,
    "cat__native_country_Cuba": 46,
    "cat__native_country_Scotland": 47,
    "cat__native_country_Laos": 48,
    "cat__native_country_Ecuador": 49,
    "cat__occupation_Protective-serv": 50,
    "cat__native_country_Guatemala": 51,
    "cat__work_class_Without-pay": 52,
    "cat__native_country_Trinadad&Tobago": 53,
    "cat__native_country_Jamaica": 54,
    "cat__native_country_Thailand": 55,
    "cat__native_country_Cambodia": 56,
    "cat__native_country_Iran": 57,
    "cat__native_country_Outlying-US(Guam-USVI-etc)": 58,
    "num__is_female": 59,
    "num__is_white": 60,
    "cat__native_country_Haiti": 61,
    "cat__native_country_Italy": 62,
    "cat__native_country_Ireland": 63,
    "cat__native_country_Taiwan": 64,
    "cat__native_country_Hungary": 65,
    "cat__native_country_Portugal": 66,
    "cat__occupation_Sales": 67,
    "cat__native_country_Japan": 68,
    "cat__native_country_Canada": 69,
    "cat__native_country_Hong": 70,
    "cat__native_country_Honduras": 71,
    "num__is_black": 72,
    "cat__native_country_England": 73,
    "cat__native_country_Yugoslavia": 74,
    "cat__work_class_Never-worked": 75,
    "cat__native_country_France": 76,
    "cat__occupation_Armed-Forces": 77,
    "cat__native_country_Holand-Netherlands": 78,
}

# LGBM feature ranks (1 = most important)
LGBM_RANKS = {
    "num__capital_net": 1,
    "num__age": 2,
    "num__hours_per_week": 3,
    "num__education": 4,
    "cat__relationship_Married": 5,
    "num__is_female": 6,
    "cat__work_class_Private": 7,
    "cat__work_class_Self-emp-not-inc": 8,
    "cat__occupation_Exec-managerial": 9,
    "cat__occupation_Prof-specialty": 10,
    "cat__relationship_Unmarried": 11,
    "cat__work_class_Local-gov": 12,
    "cat__occupation_Other-service": 13,
    "cat__occupation_Sales": 14,
    "cat__relationship_Not-in-family": 15,
    "cat__occupation_Farming-fishing": 16,
    "num__is_white": 17,
    "cat__native_country_United-States": 18,
    "cat__work_class_State-gov": 19,
    "cat__occupation_Transport-moving": 20,
    "cat__occupation_Adm-clerical": 21,
    "cat__occupation_Protective-serv": 22,
    "cat__native_country_None": 23,
    "cat__work_class_Self-emp-inc": 24,
    "cat__work_class_Federal-gov": 25,
    "num__is_black": 26,
    "cat__occupation_Handlers-cleaners": 27,
    "cat__occupation_Tech-support": 28,
    "cat__occupation_Craft-repair": 29,
    "cat__work_class_None": 30,
    "cat__native_country_Mexico": 31,
    "cat__occupation_Machine-op-inspct": 32,
    "cat__relationship_Own-child": 33,
    "cat__native_country_Philippines": 34,
    "cat__native_country_Columbia": 35,
    "cat__occupation_None": 36,
    "cat__occupation_Priv-house-serv": 37,
    "cat__native_country_Puerto-Rico": 38,
    "cat__native_country_Vietnam": 39,
    "cat__native_country_Canada": 40,
    "cat__native_country_Ireland": 41,
    "cat__native_country_Italy": 42,
    "cat__native_country_England": 43,
    "cat__native_country_Portugal": 44,
    "cat__native_country_Peru": 45,
    "cat__native_country_Taiwan": 46,
    "cat__native_country_South": 47,
    "cat__native_country_Cambodia": 48,
    "cat__native_country_Dominican-Republic": 49,
    "cat__native_country_Guatemala": 50,
    "cat__native_country_China": 51,
    "cat__native_country_Cuba": 52,
    "cat__native_country_France": 53,
    "cat__native_country_Trinadad&Tobago": 54,
    "cat__native_country_Nicaragua": 55,
    "cat__native_country_India": 56,
    "cat__native_country_Greece": 57,
    "cat__native_country_Scotland": 58,
    "cat__native_country_Outlying-US(Guam-USVI-etc)": 59,
    "cat__native_country_Poland": 60,
    "cat__occupation_Armed-Forces": 61,
    "cat__native_country_Yugoslavia": 62,
    "cat__native_country_Thailand": 63,
    "cat__work_class_Never-worked": 64,
    "cat__work_class_Without-pay": 65,
    "cat__native_country_Laos": 66,
    "cat__native_country_Japan": 67,
    "cat__native_country_Jamaica": 68,
    "cat__native_country_Iran": 69,
    "cat__native_country_Hungary": 70,
    "cat__native_country_Hong": 71,
    "cat__native_country_Honduras": 72,
    "cat__native_country_Haiti": 73,
    "cat__native_country_Germany": 74,
    "cat__native_country_El-Salvador": 75,
    "cat__native_country_Ecuador": 76,
    "cat__relationship_Other-relative": 77,
    "cat__native_country_Holand-Netherlands": 78,
}

# Top 5 features for each model
GLM_TOP5 = [
    "cat__relationship_Own-child",
    "num__capital_net",
    "cat__relationship_Unmarried",
    "cat__relationship_Not-in-family",
    "cat__relationship_Married",
]

LGBM_TOP5 = [
    "num__capital_net",
    "num__age",
    "num__hours_per_week",
    "num__education",
    "cat__relationship_Married",
]

MAX_RANK = 78


def feature_importance_rank() -> None:
    """
    Plot rank comparison of top 5 features for both GLM and LGBM models.

    Shows two charts side by side:
    - Left: Top 5 GLM features with their ranks in both models
    - Right: Top 5 LGBM features with their ranks in both models

    Higher bars indicate better rank (rank 1 = highest bar).
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(5)
    width = 0.35

    # Left chart: Top 5 GLM features
    ax1 = axes[0]

    glm_ranks_for_glm_top5 = [GLM_RANKS[f] for f in GLM_TOP5]
    lgbm_ranks_for_glm_top5 = [LGBM_RANKS[f] for f in GLM_TOP5]

    # Convert ranks to "inverse rank" so higher bar = better rank
    glm_bars = [MAX_RANK - r + 1 for r in glm_ranks_for_glm_top5]
    lgbm_bars = [MAX_RANK - r + 1 for r in lgbm_ranks_for_glm_top5]

    ax1.bar(x - width / 2, glm_bars, width, label="GLM Rank", color="steelblue")
    ax1.bar(x + width / 2, lgbm_bars, width, label="LGBM Rank", color="darkorange")

    ax1.set_xlabel("Feature")
    ax1.set_ylabel("Inverse Rank (higher = more important)")
    ax1.set_title("Top 5 GLM Features: Rank Comparison")
    ax1.set_xticks(x)
    ax1.set_xticklabels(
        [f.replace("cat__", "").replace("num__", "") for f in GLM_TOP5],
        rotation=45,
        ha="right",
    )
    ax1.grid(axis="y", alpha=0.3)

    # Add rank annotations on bars
    for i, (g_rank, l_rank) in enumerate(
        zip(glm_ranks_for_glm_top5, lgbm_ranks_for_glm_top5)
    ):
        ax1.annotate(
            f"#{g_rank}", (i - width / 2, glm_bars[i] + 0.5), ha="center", fontsize=9
        )
        ax1.annotate(
            f"#{l_rank}", (i + width / 2, lgbm_bars[i] + 0.5), ha="center", fontsize=9
        )

    # Right chart: Top 5 LGBM features
    ax2 = axes[1]

    glm_ranks_for_lgbm_top5 = [GLM_RANKS[f] for f in LGBM_TOP5]
    lgbm_ranks_for_lgbm_top5 = [LGBM_RANKS[f] for f in LGBM_TOP5]

    glm_bars = [MAX_RANK - r + 1 for r in glm_ranks_for_lgbm_top5]
    lgbm_bars = [MAX_RANK - r + 1 for r in lgbm_ranks_for_lgbm_top5]

    ax2.bar(x - width / 2, glm_bars, width, label="GLM Rank", color="steelblue")
    ax2.bar(x + width / 2, lgbm_bars, width, label="LGBM Rank", color="darkorange")

    ax2.set_xlabel("Feature")
    ax2.set_ylabel("Inverse Rank (higher = more important)")
    ax2.set_title("Top 5 LGBM Features: Rank Comparison")
    ax2.set_xticks(x)
    ax2.set_xticklabels(
        [f.replace("cat__", "").replace("num__", "") for f in LGBM_TOP5],
        rotation=45,
        ha="right",
    )
    ax2.grid(axis="y", alpha=0.3)

    # Add rank annotations on bars
    for i, (g_rank, l_rank) in enumerate(
        zip(glm_ranks_for_lgbm_top5, lgbm_ranks_for_lgbm_top5)
    ):
        ax2.annotate(
            f"#{g_rank}", (i - width / 2, glm_bars[i] + 0.5), ha="center", fontsize=9
        )
        ax2.annotate(
            f"#{l_rank}", (i + width / 2, lgbm_bars[i] + 0.5), ha="center", fontsize=9
        )

    plt.suptitle("Feature Importance Rank Comparison: GLM vs LGBM", fontsize=14, y=1.02)

    # Single legend in top left, outside charts
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.01, 0.98))

    plt.tight_layout()
    plt.show()
