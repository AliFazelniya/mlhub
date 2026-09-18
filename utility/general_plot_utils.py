# %% [code]
import math
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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