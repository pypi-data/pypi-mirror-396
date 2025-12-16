import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler
from sklearn.linear_model import BayesianRidge
from sklearn.model_selection import train_test_split

from ..plotting import _plotting as plt
from ..plotting import _grn_visualization as grn
from ..plotting import _cluster_go


def visualization_3d_generoles_grn(degrees, burst_info, edges_info, counts_data, figsize):
    grn. visualization_3d_grn(degrees, burst_info, edges_info, counts_data, figsize)
    return
    
    
def identify_gene_roles(degrees_info, res_bursting, cr_genename_info, figsize):
    """
    Identify key TF-like genes and visualize their degree differences.

    This function removes cell-cycle–related genes, rescales in/out degree,
    ranks genes by outdegree - indegree, and plots the top 20 genes with a
    custom bar + bubble chart.

    Args:
        degrees_info (str): Path to degree CSV file.
        res_bursting (str): Path to bursting result TSV with gene names.
        cr_genename_info (str): Path to TSV file containing genes to exclude.
    """
    degrees = pd.read_csv(degrees_info).to_numpy()
    genenames = pd.read_csv(res_bursting, sep='\t').to_numpy()[:, 0].astype(str)
    cr_genename = pd.read_csv(cr_genename_info, sep='\t').to_numpy().astype(str)
    
    cr_genename = np.char.lower(cr_genename)
    mask = np.isin(genenames, cr_genename)           
    idx = np.argwhere(mask)    
    degrees = np.delete(degrees, idx, 0)
    genenames = np.delete(genenames, idx, 0)

    indegree = degrees[:, 1].astype(float)
    outdegree = degrees[:, 2].astype(float)
    degrees_core = np.asarray(np.vstack([indegree, outdegree]))
    degrees_core_scaled = _scaled_data(degrees_core).reshape([2, degrees.shape[0]])
    diff = outdegree - indegree
    degree_info_tf = np.column_stack([genenames, degrees_core_scaled.T, _scaled_data(diff)])
    degree_info_tf = degree_info_tf[np.argsort(degree_info_tf[:, 3].astype(float))[::-1]]

    genename_labels = degree_info_tf[0: 20, 0]
    diff_values = degree_info_tf[0: 20, 3].astype(float)
    indegree_values = degree_info_tf[0: 20, 1].astype(float)
    outdegree_values = degree_info_tf[0: 20,2].astype(float)

    plt.bar_plus_bubble_chart(genename_labels, diff_values, outdegree_values, indegree_values, figsize)
    return

    
def _scaled_data(vals):
    scaler = MinMaxScaler()
    normalized_data = scaler.fit_transform(vals.reshape(-1, 1))
    return normalized_data ** 2


def compare_bursting_with_gene_roles(degree_info, res_bursting, figsize):
    """
    Compare bursting features between TF-like and TG-like genes.

    TF-like genes are defined by indegree - outdegree < 0 and TG-like genes
    by indegree - outdegree >= 45. Burst frequency, burst size and CV² are
    compared using violin plots.

    Args:
        degree_info (np.ndarray): Degree information per gene.
        res_bursting (np.ndarray): Bursting metrics per gene.
    """
    indegree = degree_info[:, 1].astype(float)
    outdegree = degree_info[:, 2].astype(float)
    tf_idx = np.where(indegree - outdegree < 0)[0]
    tg_idx = np.where(indegree - outdegree >= 45)[0]
    bf = res_bursting[:, 4].astype(float)
    bs = res_bursting[:, 5].astype(float)
    cv2 = res_bursting[:, 7].astype(float)
    plt.voilon_plots(bf, bs, cv2, tf_idx, tg_idx, figsize)
    return

def affinity_burst(res_bursting, degrees_info, figsize):
    indegree = degrees_info[:, 1].astype(float)
    outdegree = degrees_info[:, 2].astype(float)
    tg_idx = np.where(indegree - outdegree >= 60)[0]
    res_bursting_tg = res_bursting[np.ix_(tg_idx, [1, 2, 4, 5])].astype(float)
    plt.affinity_burst_scatter_plot(res_bursting_tg, figsize)
    return
    
    
