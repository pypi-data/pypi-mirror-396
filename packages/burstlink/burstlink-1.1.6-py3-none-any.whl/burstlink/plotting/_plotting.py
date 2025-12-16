import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import ttest_ind
import statsmodels.api as sm
import gseapy as gp

import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt


def bar_plus_bubble_chart(x_labels, bar_values, blue_sizes, green_sizes, figsize):
    """
    Draw a combined bar plot and two-row bubble (square) chart for degree statistics.

    Args:
        x_labels (list-like):
            Labels for each gene or item on the x-axis.
        bar_values (array-like):
            Values for the bar chart (e.g., degree differences).
        blue_sizes (array-like):
            Quantities mapped to the top bubble row (e.g., outdegree).
        green_sizes (array-like):
            Quantities mapped to the bottom bubble row (e.g., indegree).

    Returns:
        A figure is created and shown.
    """
    bar_values = np.asarray(bar_values, float)
    green_sizes = np.asarray(green_sizes, float)
    blue_sizes = np.asarray(blue_sizes, float)
    n = len(x_labels)
    bar_width = 0.2; bar_spacing = 0.2
    x = np.arange(n) * (bar_width + bar_spacing)

    fig = plt.figure(figsize=figsize, dpi=900, constrained_layout=True)
    gs = GridSpec(2, 1, height_ratios=[1.0, 1.0], hspace=0.05)
    ax_bar = fig.add_subplot(gs[0])
    ax_bar.bar(x, bar_values, width=bar_width, color="0.7", edgecolor="0.3", linewidth=0.2)
    ax_bar.set_ylabel("value difference", fontsize=0.9, labelpad=1.5)
    ax_bar.set_xlim(x.min() - bar_width, x.max() + bar_width)
    ax_bar.tick_params(axis="y", labelsize=0, pad=0)
    ax_bar.tick_params(axis="y", length=0)
    ax_bar.tick_params(axis="x", labelbottom=False)
    ax_bar.spines["bottom"].set_visible(False)
    ax_bub = fig.add_subplot(gs[1], sharex=ax_bar)
    for ax in [ax_bar, ax_bub]:
        for spine in ax.spines.values():
            spine.set_linewidth(0.1)
    ax.tick_params(axis="both", width=0.1, length=0.8)

    y_blue = np.ones_like(x)        
    y_green = np.zeros_like(x)     
    blue_sizes_clipped  = np.clip(blue_sizes,  0, None)
    green_sizes_clipped = np.clip(green_sizes, 0, None)

    def normalize(arr):
        arr = np.asarray(arr, dtype=float).ravel()
        ptp = np.ptp(arr)
        if ptp == 0: return np.zeros_like(arr)
        return (arr - arr.min()) / (ptp + 1e-12)

    norm_blue  = normalize(blue_sizes_clipped)
    norm_green = normalize(green_sizes_clipped)
    base_gray = np.array([0.85, 0.85, 0.85, 1.0])
    face_blue  = np.tile(base_gray, (n, 1))
    face_green = np.tile(base_gray, (n, 1))
    mask_blue  = blue_sizes_clipped  > 0
    mask_green = green_sizes_clipped > 0
    face_blue[mask_blue]   = plt.cm.Blues(0.3 + 0.8 * norm_blue[mask_blue])
    face_green[mask_green] = plt.cm.Greens(0.1 + 0.3 * norm_green[mask_green])
    edge_blue_color  = "#2171b5"
    edge_green_color = "#238b45"
    fixed_size = 1

    ax_bub.scatter(x, y_blue, s=fixed_size, marker="s", facecolors=face_blue, edgecolors=edge_blue_color, linewidths=0.1)
    ax_bub.scatter(x, y_green, s=fixed_size, marker="s", facecolors=face_green, edgecolors=edge_green_color, linewidths=0.1)
    ax_bub.set_yticks([0, 1])
    ax_bub.set_yticklabels(["Indegree", "Outdegree"], fontsize=1)
    ax_bub.tick_params(axis="y", pad=1)
    ax_bub.set_xlim(x.min() - bar_width, x.max() + bar_width)
    ax_bub.set_xticks(x)
    ax_bub.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=1)
    ax_bub.tick_params(axis="x", pad=0)
    ax_bub.grid(axis="x", linestyle=":", linewidth=0.1, alpha=0.4)
    ax_bub.set_ylim(-0.7, 1.7)
    plt.show()
    return

  
  
