# %% [code]
import math
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc
)


def distribution_plot(numeric_df, data):

    numeric_cols = numeric_df.columns
    n = len(numeric_cols)
    cols_per_row = 4
    rows = math.ceil(n / cols_per_row)

    fig, axes = plt.subplots(
        rows, cols_per_row,
        figsize=(cols_per_row * 4, rows * 3.5)
    )
    axes = axes.flatten()

    palette = sns.color_palette("crest", n)

    for i, col in enumerate(numeric_cols):
        sns.histplot(
            numeric_df[col],   
            bins=20,
            kde=True,
            ax=axes[i],
            color=palette[i]
        )
        axes[i].set_title(col, fontsize=10)
        axes[i].set_xlabel("")

    for ax in axes[n:]:
        ax.remove()

    fig.suptitle(f"Distributions of {data} data", fontsize=16, y=1.02)
    fig.tight_layout()
    plt.show()
    
def corr_plot(corr_matrix, title):
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        linewidths=0.3,
        square=True,
        cbar_kws={"shrink": 0.6},
    )
    plt.xticks(rotation=0, ha="center")
    plt.yticks(rotation=0)
    plt.title(title)
    plt.tight_layout()
    plt.show()

def plot_confusion_matrix(
    y_true = None,
    y_pred = None,
    cm = None,
    class_names = None,
    model_name = "Model",
    figsize = (7, 6),
    cmap = "Reds",
    normalize = False,
    show_metrics = True,
    save_path = None,
):
    if cm is None:

        if y_true is None or y_pred is None:
            raise ValueError(
                "Provide either (y_true, y_pred) or cm."
            )

        cm = confusion_matrix(y_true, y_pred)

    cm = np.asarray(cm)

    if class_names is None:
        class_names = [f"Class {i}" for i in range(cm.shape[0])]

    metrics_text = ""

    if (
        show_metrics
        and y_true is not None
        and y_pred is not None
        and len(np.unique(y_true)) == 2
    ):
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred)
        rec = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        metrics_text = (
            f"\nAccuracy={acc:.3f} | "
            f"Precision={prec:.3f} | "
            f"Recall={rec:.3f} | "
            f"F1={f1:.3f}"
        )

    percentages = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100

    annotations = np.empty_like(cm).astype(str)

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):

            if normalize:
                annotations[i, j] = (
                    f"{percentages[i, j]:.1f}%"
                )
            else:
                annotations[i, j] = (
                    f"{cm[i, j]:,}\n"
                    f"({percentages[i, j]:.1f}%)"
                )

    fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(
        cm if not normalize else percentages,
        annot=annotations,
        fmt = "",
        cmap = cmap,
        linewidths = 1,
        linecolor = "white",
        cbar = True,
        square = True,
        xticklabels = class_names,
        yticklabels = class_names,
        annot_kws={
            "fontsize": 11,
            "fontweight": "bold"
        },
        ax = ax
    )

    ax.set_title(
        f"Confusion Matrix — {model_name}"
        f"{metrics_text}",
        fontsize = 14,
        fontweight = "bold",
        pad = 20
    )

    ax.set_xlabel(
        "Predicted Label",
        fontsize = 12,
        fontweight = "bold"
    )

    ax.set_ylabel(
        "True Label",
        fontsize = 12,
        fontweight = "bold"
    )

    plt.xticks(rotation=0)
    plt.yticks(rotation=0)

    plt.tight_layout()

    if save_path:
        plt.savefig(
            save_path,
            dpi = 300,
            bbox_inches = "tight"
        )

    plt.show()

    return fig, ax

def plot_roc_curve(
    y_true,
    y_score,
    model_name = "Model",
    figsize = (7, 6),
    color = "navy",
    show_thresholds = False,
    save_path = None,
):

    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize = figsize)

    ax.plot(
        fpr,
        tpr,
        color = color,
        lw = 2.5,
        label=f"{model_name} (AUC = {roc_auc:.3f})"
    )

    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="gray",
        lw=1.5,
        label="Random Classifier"
    )

    if show_thresholds:
        n_points = min(5, len(thresholds))
        idx = np.linspace(0, len(thresholds) - 1, n_points, dtype=int)

        for i in idx:
            ax.scatter(fpr[i], tpr[i], s=40, color=color)
            ax.annotate(
                f"{thresholds[i]:.2f}",
                (fpr[i], tpr[i]),
                fontsize=8,
                xytext=(5, 5),
                textcoords="offset points"
            )

    ax.set_title(
        f"Receiver Operating Characteristic (ROC)\n{model_name}",
        fontsize=14,
        fontweight="bold"
    )

    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])

    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower right", frameon=True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()

    return fig, ax, roc_auc

import matplotlib.pyplot as plt
import pandas as pd