def burst_regulation_bayesian(res_bursting, res_interaction, degrees_info):
    """
    Infer how TF–TG interaction strengths regulate bursting using Bayesian ridge regression.

    Args:
        res_bursting (np.ndarray): Bursting metrics per gene.
        res_interaction (np.ndarray): Gene–gene interaction results.
        degrees_info (np.ndarray): Degree information per gene.

    Returns:
        tuple[list, list]: (burst_info_pos, burst_info_neg) representing
            regression summaries for positive and negative regulation.
    """
    interactions = np.vstack([res_interaction[:, [0, 1, 6, 8]], res_interaction[:, [1, 0, 7, 9]]])
    _, unique_indices = np.unique(interactions[:, 0].astype(str), return_index=True)
    genenames = interactions[:, 0][np.sort(unique_indices)]
    interactions = np.asarray(sorted(interactions.tolist(), key = lambda x: (x[0], x[1])))

    prod = interactions[:, 2].astype(float) * interactions[:, 3].astype(float)
    prod = np.nan_to_num(prod, nan=0.0)
    genenames_dict = {v: i for i, v in enumerate(genenames)}
    genepair_interactions = np.zeros([len(genenames), len(genenames)])
    for n in np.arange(len(genenames)):
        tg = genenames[n]
        idx = np.where(interactions[:, 1] == tg)[0]
        tf = interactions[idx, 0]
        tf_idx = [genenames_dict[x] for x in tf if x in genenames_dict]
        genepair_interactions[n, tf_idx] = prod[idx]
        
    indegree = degrees_info[:, 1].astype(float)
    outdegree = degrees_info[:, 2].astype(float)
    tf_idx = np.where(indegree - outdegree < 0)[0]
    tg_idx = np.where(indegree - outdegree >= 45)[0]
    tg_tf_interactions = genepair_interactions[tg_idx, :]
    tg_tf_interactions = tg_tf_interactions[:, tf_idx]

    bf = res_bursting[tg_idx, 4].astype(float)
    bs = res_bursting[tg_idx, 5].astype(float)
    cv2 = res_bursting[tg_idx, 7].astype(float)
    expression_level = bf * bs

    column_all_zero = np.all(tg_tf_interactions == 0, axis=0)
    idx = np.where(column_all_zero == False)[0]
    tg_tf_interactions = tg_tf_interactions[:, idx]

    idx_low = np.where(expression_level < np.median(expression_level))[0]
    idx_high = np.where(expression_level > np.median(expression_level))[0]
    X_tg_low = tg_tf_interactions[idx_low,:]
    X_tg_high = tg_tf_interactions[idx_high,:]

    pos_percent = np.asarray([0.1, 0.3, 0.5, 0.7, 0.9])
    bf_low = bayesian_ridge_regression(X_tg_low, bf[idx_low], pos_percent)
    bs_low = bayesian_ridge_regression(X_tg_low, bs[idx_low], pos_percent)
    cv2_low = bayesian_ridge_regression(X_tg_low, cv2[idx_low], pos_percent)
    bf_high = bayesian_ridge_regression(X_tg_high, bf[idx_high], pos_percent)
    bs_high = bayesian_ridge_regression(X_tg_high, bs[idx_high], pos_percent)
    cv2_high = bayesian_ridge_regression(X_tg_low, cv2[idx_low], pos_percent)
    burst_info_pos = [bf_low, bs_low, cv2_low, bf_high, bs_high, cv2_high]
    
    neg_percent = np.asarray([0.9, 0.7, 0.5, 0.3, 0.1])
    bf_low = bayesian_ridge_regression(X_tg_low, bf[idx_low], neg_percent)
    bs_low = bayesian_ridge_regression(X_tg_low, bs[idx_low], neg_percent)
    cv2_low = bayesian_ridge_regression(X_tg_low, cv2[idx_low], neg_percent)
    bf_high = bayesian_ridge_regression(X_tg_high, bf[idx_high], neg_percent)
    bs_high = bayesian_ridge_regression(X_tg_high, bs[idx_high], neg_percent)
    cv2_high = bayesian_ridge_regression(X_tg_low, cv2[idx_low], neg_percent)
    burst_info_neg = [bf_low, bs_low, cv2_low, bf_high, bs_high, cv2_high]
    return burst_info_pos, burst_info_neg


