import matplotlib.pyplot as plt
import numpy as np

from statsmodels.nonparametric.kde import KDEUnivariate
import seaborn as sns

def plot_top_kde(
    gdata,
    result_field: str,
    show_sgnt: bool = True,
    top_n: int = 2,
    violin: bool = True,
    sgnt_label: str = "sgNon-targeting",
    figsize: tuple = (5, 2.7),
    min_count: int = 0
):
    """
    Plot the KDE distribution of Aitchison distances, with options to highlight sgNon-targeting and the top_n genes with the highest distances.

    Args:
        gdata: AnnData object (must contain gdata.var[result_field])
        result_field: Name of the distance column in gdata.var (usually "aitchison_dist")
        show_sgnt: Whether to highlight sgNon-targeting
        top_n: Number of top genes with highest distances to highlight
        violin: Whether to plot "violin" vertical lines (one per data point)
        sgnt_label: Name of the sgNon-targeting guide
        figsize: Figure size
    """

    if (result_field not in gdata.var.columns) or (gdata.var[result_field].notna().sum() <= 0):
        raise ValueError(f"{result_field} not found in gdata.var or all values are NA/0")
        return

    var = gdata.var.copy()
    if 'TotalCount' in var.columns:
        var_sub = var[var['TotalCount'] > min_count]
    else:
        var_sub = var

    if len(var_sub) == 0 or result_field not in var_sub.columns:
        raise ValueError(f"{result_field} not found in valid gene list")
        return

    vals = var_sub[result_field].values
    kde = KDEUnivariate(vals)
    kde.fit()

    fig, ax = plt.subplots(2, 1, figsize=figsize, sharex=False, height_ratios=[3, 1], gridspec_kw={'hspace': 0})
    ax[0].set_ylim(0, max(kde.density)*1.15)

    ax[0].fill_between(kde.support, kde.density, alpha=1, color='gray')
    ax[0].plot(kde.support, kde.density, color='gray')

    lim = ax[0].get_xlim()
    ax[0].set_xlabel('')
    ax[0].set_xticks([])
    ax[0].set_ylabel('Density')
    sns.despine(ax=ax[0])

    if violin:
        for val in var_sub[result_field]:
            ax[1].vlines(x=val, ymin=0, ymax=1, color='gray', linestyles='-', alpha=0.3, linewidth=2)

    if show_sgnt and (sgnt_label in var_sub.index):
        sgnt_val = var_sub.loc[sgnt_label, result_field]
        color = 'red'
        yval = kde.density[np.abs(kde.support - sgnt_val).argmin()]
        ax[0].vlines(x=sgnt_val, ymin=0, ymax=yval,
                     color=color, linestyles='-', linewidth=3, alpha=1, zorder=10)
        ax[0].text(sgnt_val, yval, sgnt_label,
                   color=color, rotation=0, ha='left', va='bottom', fontsize=9, fontweight='bold', zorder=11)
        ax[1].vlines(x=sgnt_val, ymin=0, ymax=1, color=color, linestyles='-', linewidth=3, alpha=1, zorder=10)

    top_genes = (
        var_sub.loc[var_sub.index != sgnt_label, result_field]
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
    colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(top_genes)))
    for i, gene in enumerate(top_genes):
        val = var_sub.loc[gene, result_field]
        color = colors[i % len(colors)]
        yval = kde.density[np.abs(kde.support - val).argmin()]
        ax[0].vlines(x=val, ymin=0, ymax=yval,
                     color=color, linestyles='--', alpha=1, linewidth=2)
        ax[0].text(val, yval, gene,
                   color=color, rotation=0, ha='left', va='bottom', fontsize=8, fontweight='bold')
        ax[1].vlines(x=val, ymin=0, ymax=1, color=color, linestyles='-', alpha=1, linewidth=3)

    ax[1].set_facecolor('whitesmoke')
    ax[1].set_ylim(0, 1)
    ax[1].set_xlim(lim)
    ax[1].set_xlabel(result_field.replace('_', ' ').capitalize())
    ax[1].set_ylabel('')
    ax[1].set_yticks([])

    plt.tight_layout()
    plt.show()
