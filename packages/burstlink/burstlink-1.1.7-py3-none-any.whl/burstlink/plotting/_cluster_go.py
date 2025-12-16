# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle
import matplotlib.patches as mpatches
import seaborn as sns
import gseapy as gp
from sklearn.cluster import KMeans
from collections import defaultdict



def _parse_overlap(s):
    try:
        k, m = s.split("/")
        k, m = int(k), int(m)
        return k, m, k / float(m)
    except Exception:
        return np.nan, np.nan, np.nan


def _norm_gene_list(glist):
    arr = np.asarray(glist).ravel()
    genes = [str(g).strip().upper() for g in arr if str(g).strip() != ""]
    return genes


def _enrich_one_group(glist, gene_sets, organism, top_n_each, group_name):
    if len(glist) == 0:
        return None

    enr = gp.enrichr(
        gene_list=list(set(glist)),
        gene_sets=gene_sets,
        organism=organism,
        outdir=None,
        cutoff=1.0
    )
    res = enr.results.copy()
    if res is None or res.empty:
        return None

    res = res.sort_values("Adjusted P-value").head(top_n_each).reset_index(drop=True)
    res["group"] = group_name
    return res


def _choose_n_clusters(n_genes, max_clusters=8, genes_per_cluster=80):
    if n_genes <= 0:
        return 0
    est = int(np.ceil(n_genes / genes_per_cluster))
    est = max(1, min(max_clusters, est))
    est = min(est, n_genes)  # 聚类数不能超过样本数
    return est


def _name_cluster_by_go(cluster_genes, gene_sets, organism):
    if len(cluster_genes) == 0:
        return "Unknown"

    try:
        enr = gp.enrichr(
            gene_list=list(set(cluster_genes)),
            gene_sets=gene_sets,
            organism=organism,
            outdir=None,
            cutoff=1.0
        )
        res = enr.results
    except Exception:
        return "Unknown"

    if res is None or res.empty:
        return "Unknown"

    res = res.sort_values("Adjusted P-value")
    top_term = res.iloc[0]["Term"]
    # 取前 4 个词，避免太长
    words = str(top_term).split()
    short_name = " ".join(words[:4])
    return short_name