def _clean_reduce_X(X, drop_sparse_ratio=0.01, clip_pct=(0.5, 99.5)):
    X = np.asarray(X, dtype=float)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    vt = VarianceThreshold(threshold=0.0)
    X1 = vt.fit_transform(X)
    nz_ratio = (X1 != 0).mean(axis=0)
    keep = nz_ratio >= drop_sparse_ratio
    if keep.sum() == 0:
        keep[np.argmax(np.var(X1, axis=0))] = True
    X2 = X1[:, keep]
    lo, hi = np.percentile(X2, clip_pct[0]), np.percentile(X2, clip_pct[1])
    X2 = np.clip(X2, lo, hi)
    X2 = np.sign(X2) * np.log1p(np.abs(X2))
    scaler = MaxAbsScaler()
    Xs = scaler.fit_transform(X2)
    info = {"vt": vt, "keep": keep, "scaler": scaler, "clip_bounds": (float(lo), float(hi)), "signed_log": True}
    return Xs, info

def _reduce_svd(Xs, n_components=100, random_state=42):
    k = max(1, min(n_components, Xs.shape[1] - 1) if Xs.shape[1] > 1 else 1)
    svd = TruncatedSVD(n_components=k, random_state=random_state)
    Z = svd.fit_transform(Xs).astype(np.float32)
    return Z, svd

def fit_bayes_ridge(Z, y, test_size=0.2, random_state=42):
    X_tr, X_va, y_tr, y_va = train_test_split(Z, y, test_size=test_size, random_state=random_state)
    br = BayesianRidge(max_iter=1000, tol=1e-5, lambda_1=1e-32, lambda_2=1e-32, lambda_init=1e-6, compute_score=False)
    br.fit(X_tr, y_tr)
    return br

def _transform_new_X(X_new, info, svd):
    Xn = np.asarray(X_new, dtype=float)
    Xn = np.nan_to_num(Xn, nan=0.0, posinf=0.0, neginf=0.0)
    Xn = Xn[:, info["vt"].get_support()]
    Xn = Xn[:, info["keep"]]
    lo, hi = info["clip_bounds"]
    Xn = np.clip(Xn, lo, hi)
    if info.get("signed_log", True): Xn = np.sign(Xn) * np.log1p(np.abs(Xn))
    Xn = info["scaler"].transform(Xn)
    if svd is not None: Xn = svd.transform(Xn)
    return Xn.astype(np.float32)

def train_model(X, y):
    Xs, info = _clean_reduce_X(X)
    svd_k = 100
    Z, svd = _reduce_svd(Xs, n_components=svd_k, random_state=42)
    br = fit_bayes_ridge(Z, y)
    payload = {"br": br, "info": info, "svd": svd}
    return payload

def predict_from_payload(payload, X_new):
    br = payload["br"]
    info = payload["info"]
    svd = payload["svd"]
    X_new_proc = _transform_new_X(X_new, info, svd=svd)
    y_pred, y_std = br.predict(X_new_proc, return_std=True)
    out = pd.DataFrame({"y_pred": y_pred.ravel()})
    if y_std is not None: out["y_std"] = np.asarray(y_std).ravel()
    return out

def bayesian_ridge_regression(X, y, percent):
    payload = train_model(X, y)
    X_abs = np.abs(X)
    mask = (~np.isnan(X_abs)) & (X_abs != 0)
    rmi = np.array([np.mean(X_abs[mask[:, i], i]) if np.any(mask[:, i]) else np.nan for i in range(X_abs.shape[1])])[np.newaxis, :]

    num = 20
    res = np.zeros([5, 20])
    for m in np.arange(len(percent)):
        pp = percent[m]
        nn = 0
        for nn in np.arange(num):
            n_cols = rmi.shape[1]
            n_neg = max(1, int(pp * n_cols))
            neg_idx = np.random.choice(n_cols, n_neg, replace=False)
            X_new = -rmi.copy()
            X_new[:, neg_idx] = -1 * X_new[:, neg_idx]
            preds_df = predict_from_payload(payload, X_new)
            res[m, nn] = preds_df.iloc[0][0]

    res = np.log10(res)
    col_means = np.nanmean(res, axis=0)
    mask = np.isnan(res)
    res[mask] = np.take(col_means, np.where(mask)[1])
    res = res[::-1, :]
    return res


def compare_burst_regulation(burst_info_pos, burst_info_neg, figsize):
    """
    Summarize positive and negative regulation effects on bursting metrics.

    Args:
        burst_info_pos (list): Regression summaries for positive regulation.
        burst_info_neg (list): Regression summaries for negative regulation.
    """
    plt.scatter_with_variance_plots(burst_info_pos, burst_info_neg, figsize)
    return
    