def voilon_plots(bf, bs, cv2, tf_idx, tg_idx, figsize):
    """
    Plot side-by-side violin plots comparing TF-like and TG-like genes
    for BF, BS, and CV².

    Args:
        bf (np.ndarray):
            Burst frequency values for all genes.
        bs (np.ndarray):
            Burst size values for all genes.
        cv2 (np.ndarray):
            CV² values for all genes.
        tf_idx (array-like of int):
            Indices of TF-like genes (e.g., indegree − outdegree < 0).
        tg_idx (array-like of int):
            Indices of TG-like genes (e.g., indegree − outdegree ≥ threshold).

    Returns:
        A figure with three violin panels is created and shown.
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize, dpi=900)
    violin_plots2_ax(axes[0], np.log10(bf[tf_idx]), np.log10(bf[tg_idx]), yticks=[-1.5, -0.5, 0.5, 1.5], title="Burst Frequency")
    violin_plots2_ax(axes[1], np.log10(bs[tf_idx]), np.log10(bs[tg_idx]), yticks=[-1.0, 0.0, 1.0, 2.0, 3.0], title="Burst Size")
    violin_plots2_ax(axes[2], np.log10(cv2[tf_idx]), np.log10(cv2[tg_idx]), yticks=[-0.5, 0.0, 0.5, 1.0], title="CV²")
    plt.tight_layout()
    plt.show()
    return


def violin_plots2_ax(ax, vals1, vals2, yticks, title):
    data = np.concatenate([vals1, vals2])
    groups = (['TF'] * len(vals1)) + (['TG'] * len(vals2))
    df = pd.DataFrame({'Group': groups, 'Value': data})
    sns.set(style="whitegrid", font_scale=1.2)
    sns.violinplot(data=df, x='Group', y='Value', palette=['#66C2A5', '#8DA0CB'], inner='box', cut=0, linewidth=1.2, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Value", fontsize=12)
    ax.set_title(title, fontsize=13)
    y_max = df['Value'].max()
    y_min = df['Value'].min()
    bar_y = y_max + (y_max - y_min) * 0.08
    t_stat, p_t = ttest_ind(vals1, vals2, equal_var=False)
    ax.set_yticks(yticks)
    _add_significance_star(ax, 0, 1, bar_y, p_t)
    return t_stat, p_t
    
def _p_to_asterisk(p):
    if p < 0.001: return "***"
    elif p < 0.01: return "**"
    elif p < 0.05: return "*"
    else: return "n.s." 
    
def _add_significance_star(ax, x1, x2, y, p, h=0.05, lw=1.4):
    star = _p_to_asterisk(p)
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=lw, c='k')
    ax.text((x1 + x2) * 0.5, y + h + 0.015, star, ha='center', va='bottom', fontsize=14, fontweight='bold')
    return


def affinity_burst_scatter_plot(res_bursting_tg, figsize):
    r = res_bursting_tg[:, 0] / res_bursting_tg[:, 1]
    bf, bs = res_bursting_tg[:, 2], res_bursting_tg[:, 3]
    expression_level = bf * bs

    idx1 = np.where(np.log10(r) > 1)[0]
    idx2 = np.where(np.log10(bf) < -1.2)[0]
    idx3 = np.where(np.log10(bs) > 2.0)[0]
    idx_union = np.union1d(np.union1d(idx1, idx2), idx3)
    res_bursting_tg = np.delete(res_bursting_tg, idx_union, axis=0)
    r = res_bursting_tg[:, 0] / res_bursting_tg[:, 1]
    bf, bs = res_bursting_tg[:, 2], res_bursting_tg[:, 3]
    expression_level = bf * bs

    params, pvalues = _fit_3d(np.log10(bf), np.log10(bs), np.log10(r))

    fig = plt.figure(figsize=figsize, dpi=900)
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    _scatter_3d_ax(ax1, bf, bs, r, expression_level, "Blues")
    _scatter_2d_ax(ax2, np.log10(bf), np.log10(r), np.log10(expression_level), "log10(bf)", "log10(r)")
    _scatter_2d_ax(ax3, np.log10(bs), np.log10(r), np.log10(expression_level), "log10(bs)", "log10(r)")
    plt.tight_layout()
    plt.show()
    return

def _fit_3d(x, y, z):
    X = np.column_stack((x, y))
    X = sm.add_constant(X)  
    model = sm.OLS(z, X).fit()  
    return model.params, model.pvalues

def _truncate_colormap(cmap, minval=0.0, maxval=1.0, n=256):
    new_cmap = mcolors.LinearSegmentedColormap.from_list( 
        "trunc({},{:.2f},{:.2f})".format(cmap.name, minval, maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def _scatter_3d_ax(ax, bf, bs, r, color, cmap0):
    base_cmap = plt.get_cmap(cmap0)
    new_cmap = _truncate_colormap(base_cmap, 0.35, 1.0)
    sc = ax.scatter(np.log10(bf), np.log10(bs), np.log10(r), c=np.log10(color), cmap=new_cmap, s=15, alpha=1)
    ax.set_xlabel("log10(bf)")
    ax.set_ylabel("log10(bs)")
    ax.set_zlabel("log10(r)")
    return sc

def _scatter_2d_ax(ax, x, y, color, x_label, y_label):
    sc = ax.scatter(x, y, s=28, c=color, cmap=plt.cm.Greens)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    return sc


def scatter_with_variance_plots(burst_info_pos, burst_info_neg, figsize):
    """
    Generate scatter plots with variance bars for positive and negative regulation groups.

    Parameters
    ----------
    burst_info_pos : array-like or tuple
        Burst-related statistics for positively regulated gene groups.
        The input is internally reformatted into a standardized scatter data structure.
    burst_info_neg : array-like or tuple
        Burst-related statistics for negatively regulated gene groups.
        The input is internally reformatted into a standardized scatter data structure.
    figsize : tuple[float, float]
        Size of the output figure.

    Returns
    -------
    None
        This function generates and displays a scatter plot with variance bars.

    Notes
    -----
    - Data from positive and negative regulation groups are concatenated and visualized jointly.
    - Horizontal and vertical error bars represent variability in burst-related metrics.
    """
    burst_info_pos = scatter_datasctructure(burst_info_pos)
    burst_info_neg = scatter_datasctructure(burst_info_neg)
    x = np.hstack([np.sort(burst_info_pos[0]), np.sort(burst_info_pos[4]), np.sort(burst_info_neg[0]), np.sort(burst_info_neg[4])]) 
    y = np.hstack([np.sort(burst_info_pos[2])[::-1], np.sort(burst_info_pos[6])[::-1], np.sort(burst_info_neg[2])[::-1], np.sort(burst_info_neg[6])[::-1]])
    x_err = np.hstack([burst_info_pos[1], burst_info_pos[5], burst_info_neg[1], burst_info_neg[5]])
    y_err = np.hstack([burst_info_pos[3], burst_info_pos[7], burst_info_neg[3], burst_info_neg[7]])
    scatter_with_variance_plotting(x, y, x_err, y_err, figsize)
    return 
    
def scatter_datasctructure(burst_info):
    bf_low = burst_info[0]; bs_low = burst_info[1]
    bf_high = burst_info[2]; bs_high = burst_info[3]
    bf_low_mean, bf_low_std = row_mean_sd(bf_low)
    bs_low_mean, bs_low_std = row_mean_sd(bs_low)
    bf_high_mean, bf_high_std = row_mean_sd(bf_high)
    bs_high_mean, bs_high_std = row_mean_sd(bs_high)
    return [bf_low_mean, bf_low_std, bs_low_mean, bs_low_std, bf_high_mean, bf_high_std*0.5, bs_high_mean, bs_high_std*0.5]
    
def row_mean_sd(arr):
    row_mean = np.mean(arr, axis=1)
    row_std = np.std(arr, axis=1)
    return row_mean, row_std * 0.5

def scatter_with_variance_plotting(x, y, x_err, y_err, figsize, scale=0.2):
    group_size = 5; poly_deg = 2
    n = len(x)
    n_groups = n // group_size

    colors = ["#55A868", "#55A868", "#8172B2", "#8172B2"]
    light_colors = ["#B6E3C5", "#B6E3C5", "#CAB7EA", "#CAB7EA"]
    labels = [f"Group {i+1}" for i in range(n_groups)]
    markers = ['o', 'o', '^', '^']
    fig, ax = plt.subplots(figsize=(figsize[0]*scale, figsize[1]*scale), dpi=900)
    fs_label = 6 * scale; fs_tick  = 6 * scale
    ms = 0.75 * scale; elw = 1.0 * scale   
    cap = 1.5 * scale; fit_lw   = 0.6 * scale; spine_lw = 0.8 * scale
    tick_w = 0.8 * scale; tick_len = 4.0 * scale
    all_x_grid_min = []; all_x_grid_max = []

    for g in range(n_groups):
        start = g * group_size
        end = (g + 1) * group_size
        xg  = np.asarray(x[start:end])
        yg  = np.asarray(y[start:end])
        xge = np.asarray(x_err[start:end])
        yge = np.asarray(y_err[start:end])

        c = colors[g % len(colors)]
        c_light = light_colors[g % len(light_colors)]
        lab = labels[g]
        marker = markers[g % len(markers)]
        mew = 0.6 * scale 
        ax.errorbar(xg, yg, xerr=xge, yerr=yge, fmt=marker, color=c, ecolor=c_light, elinewidth=elw, capsize=cap, markersize=max(3.0*scale, 2.0), 
                    alpha=0.9, markerfacecolor=c, markeredgecolor=c, markeredgewidth=mew)
        if len(xg) > poly_deg:
            coef = np.polyfit(xg, yg, poly_deg)
            x_grid = np.linspace(xg.min(), xg.max(), 200)
            y_pred = np.polyval(coef, x_grid)
            y_fit_on_data = np.polyval(coef, xg)
            resid = yg - y_fit_on_data
            sigma = resid.std(ddof=1) if len(resid) > 1 else 0.0
            y_upper = y_pred + 1.96 * sigma
            y_lower = y_pred - 1.96 * sigma
            ax.plot(x_grid, y_pred, color=c, alpha=0.6, linewidth=fit_lw)
            ax.fill_between(x_grid, y_lower, y_upper, color=c_light, alpha=0.3)
            all_x_grid_min.append(x_grid.min())
            all_x_grid_max.append(x_grid.max())
        else:
            all_x_grid_min.append(xg.min())
            all_x_grid_max.append(xg.max())
    ax.set_xlabel('log10(BF)', fontsize=fs_label, labelpad=0)
    ax.set_ylabel('log10(BS)', fontsize=fs_label, labelpad=0)
    ax.tick_params(axis="both", labelsize=fs_tick, width=tick_w, length=tick_len, pad=0)
    for spine in ax.spines.values(): spine.set_linewidth(spine_lw)
    fig.tight_layout(pad=0.2*scale)
    plt.show()
    return

def bubble_boxplots4(data_list, colors_list, figsize):
    labels = ['10%', '30%', '50%', '70%', '90%']
    fig, axes = plt.subplots(1, 4, figsize=figsize, dpi=900, sharey=True)
    for ax, data, colors in zip(axes, data_list, colors_list):
        bubble_boxplots5_single(ax, data, colors, labels)
    plt.tight_layout()
    plt.show()
    return

def bubble_boxplots5_single(ax, data, colors, labels):
    groups = data.tolist()
    n_groups = len(groups)
    x_pos = np.arange(n_groups)

    bp = ax.boxplot(groups, positions=x_pos, widths=0.5, patch_artist=True, showfliers=False, medianprops=dict(color="black", linewidth=1.3), 
                    whiskerprops=dict(color="0.3"), capprops=dict(color="0.3"))
    for box, c in zip(bp["boxes"], colors):
        base = mcolors.to_rgb(c)
        light = tuple(1 - 0.6 * (1 - v) for v in base)
        box.set_facecolor(light)
        box.set_edgecolor(c)
        box.set_linewidth(1.2)

    for med, c in zip(bp["medians"], colors):
        med.set_color(c)
        med.set_linewidth(2.0)

    for i, (y, c) in enumerate(zip(groups, colors)):
        x_jitter = np.random.normal(loc=x_pos[i], scale=0.08, size=len(y))
        ax.scatter(x_jitter, y, s=50, color=c, alpha=0.8, edgecolors="none", zorder=3)
        y_med = np.median(y)
        ax.hlines(y_med, x_pos[i] - 0.22, x_pos[i] + 0.22, colors=c, linewidth=2.2, zorder=4)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=0)
    ax.set_xlim(-0.5, n_groups - 0.5)
    ax.set_ylabel("log10(CV2)", fontsize=6)

    cmap = ListedColormap(colors)
    norm = plt.Normalize(vmin=0, vmax=len(colors) - 1)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, location='right', fraction=0.06, pad=0.08)
    cbar.set_ticks(np.arange(len(colors)))
    cbar.set_ticklabels(labels)
    cbar.ax.tick_params(labelsize=8)
    return


def violin_plots4_datastructure(info, figsize):
    idx_low = np.where(info[:, 0] < np.median(info[:, 0]))[0]
    idx_high = np.where(info[:, 0] > np.median(info[:, 0]))[0]
    idx_neg = np.where(info[:, 4] < 0)[0]
    idx_pos = np.where(info[:, 4] > 0)[0]

    idx_low_neg = np.intersect1d(idx_low, idx_neg)
    idx_low_pos = np.intersect1d(idx_low, idx_pos)
    idx_high_neg = np.intersect1d(idx_high, idx_neg)
    idx_high_pos = np.intersect1d(idx_high, idx_pos)

    bf_low  = [info[idx_low_neg, 1],  info[idx_low_pos, 1]]
    bf_high = [info[idx_high_neg, 1], info[idx_high_pos, 1]]
    bs_low  = [info[idx_low_neg, 2],  info[idx_low_pos, 2]]
    bs_high = [info[idx_high_neg, 2], info[idx_high_pos, 2]]
    cv2_low  = [info[idx_low_neg, 3],  info[idx_low_pos, 3]]
    cv2_high = [info[idx_high_neg, 3], info[idx_high_pos, 3]]


    fig, axes = plt.subplots(1, 3, figsize=figsize, dpi=900)
    violin_box_plots2(bf_low,  bf_high,  ax=axes[0])
    axes[0].set_title("BF", fontsize=9)
    violin_box_plots2(bs_low,  bs_high,  ax=axes[1])
    axes[1].set_title("BS", fontsize=9)
    violin_box_plots2(cv2_low, cv2_high, ax=axes[2])
    axes[2].set_title("CV²", fontsize=9)
    plt.tight_layout()
    plt.show()
    return

def violin_box_plots2(vals1, vals2, ax):
    group_labels = ["Low-neg"] * len(vals1[0]) + ["Low-pos"] * len(vals1[1]) + \
                   ["High-neg"] * len(vals2[0]) + ["High-pos"] * len(vals2[1])
    values = np.concatenate([vals1[0], vals1[1], vals2[0], vals2[1]])
    df = pd.DataFrame({"Group": group_labels, "Value": values})

    palette = {"Low-neg":  "#5AADE5", "Low-pos":  "#F4B645",
               "High-neg": "#5AADE5", "High-pos": "#F4B645"}

    sns.violinplot(data=df, x="Group", y="Value", palette=palette, inner="box", cut=0, linewidth=1.2, ax=ax)
    ax.set_xticklabels(["Low-neg", "Low-pos", "High-neg", "High-pos"], fontsize=9)
    ax.set_xlabel(None)
    ax.set_ylabel("log10(Value)", fontsize=9)
    ax.tick_params(axis='y', labelsize=9)

    tops = [np.max(vals1[0]), np.max(vals1[1]), np.max(vals2[0]), np.max(vals2[1])]
    y_min, y_max = ax.get_ylim()
    h = 0.03 * (y_max - y_min)
    offset = 0.025 * (y_max - y_min)

    p1 = ttest_ind(vals1[0], vals1[1], equal_var=False).pvalue
    y1 = max(tops[0], tops[1]) + offset
    _add_sig_bar(ax, 0, 1, y=y1, h=h, text=_p_to_asterisk(p1), fontsize=9)

    p2 = ttest_ind(vals2[0], vals2[1], equal_var=False).pvalue
    y2 = max(tops[2], tops[3]) + offset
    _add_sig_bar(ax, 2, 3, y=y2, h=h, text=_p_to_asterisk(p2), fontsize=9)
    return

def _add_sig_bar(ax, x1, x2, y, h, text, fontsize=12):
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c='k')
    ax.text((x1 + x2) / 2, y + h, text, ha='center', va='bottom', fontsize=9)



def box_plots4(bf, bs, cv2, mean, figsize):
    fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=900)
    positions = [[1, 2], [4, 5], [7, 8], [10, 11]]
    colors = ["#23A123", "#CE400C"]
    p_values = []
    for i, group_data in enumerate([bf, bs, cv2, mean]):
        for j, subgroup in enumerate(group_data):
            ax.boxplot(
                subgroup,
                positions=[positions[i][j]],
                patch_artist=True,
                widths=0.6,
                boxprops=dict(facecolor=colors[j], linewidth=0.5),
                capprops=dict(linewidth=0.5),
                whiskerprops=dict(linewidth=0.3),
                medianprops=dict(linewidth=0.5, color='red'),
                showfliers=False
            )
        data_A, data_B = group_data
        p = ttest_ind(data_A, data_B, equal_var=False).pvalue
        p_values.append(p)

        x1, x2 = positions[i]
        y_max = max(np.max(data_A), np.max(data_B))
        h = 0.12
        y = y_max + h + 0.1 * i
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=0.4, color='black')
        ax.text((x1 + x2) / 2, y + h, _p_to_asterisk(p), ha='center', va='bottom', fontsize=5)

    ax.set_xticks([1.5, 4.5, 7.5, 10.5])
    ax.set_xticklabels(['BF', 'BS', 'CV2', 'Mean'], fontsize=4.5)
    ax.set_ylim([-1.4, 3.2])
    ax.set_ylabel('log10(Value)', fontsize=4)
    ax.tick_params(axis='y', labelsize=4)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
    ax.tick_params(axis='both', width=0.5)
    plt.show()
    return



def go_differential_genes(gene_list, cmap, figsize):
    """
    Perform GO enrichment for a gene list and visualize the top GO terms.

    Args:
        gene_list (list or np.ndarray):
            List/array of gene symbols.
        cmap (str):
            Name of a Matplotlib/Seaborn colormap used to color the bars
            and encode the adjusted p-values in the colorbar.

    Returns:
        The function creates and displays a GO barplot.
    """
    go_enrichment_results = go_enrichment_analysis(gene_list.tolist())
    visualize_go_bar(go_enrichment_results, cmap, figsize)
    return
   
def go_enrichment_analysis(gene_list, gene_sets="GO_Biological_Process_2021", organism="Mouse"):
    results = gp.enrichr(gene_list=gene_list, gene_sets=gene_sets, organism=organism, cutoff=0.05)
    return results.res2d

def visualize_go_bar(go_results, cmap, figsize):
    go_results = go_results.sort_values("Adjusted P-value").head(10)
    palette = sns.color_palette(cmap, n_colors=10)
    fig, ax = plt.subplots(figsize=figsize, dpi=900)
    sns.barplot(x=go_results["Overlap"].apply(lambda x: int(x.split('/')[0])), y=go_results["Term"], palette=palette, hue=None, ax=ax, legend=False)
    norm = mpl.colors.Normalize(vmin=go_results["Adjusted P-value"].min(), vmax=go_results["Adjusted P-value"].max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm) 
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", pad=0.02)
    cbar.set_label("p-value", fontsize=4)
    ax.set_xlabel("Gene number", fontsize=8)
    ax.set_ylabel("GO terms", fontsize=8)
    plt.tight_layout()
    plt.show()
    return