def plot_target_distribution(
    data,
    target_col,
    labels = None,
    colors = None,
    figsize = (12, 5),
    title = None,
    show_percentages = True,
    save_path = None,
):
    
    counts = data[target_col].value_counts().sort_index()

    if labels is None:
        labels = [str(x) for x in counts.index]

    if colors is None:
        colors = plt.cm.Set2.colors[:len(counts)]

    fig, axes = plt.subplots(
        1,
        2,
        figsize = figsize,
        gridspec_kw = {"width_ratios": [1.2, 1]}
    )
    
    bars = axes[0].bar(
        labels,
        counts.values,
        color = colors,
        edgecolor = "black",
        linewidth = 1.0
    )

    axes[0].set_title(
        "Class Distribution",
        fontsize = 13,
        fontweight = "bold"
    )

    axes[0].set_xlabel("Class")
    axes[0].set_ylabel("Count")
    axes[0].grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    total = counts.sum()

    for bar, count in zip(bars, counts.values):

        percentage = 100 * count / total

        text = (
            f"{count:,}\n({percentage:.1f}%)"
            if show_percentages
            else f"{count:,}"
        )

        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            text,
            ha = "center",
            va = "bottom",
            fontsize = 10,
            fontweight = "bold"
        )

    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    wedges, texts, autotexts = axes[1].pie(
        counts.values,
        labels = labels,
        colors = colors,
        autopct = "%1.1f%%",
        startangle = 90,
        counterclock = False,
        wedgeprops = {
            "edgecolor": "white",
            "linewidth": 2
        },
        textprops={
            "fontsize": 10
        }
    )

    for autotext in autotexts:
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    axes[1].set_title(
        "Class Proportion",
        fontsize = 13,
        fontweight = "bold"
    )

    if title is None:
        title = f"Distribution of '{target_col}'"

    fig.suptitle(
        title,
        fontsize = 16,
        fontweight = "bold",
        y = 1.02
    )

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(
            save_path,
            dpi = 300,
            bbox_inches = "tight"
        )

    plt.show()

    return fig, axes

def plot_table(
    df,
    title=None,
    figsize=None,
    font_size=10,
    header_color="#2F5597",
    header_text_color="white",
    row_colors=("#F5F5F5", "white"),
    edge_color="#D0D0D0",
    precision=3,
    save_path=None,
):

    df = df.copy()

    for col in df.select_dtypes(include=np.number).columns:
        df[col] = df[col].map(
            lambda x: f"{x:.{precision}f}"
            if isinstance(x, (float, np.floating))
            else f"{x:,}"
        )

    n_rows, n_cols = df.shape

    if figsize is None:
        width = max(8, n_cols * 2)
        height = max(1.5, 0.45 * n_rows + 1.2)
        figsize = (width, height)

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        colLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1.1, 1.4)

    for (row, col), cell in table.get_celld().items():

        cell.set_edgecolor(edge_color)

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(
                color=header_text_color,
                weight="bold"
            )
            cell.set_height(0.08)

        else:
            cell.set_facecolor(
                row_colors[(row - 1) % len(row_colors)]
            )

    for row in range(1, n_rows + 1):
        table[(row, 0)].set_text_props(weight="bold")

    if title:
        plt.title(
            title,
            fontsize=14,
            fontweight="bold",
            pad=20
        )

    plt.tight_layout()

    if save_path:
        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

    plt.show()

    return fig, ax

def plot_boxplots(
    data,
    columns = None,
    figsize = None,
    title = "Feature Distributions and Outliers",
    rotation = 45,
    sort_by_variance = False,
    showfliers = True,
    orient = "v",
    palette = "Set2",
    save_path = None,
):
    
    if columns is None:
        df = data.select_dtypes(include=np.number).copy()
    else:
        df = data[columns].copy()

    if df.empty:
        raise ValueError("No numeric columns available.")

    if sort_by_variance:
        order = df.var().sort_values(ascending=False).index
        df = df[order]

    if figsize is None:
        if orient == "v":
            figsize = (max(10, 1.2 * len(df.columns)), 6)
        else:
            figsize = (8, max(5, 0.5 * len(df.columns)))

    fig, ax = plt.subplots(figsize=figsize)

    sns.boxplot(
        data=df,
        orient=orient,
        showfliers=showfliers,
        linewidth=1.2,
        palette=palette,
        ax=ax,
    )

    ax.set_title(
        title,
        fontsize=15,
        fontweight="bold",
        pad=15
    )

    if orient == "v":
        ax.set_xticklabels(
            ax.get_xticklabels(),
            rotation=rotation,
            ha="right"
        )
        ax.set_xlabel("")
        ax.set_ylabel("Value")
    else:
        ax.set_ylabel("")
        ax.set_xlabel("Value")

    ax.grid(
        axis="y" if orient == "v" else "x",
        linestyle="--",
        alpha=0.3
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    if save_path:
        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

    plt.show()

    return fig, ax