def compare_cv2_regulation(burst_info_pos, burst_info_neg, figsize):
    """
    Visualize how positive/negative regulation shapes CV²-related metrics.

    Args:
        burst_info_pos (list): Positive-regulation regression summaries.
        burst_info_neg (list): Negative-regulation regression summaries.
    """
    data_list = [burst_info_neg[4], burst_info_pos[4], burst_info_neg[5], burst_info_pos[5]]
    cmap1 = ["#9e9ac8", "#958fc3", "#8a83bd", "#817bb7", "#756bb1"]
    cmap2 = ["#a6d8a8", "#98cc9a", "#89bf8c", "#7bb27e", "#6ca670"]
    colors_list = [cmap1, cmap2, cmap1, cmap2]
    plt.bubble_boxplots4(data_list, colors_list, figsize)
    return


def compare_burst_overall_regulation(res_bursting, res_interaction, figsize):
    """
    Aggregate TF–TG interaction products per gene and relate them to bursting.

    This function collapses pairwise interactions into a single regulation
    score per gene, and then compares BF, BS, and CV² across regulation
    strength with custom violin/box plots.

    Args:
        res_bursting (np.ndarray): Bursting metrics per gene (including names).
        res_interaction (np.ndarray): Pairwise regulation results.
    """
    singlegene_interaction = np.row_stack([res_interaction[:, [0, 7, 9]], res_interaction[:, [1, 6, 8]]])
    singlegene_interaction[:, 1::] = np.nan_to_num(singlegene_interaction[:, 1::].astype(float), nan=0.0, posinf=0.0, neginf=0.0)

    genename = res_bursting[:, 0].astype(str)
    regulation = np.zeros([len(genename)])
    for n in np.arange(len(genename)):
        genename_idx = genename[n]
        idx = np.where(singlegene_interaction[:, 0] == genename_idx)[0]
        prod = singlegene_interaction[idx, 1].astype(float) * singlegene_interaction[idx, 2].astype(float)
        regulation[n] = np.nansum(prod)

    bf = np.log10(res_bursting[:, 4].astype(float))
    bs = np.log10(res_bursting[:, 5].astype(float))
    cv2 = np.log10(res_bursting[:, 7].astype(float))
    expressionlevel = bf + bs

    info = np.column_stack([expressionlevel, bf, bs, cv2, regulation])
    plt.violin_plots4_datastructure(info, figsize)
    return



def comparison_bursting_between_two_groups(bursting_dmso, bursting_idu, figsize):
    """
    Compare gene-level bursting features between DMSO and IdU conditions.

    Args:
        bursting_dmso (np.ndarray):
            Bursting metrics under DMSO control condition.
            Expected columns: [gene, BF, BS, CV2, ...].
        bursting_idu (np.ndarray):
            Bursting metrics under IdU treatment condition.

    Returns:
        A comparison figure is displayed using plt.box_plots4().
    """
    bursting_info_dmso = np.log10(bursting_dmso[:, 1::].astype(float))
    bursting_info_idu = np.log10(bursting_idu[:, 1::].astype(float))
    bursting_info_dmso = np.column_stack([bursting_info_dmso, bursting_info_dmso[:, 0] + bursting_info_dmso[:, 1]])
    bursting_info_idu = np.column_stack([bursting_info_idu, bursting_info_idu[:, 0] + bursting_info_idu[:, 1]])
    bf = [bursting_info_dmso[:, 0], bursting_info_idu[:, 0]]
    bs = [bursting_info_dmso[:, 1], bursting_info_idu[:, 1]]
    cv2 = [bursting_info_dmso[:, 2], bursting_info_idu[:, 2]]
    mean = [bursting_info_dmso[:, 3], bursting_info_idu[:, 3]]
    plt.box_plots4(bf, bs, cv2, mean, figsize)
    
    
    
