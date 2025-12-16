import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def avg_minerals_all(legusdf):
    minerals = ["Nitrogen (g)",
    "Protein (g)",
    "Fat (g)",
    "Ash (g)",
    "Carbs (g)",
    "Starch (g)",
    "Resistant starch (g)",
    "Iron (mg)",
    "Magnesium (mg)",
    "Phosphorus (mg)",
    "Potassium (mg)",
    "Sodium (mg)",
    "Zinc (mg)",
    "Copper (mg)",
    "Manganese (mg)"]
    # compute means
    mineral_means = legusdf[minerals].mean().reset_index()
    mineral_means.columns = ["Mineral", "Average_Value"]
    # plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=mineral_means, x="Mineral", y="Average_Value")
    plt.title("Average Mineral Content Across All Legumes")
    plt.xlabel("Mineral")
    plt.xticks(rotation=45, fontsize=10)
    plt.ylabel("Average Amount (per 100g sample)")
    for p in ax.patches:
        value = p.get_height()
        x = p.get_x() + p.get_width() / 2
        y = value
        ax.text(x, y, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.show()


def sidebyside_boxes(legusdf):
    beans = legusdf[legusdf["Category"] == "Beans"]

    filtered_beans = beans[(beans["Protein (g)"] < 150) &
                       (beans["Fat (g)"] < 150) &
                       (beans["Carbs (g)"] < 150) &
                       (beans["Calories (kcal)"] < 150)]

    # Select nutrients
    nutrients = ["Protein (g)", "Fat (g)", "Carbs (g)", "Calories (kcal)"]

    # Melt the dataframe from wide → long format
    beans_melted = filtered_beans.melt(value_vars=nutrients, var_name="Nutrient", value_name="Value")

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=beans_melted, x="Nutrient", y="Value")
    plt.title("Nutrient Distributions for Beans")
    plt.xlabel("Nutrient")
    plt.ylabel("Value (per 100g)")

    plt.show()


def corr_heatmap_minerals(legusdf):
    numeric = legusdf.select_dtypes(include="number")
    # Compute correlation matrix
    corr = numeric.corr()
    # Create mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    # Plot heatmap (bottom triangle only)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=1.0
    )
    plt.title("Correlation Heatmap (Bottom Triangle Only)")
    plt.show()