def go_sankey_clustered_groups(
        tf_up_genes,
        tf_down_genes,
        tg_up_genes,
        tg_down_genes,
        gene_sets="GO_Biological_Process_2021",
        organism="Mouse",
        top_n_each=8,
        top_n_terms_global=12,
        max_clusters_per_group=8,
        genes_per_cluster=80,
        figsize=(8, 3.5),
        dpi=900
    ):
    """
    Generate a clustered GO-term Sankey diagram for four gene groups (TF_up, TF_down,
    TG_up, TG_down) and visualize shared biological processes with cluster-to-term
    link weights.

    This function performs the following steps:

    1. Normalize gene symbols and assign each gene to one of four groups.
    2. Perform GO enrichment (Biological Process) for each group separately.
    3. Collect significant GO terms across groups and select globally top enriched terms.
    4. Build gene–term hit matrices and cluster genes within each group using K-means.
    5. Annotate each cluster with representative biological functions inferred from GO terms.
    6. Construct a Sankey diagram linking clusters to GO terms; edge width reflects hit counts.
    7. Draw a summary bubble chart of -log10(min adjusted P-value) per GO term.
    8. Save the figure and print a clustering summary table.

    Parameters
    ----------
    tf_up_genes : list[str]
        Up-regulated transcription factor genes.
    tf_down_genes : list[str]
        Down-regulated transcription factor genes.
    tg_up_genes : list[str]
        Up-regulated target genes.
    tg_down_genes : list[str]
        Down-regulated target genes.
    gene_sets : str, default="GO_Biological_Process_2021"
        GO database name used for enrichment.
    organism : str, default="Mouse"
        Organism used in GO analysis.
    top_n_each : int, default=8
        Number of top enriched GO terms retained per group.
    top_n_terms_global : int, default=12
        Number of globally most significant GO terms to visualize.
    max_clusters_per_group : int, default=8
        Maximum number of clusters allowed for any group.
    genes_per_cluster : int, default=80
        Approximate number of genes per cluster (controls K-means k).
    figsize : tuple[float, float], default=(8, 3.5)
        Output figure size.
    dpi : int, default=900
        Output figure resolution.

    Returns
    -------
    None
        This function prints a clustering summary table and saves the figure.

    Notes
    -----
    - Gene clusters are annotated by enriched GO functions to provide biologically meaningful
      labels.
    - Edge width and transparency encode support between clusters and GO terms.
    """
    tf_up_genes_u = _norm_gene_list(tf_up_genes)
    tf_down_genes_u = _norm_gene_list(tf_down_genes)
    tg_up_genes_u = _norm_gene_list(tg_up_genes)
    tg_down_genes_u = _norm_gene_list(tg_down_genes)

    group_labels = ["TF_up", "TF_down", "TG_up", "TG_down"]
    group_colors = {
    "TF_up":   "#2ca02c",   
    "TF_down": "#98df8a",   
    "TG_up":   "#d62728",   
    "TG_down": "#1f77b4"}

    gene_to_group = {}
    for g in tf_up_genes_u:
        gene_to_group[g] = "TF_up"
    for g in tf_down_genes_u:
        gene_to_group.setdefault(g, "TF_down")
    for g in tg_up_genes_u:
        gene_to_group.setdefault(g, "TG_up")
    for g in tg_down_genes_u:
        gene_to_group.setdefault(g, "TG_down")

    go_tf_up = _enrich_one_group(tf_up_genes_u, gene_sets, organism, top_n_each, "TF_up")
    go_tf_down = _enrich_one_group(tf_down_genes_u, gene_sets, organism, top_n_each, "TF_down")
    go_tg_up = _enrich_one_group(tg_up_genes_u, gene_sets, organism, top_n_each, "TG_up")
    go_tg_down = _enrich_one_group(tg_down_genes_u, gene_sets, organism, top_n_each, "TG_down")

    dfs = [x for x in [go_tf_up, go_tf_down, go_tg_up, go_tg_down] if x is not None]
    if len(dfs) == 0:
        raise ValueError("四组基因的 GO 富集结果都为空，请检查输入基因或数据库设置。")

    go_all = pd.concat(dfs, axis=0, ignore_index=True)

    term_stats = {}
    for _, row in go_all.iterrows():
        term = row["Term"]
        group = row["group"]
        p_adj = float(row["Adjusted P-value"])
        overlap = row["Overlap"]
        minus_log10_p = -np.log10(p_adj + 1e-308)
        k, m, r = _parse_overlap(overlap)

        if term not in term_stats:
            term_stats[term] = {
                "min_p": p_adj,
                "max_minus_log10_p": minus_log10_p,
                "groups": set([group]),
                "hit_ratio_max": r if not np.isnan(r) else np.nan,
                "hit_count_sum": k if not np.isnan(k) else 0,
                "p_by_group": {group: p_adj},
                "overlap_by_group": {group: overlap}
            }
        else:
            d = term_stats[term]
            d["min_p"] = min(d["min_p"], p_adj)
            d["max_minus_log10_p"] = max(d["max_minus_log10_p"], minus_log10_p)
            d["groups"].add(group)

            if not np.isnan(r):
                if np.isnan(d["hit_ratio_max"]):
                    d["hit_ratio_max"] = r
                else:
                    d["hit_ratio_max"] = max(d["hit_ratio_max"], r)
            if not np.isnan(k):
                d["hit_count_sum"] += k

            # 按 group 记录 p 和 overlap（如果重复，就用更小的 p 值）
            if group in d["p_by_group"]:
                if p_adj < d["p_by_group"][group]:
                    d["p_by_group"][group] = p_adj
                    d["overlap_by_group"][group] = overlap
            else:
                d["p_by_group"][group] = p_adj
                d["overlap_by_group"][group] = overlap

    rows = []
    for term, d in term_stats.items():
        row = {
            "Term": term,
            "min_p": d["min_p"],
            "max_minus_log10_p": d["max_minus_log10_p"],
            "hit_ratio_max": d["hit_ratio_max"],
            "hit_count_sum": d["hit_count_sum"],
            "groups": ",".join(sorted(list(d["groups"])))
        }
        for grp in group_labels:
            row[f"p_{grp}"] = d["p_by_group"].get(grp, np.nan)
            row[f"overlap_{grp}"] = d["overlap_by_group"].get(grp, None)
        rows.append(row)

    go_term_table = pd.DataFrame(rows)

    go_term_table = go_term_table.sort_values("min_p").head(top_n_terms_global).reset_index(drop=True)
    terms_global = list(go_term_table["Term"].values)
    n_terms = len(terms_global)

    def _build_gene_term_hits(go_res_group, group_label):
        if go_res_group is None:
            return [], np.zeros((0, n_terms), dtype=int)

        term_to_genes = {}
        for _, row in go_res_group.iterrows():
            term = row["Term"]
            if term not in terms_global:
                continue
            raw_hits = str(row["Genes"]).replace("/", ";").split(";")
            hit_genes = [g.strip().upper() for g in raw_hits if g.strip() != ""]
            term_to_genes.setdefault(term, set()).update(hit_genes)

        genes = set()
        for t in terms_global:
            if t in term_to_genes:
                genes.update(term_to_genes[t])

        genes_group = [g for g in genes if gene_to_group.get(g, None) == group_label]
        genes_group = sorted(genes_group)

        if len(genes_group) == 0:
            return [], np.zeros((0, n_terms), dtype=int)

        mat = np.zeros((len(genes_group), n_terms), dtype=int)
        term_index = {t: i for i, t in enumerate(terms_global)}
        for t, gset in term_to_genes.items():
            if t not in term_index:
                continue
            j = term_index[t]
            for g in gset:
                if g in gene_to_group and gene_to_group[g] == group_label and g in genes_group:
                    i = genes_group.index(g)
                    mat[i, j] = 1
        return genes_group, mat

    genes_tf_up, hits_tf_up = _build_gene_term_hits(go_tf_up, "TF_up")
    genes_tf_down, hits_tf_down = _build_gene_term_hits(go_tf_down, "TF_down")
    genes_tg_up, hits_tg_up = _build_gene_term_hits(go_tg_up, "TG_up")
    genes_tg_down, hits_tg_down = _build_gene_term_hits(go_tg_down, "TG_down")

    def _cluster_group(genes_group, hits_group, group_label):
        cluster_for_gene = {}
        cluster_sizes = {}
        cluster_names_ordered = []

        n = len(genes_group)
        if n == 0:
            return cluster_names_ordered, cluster_for_gene, cluster_sizes

        n_clusters = _choose_n_clusters(
            n_genes=n,
            max_clusters=max_clusters_per_group,
            genes_per_cluster=genes_per_cluster
        )
        if n_clusters <= 1:
            cname = f"{group_label}-C1"
            for g in genes_group:
                cluster_for_gene[(group_label, g)] = cname
            cluster_sizes[cname] = n
            cluster_names_ordered = [cname]
            return cluster_names_ordered, cluster_for_gene, cluster_sizes

        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=10)
        labels = kmeans.fit_predict(hits_group)

        cluster_to_genes = {}
        for g, lab in zip(genes_group, labels):
            cluster_to_genes.setdefault(lab, []).append(g)

        labs_sorted = sorted(cluster_to_genes.keys(),
                             key=lambda lab: len(cluster_to_genes[lab]),
                             reverse=True)

        for idx, lab in enumerate(labs_sorted, start=1):
            g_list = cluster_to_genes[lab]
            cname = f"{group_label}-C{idx}"
            cluster_names_ordered.append(cname)
            cluster_sizes[cname] = len(g_list)
            for g in g_list:
                cluster_for_gene[(group_label, g)] = cname

        return cluster_names_ordered, cluster_for_gene, cluster_sizes

    clusters_tf_up, cluster_for_gene_tf_up, cluster_sizes_tf_up = _cluster_group(genes_tf_up, hits_tf_up, "TF_up")
    clusters_tf_down, cluster_for_gene_tf_down, cluster_sizes_tf_down = _cluster_group(genes_tf_down, hits_tf_down, "TF_down")
    clusters_tg_up, cluster_for_gene_tg_up, cluster_sizes_tg_up = _cluster_group(genes_tg_up, hits_tg_up, "TG_up")
    clusters_tg_down, cluster_for_gene_tg_down, cluster_sizes_tg_down = _cluster_group(genes_tg_down, hits_tg_down, "TG_down")

    cluster_for_gene = {}
    cluster_for_gene.update(cluster_for_gene_tf_up)
    cluster_for_gene.update(cluster_for_gene_tf_down)
    cluster_for_gene.update(cluster_for_gene_tg_up)
    cluster_for_gene.update(cluster_for_gene_tg_down)

    cluster_group = {}
    for cname in clusters_tf_up:
        cluster_group[cname] = "TF_up"
    for cname in clusters_tf_down:
        cluster_group[cname] = "TF_down"
    for cname in clusters_tg_up:
        cluster_group[cname] = "TG_up"
    for cname in clusters_tg_down:
        cluster_group[cname] = "TG_down"

    clusters_all = (
        clusters_tf_up
        + clusters_tf_down
        + clusters_tg_up
        + clusters_tg_down
    )

    cluster_function_name = {}
    for cname in clusters_tf_up:
        genes = [g for (grp, g), c in cluster_for_gene.items()
                 if grp == "TF_up" and c == cname]
        cluster_function_name[cname] = _name_cluster_by_go(genes, gene_sets, organism)
    for cname in clusters_tf_down:
        genes = [g for (grp, g), c in cluster_for_gene.items()
                 if grp == "TF_down" and c == cname]
        cluster_function_name[cname] = _name_cluster_by_go(genes, gene_sets, organism)
    for cname in clusters_tg_up:
        genes = [g for (grp, g), c in cluster_for_gene.items()
                 if grp == "TG_up" and c == cname]
        cluster_function_name[cname] = _name_cluster_by_go(genes, gene_sets, organism)
    for cname in clusters_tg_down:
        genes = [g for (grp, g), c in cluster_for_gene.items()
                 if grp == "TG_down" and c == cname]
        cluster_function_name[cname] = _name_cluster_by_go(genes, gene_sets, organism)

    def _build_edges_cluster(go_res_group, group_label):
        edges = []
        if go_res_group is None:
            return edges
        for _, row in go_res_group.iterrows():
            term = row["Term"]
            if term not in terms_global:
                continue
            raw_hits = str(row["Genes"]).replace("/", ";").split(";")
            hit_genes = [g.strip().upper() for g in raw_hits if g.strip() != ""]
            for g in hit_genes:
                key = (group_label, g)
                if key in cluster_for_gene:
                    cname = cluster_for_gene[key]
                    edges.append((cname, term, group_label))
        return edges

    edges_tf_up_c = _build_edges_cluster(go_tf_up, "TF_up")
    edges_tf_down_c = _build_edges_cluster(go_tf_down, "TF_down")
    edges_tg_up_c = _build_edges_cluster(go_tg_up, "TG_up")
    edges_tg_down_c = _build_edges_cluster(go_tg_down, "TG_down")
    edges_cluster_raw = edges_tf_up_c + edges_tf_down_c + edges_tg_up_c + edges_tg_down_c

    cluster_term_weight = defaultdict(int)
    for cname, term, grp in edges_cluster_raw:
        if term in terms_global:
            cluster_term_weight[(cname, term)] += 1

    minus_log10_p = -np.log10(go_term_table["min_p"].astype(float).values + 1e-308)
    hit_ratio = go_term_table["hit_ratio_max"].astype(float).values
    hit_count = go_term_table["hit_count_sum"].astype(float).values

    cluster_sizes_all = {}
    cluster_sizes_all.update(cluster_sizes_tf_up)
    cluster_sizes_all.update(cluster_sizes_tf_down)
    cluster_sizes_all.update(cluster_sizes_tg_up)
    cluster_sizes_all.update(cluster_sizes_tg_down)
    max_cluster_size = max(cluster_sizes_all.values()) if cluster_sizes_all else 1

    fig = plt.figure(figsize=figsize, dpi=dpi)
    gs = gridspec.GridSpec(1, 2, width_ratios=[2.3, 1.0], wspace=0.25)

    ax_sankey = fig.add_subplot(gs[0, 0])
    ax_dot = fig.add_subplot(gs[0, 1])

    bar_x0 = 0.0                 
    bar_width = 0.15            
    max_bar_height = 1.2        
    cluster_gap = 0.25         

    cluster_y_center = {}
    cluster_bar_height = {}
    current_y = 0.0

    for cname in clusters_all:
        size = cluster_sizes_all.get(cname, 1)
        bar_h = max_bar_height * (size / max_cluster_size)
        y_bottom = current_y
        y_center = y_bottom + bar_h / 2.0

        cluster_y_center[cname] = y_center
        cluster_bar_height[cname] = bar_h

        grp = cluster_group.get(cname, "Other")
        color = group_colors.get(grp, "#888888")

        rect = Rectangle(
            (bar_x0, y_bottom),
            bar_width, bar_h,
            facecolor=color,
            edgecolor="none",
            zorder=2
        )
        ax_sankey.add_patch(rect)

        # 左侧 label：TF_up-C1: 功能名 (n=30)
        func = cluster_function_name.get(cname, "Unknown")
        size_txt = cluster_sizes_all.get(cname, 0)
        label_text = f"{cname}: {func} (n={size_txt})"

        ax_sankey.text(
            bar_x0 - 0.05, y_center,
            label_text,
            ha="right", va="center",
            fontsize=6.0
        )

        current_y += bar_h + cluster_gap

    cluster_total_height = max(current_y - cluster_gap, 0.5)

    y_terms_center = {}
    term_bar_height = 0.7
    if n_terms > 1:
        term_spacing = cluster_total_height / (n_terms - 1)
    else:
        term_spacing = 1.0

    for i, t in enumerate(terms_global):
        y = i * term_spacing
        y_terms_center[t] = y

    x_start = bar_x0 + bar_width         
    x_end = 1.0                         
    bar_x_term = x_end + 0.02           
    bar_w_term = 0.08

    palette = sns.color_palette("tab20", n_terms)
    term_color = {t: palette[i] for i, t in enumerate(terms_global)}

    if cluster_term_weight:
        max_w = max(cluster_term_weight.values())
    else:
        max_w = 1

    def _lw_for_weight(w):
        return 0.6 + 3.4 * (w / max_w)

    edges = []
    for (cname, term), w in cluster_term_weight.items():
        if cname not in cluster_y_center or term not in y_terms_center:
            continue
        edges.append((cname, term, w))

    # 画曲线
    for cname, term, w in edges:
        y1 = cluster_y_center[cname]   
        y2 = y_terms_center[term]     

        verts = [
            (x_start, y1),
            (x_start + 0.35, y1),
            (x_end - 0.35, y2),
            (x_end, y2),
        ]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        path = Path(verts, codes)
        patch = PathPatch(
            path,
            facecolor='none',
            edgecolor='#B0B0B0',
            lw=_lw_for_weight(w),
            alpha=0.9,
            zorder=1
        )
        ax_sankey.add_patch(patch)

    for t, y in y_terms_center.items():
        ax_sankey.text(
            x_end + 0.15, y,
            t,
            ha="left", va="center",
            fontsize=6.5
        )
        rect = Rectangle(
            (bar_x_term, y - term_bar_height / 2),
            bar_w_term, term_bar_height,
            facecolor=term_color[t],
            edgecolor="none",
            zorder=2
        )
        ax_sankey.add_patch(rect)

    ax_sankey.set_xlim(bar_x0 - 0.9, x_end + 1.2)
    ymax = max(cluster_total_height, (n_terms - 1) * term_spacing) + 0.5
    ax_sankey.set_ylim(-0.5, ymax)
    ax_sankey.axis("off")
    ax_sankey.set_title(
        "Clustered TF_up / TF_down / TG_up / TG_down genes \u2192 Shared GO Biological Processes",
        fontsize=11
    )

    y_pos = np.arange(n_terms)
    size_scale = 100.0          
    base_size = 15.0            

    sizes = (hit_count / (hit_count.max() if hit_count.max() > 0 else 1.0)) * size_scale + base_size

    cmap_blues = cm.Blues
    norm = Normalize(vmin=np.nanmin(hit_ratio), vmax=np.nanmax(hit_ratio))

    sc = ax_dot.scatter(
        minus_log10_p,
        y_pos,
        s=sizes,
        c=hit_ratio,
        cmap=cmap_blues,
        norm=norm,
        edgecolors='none'
    )

    ax_dot.set_xlabel("-log10(min Adjusted P-value across groups)", fontsize=8)
    ax_dot.set_yticks(y_pos)
    ax_dot.set_yticklabels([])
    ax_dot.tick_params(axis='x', labelsize=8)
    ax_dot.invert_yaxis()

    cbar = plt.colorbar(sc, ax=ax_dot, pad=0.02)
    cbar.set_label("Max hit ratio across groups", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    handles = [
        mpatches.Patch(color=group_colors["TF_up"],   label="TF up-regulated"),
        mpatches.Patch(color=group_colors["TF_down"], label="TF down-regulated"),
        mpatches.Patch(color=group_colors["TG_up"],   label="Target up-regulated"),
        mpatches.Patch(color=group_colors["TG_down"], label="Target down-regulated"),
    ]
    ax_sankey.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(-0.7, 1.02),
        fontsize=7,
        frameon=False,
        title="Gene group",
        title_fontsize=8
    )

    plt.tight_layout()
    plt.show()

    cluster_rows = []
    for (grp, gene), cname in cluster_for_gene.items():
        cluster_rows.append({
            "group": grp,
            "gene": gene,
            "cluster": cname,
            "cluster_function": cluster_function_name.get(cname, "Unknown")
        })
    cluster_table = pd.DataFrame(cluster_rows).sort_values(
        ["group", "cluster", "gene"]
    ).reset_index(drop=True)

    return go_term_table, cluster_table