def cluster_gene_ontology_enrichment_analysis(interactions_dmso, interactions_idu, genename, cr_genename, figsize):
    """
    Perform differential TF/TG regulation analysis and GO enrichment comparison between DMSO and IdU conditions.

    Args:
        interactions_dmso (np.ndarray):
            Pairwise TF–TG interaction matrix under DMSO condition.

        interactions_idu (np.ndarray):
            Pairwise TF–TG interaction matrix under IdU condition.

        genename (np.ndarray or list):
            List of gene names corresponding to the interaction matrices.

        cr_genename (np.ndarray or list):
            Known unwanted / cell-cycle–related genes to exclude before 
            computing differential TF regulation.

    Returns:
        Produces:
            - A clustered four-group GO Sankey diagram
            - GO bubble charts for TF-up, TF-down, TG-up, TG-down groups
    """
    tf_regulation_dmso = _overall_tf_regulation_compute(interactions_dmso, genename)
    tf_regulation_idu = _overall_tf_regulation_compute(interactions_idu, genename)
    tg_regulation_dmso = _overall_tg_regulation_compute(interactions_dmso, genename)
    tg_regulation_idu = _overall_tg_regulation_compute(interactions_idu, genename)
    degrees_dmso, degrees_dmso_sorted = _network_degrees_compute(interactions_dmso, genename)
    degrees_idu, degrees_idu_sorted = _network_degrees_compute(interactions_idu, genename)
    up_tf, down_tf = identify_differential_tf(degrees_dmso, tf_regulation_dmso, tf_regulation_idu, genename, cr_genename)
    up_tg, down_tg = identify_differential_tg(degrees_dmso, tg_regulation_dmso, tg_regulation_idu, genename)
    
    _cluster_go.go_sankey_clustered_groups(tf_up_genes=up_tf, tf_down_genes=down_tf, tg_up_genes=up_tg, tg_down_genes=down_tg,
                                           gene_sets="GO_Biological_Process_2021", organism="Mouse", top_n_each=8, top_n_terms_global=15)
    plt.go_differential_genes(up_tf, 'Greens_r', figsize)
    plt.go_differential_genes(down_tf, 'Purples_r', figsize)
    plt.go_differential_genes(up_tg, 'Reds_r', figsize)
    plt.go_differential_genes(down_tg, 'Blues_r', figsize)
    return



def _overall_tf_regulation_compute(res_interactions, genename):
    singlegene_interaction = np.row_stack([res_interactions[:, [0, 6, 8]], res_interactions[:, [1, 7, 9]]])
    singlegene_interaction[:, 1::] = np.nan_to_num(singlegene_interaction[:, 1::].astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    
    regulation = np.zeros([len(genename)])
    for n in np.arange(len(genename)):
        genename_idx = genename[n]
        idx = np.where(singlegene_interaction[:, 0] == genename_idx)[0]
        prod = singlegene_interaction[idx, 1].astype(float) * singlegene_interaction[idx, 2].astype(float)
        regulation[n] = np.nansum(prod)
    return regulation




def _overall_tg_regulation_compute(res_interactions, genename):
    singlegene_interaction = np.row_stack([res_interactions[:, [0, 7, 9]], res_interactions[:, [1, 6, 8]]])
    singlegene_interaction[:, 1::] = np.nan_to_num(singlegene_interaction[:, 1::].astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    
    regulation = np.zeros([len(genename)])
    for n in np.arange(len(genename)):
        genename_idx = genename[n]
        idx = np.where(singlegene_interaction[:, 0] == genename_idx)[0]
        prod = singlegene_interaction[idx, 1].astype(float) * singlegene_interaction[idx, 2].astype(float)
        regulation[n] = np.nansum(prod)
    return regulation



def _network_degrees_compute(res_interactions, genename):
    singlegene_interaction = np.row_stack([res_interactions[:, [0, 2, 3]], res_interactions[:, [1, 3, 2]]])
    singlegene_interaction[:, 1::] = np.nan_to_num(singlegene_interaction[:, 1::].astype(float), nan=0.0, posinf=0.0, neginf=0.0)
    
    degrees = np.zeros([len(genename), 3])
    for n in np.arange(len(genename)):
        genename_idx = genename[n]
        idx = np.where(singlegene_interaction[:, 0] == genename_idx)[0]
        idx_tf = np.where(singlegene_interaction[idx, 1].astype(float) == 1)[0]
        idx_tg = np.where(singlegene_interaction[idx, 2].astype(float) == 1)[0]
        degrees[n, 0] = len(idx_tf)
        degrees[n, 1] = len(idx_tg)
        degrees[n, 2] = len(idx_tf) - len(idx_tg)
    degrees = np.column_stack([genename, degrees])
    degrees_sorted = degrees[np.argsort(-degrees[:, 3].astype(float))]
    return degrees, degrees_sorted

    



def identify_differential_tf(degrees_dmso, tf_regulation_dmso, tf_regulation_idu, genename, cr_genename):
    idx = np.where(degrees_dmso[:, 3].astype(float) > 0)[0]
    tf_dmso = degrees_dmso[idx, 0].astype(str)

    idx1 = np.where(tf_regulation_dmso >= 30000000)[0]
    idx2 = np.where(tf_regulation_idu >= 30000000)[0]
    idx_union = np.union1d(idx1, idx2)

    tf_regulation_dmso_filtered = np.delete(tf_regulation_dmso, idx_union)
    tf_regulation_idu_filtered = np.delete(tf_regulation_idu, idx_union)
    tf_genename = np.delete(genename, idx_union)

    tf_interaction_level_dmso = (tf_regulation_dmso_filtered - np.mean(tf_regulation_dmso_filtered)) / np.std(tf_regulation_dmso_filtered)
    tf_interaction_level_idu = (tf_regulation_idu_filtered - np.mean(tf_regulation_idu_filtered)) / np.std(tf_regulation_idu_filtered)
    diff = tf_interaction_level_idu - tf_interaction_level_dmso

    tf_interaction_levels = np.column_stack([tf_genename, diff, tf_interaction_level_dmso, tf_interaction_level_idu])
    idx = np.where(np.isin(tf_interaction_levels[:, 0].astype(str), tf_dmso))[0]
    tf_interaction_levels = tf_interaction_levels[idx, :]

    cr = np.char.lower(cr_genename.astype(str))
    idx = np.where(np.isin(tf_interaction_levels[:, 0].astype(str), cr))[0]
    tf_interaction_levels = np.delete(tf_interaction_levels, idx, axis=0)
    tf_interaction_levels_sorted = tf_interaction_levels[np.argsort(-tf_interaction_levels[:, 1].astype(float))]
    tf_genename = tf_interaction_levels_sorted[:, 0].astype(str)
    return tf_genename[0: 27], tf_genename[28::]
    

def identify_differential_tg(degrees_dmso, tg_regulation_dmso, tg_regulation_idu, genename):
    idx = np.where(degrees_dmso[:, 3].astype(float) < 0)[0]
    tg_dmso = degrees_dmso[idx, 0].astype(str)

    idx1 = np.where(tg_regulation_dmso >= 3000000)[0]
    idx2 = np.where(tg_regulation_idu >= 3000000)[0]
    idx_union = np.union1d(idx1, idx2)

    tg_regulation_dmso_filtered = np.delete(tg_regulation_dmso, idx_union)
    tg_regulation_idu_filtered = np.delete(tg_regulation_idu, idx_union)
    tg_genename = np.delete(genename, idx_union)

    tg_interaction_level_dmso = (tg_regulation_dmso_filtered - np.mean(tg_regulation_dmso_filtered)) / np.std(tg_regulation_dmso_filtered)
    tg_interaction_level_idu = (tg_regulation_idu_filtered - np.mean(tg_regulation_idu_filtered)) / np.std(tg_regulation_idu_filtered)
    diff = tg_interaction_level_idu - tg_interaction_level_dmso

    tg_interaction_levels = np.column_stack([tg_genename, diff, tg_interaction_level_dmso, tg_interaction_level_idu])
    idx = np.where(np.isin(tg_interaction_levels[:, 0].astype(str), tg_dmso))[0]
    tg_interaction_levels = tg_interaction_levels[idx, :]

    tg_interaction_levels_sorted = tg_interaction_levels[np.argsort(-tg_interaction_levels[:, 1].astype(float))]
    
    idx = np.where(tg_interaction_levels_sorted[:, 1].astype(float) >= 0)[0]
    up_tg_interaction_levels = tg_interaction_levels_sorted[idx, :]
    idx = np.where(up_tg_interaction_levels[:, 1].astype(float) >= np.median(up_tg_interaction_levels[:, 1].astype(float)))[0]
    up_tg = up_tg_interaction_levels[idx, 0].astype(str)
    
    idx = np.where(tg_interaction_levels_sorted[:, 1].astype(float) <= 0)[0]
    down_tg_interaction_levels = tg_interaction_levels_sorted[idx, :]
    idx = np.where(np.abs(down_tg_interaction_levels[:, 1].astype(float)) >= np.median(np.abs(down_tg_interaction_levels[:, 1].astype(float))))[0]
    down_tg = down_tg_interaction_levels[idx, 0].astype(str)
    return up_tg, down_tg
    
