import os
import shutil
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy import stats
from scipy.stats import spearmanr
from scipy.optimize import minimize
from sklearn.metrics import mutual_info_score
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
from matplotlib import cm

from .._utils import _probability_core as pc



def burst_link(grn_info, rnaseq_data, tau, tol, rho, r, max_iter, n_jobs, TAU, return_plots, log_path, return_res):
    """
    Perform main pipeline of BurstLink
    
    Args:
        grn_info (pd.DataFrame): Gene-gene interaction table, each row = (gene1, gene2, sign12, sign21).
        rnaseq_data (pd.DataFrame): Raw RNA-seq count matrix, first column = gene id, following columns = cells.
        tau (float): Global normalization constant for scaling τ_i values.
        tol (float): ADMM convergence tolerance.
        rho (float): ADMM penalty parameter.
        r (float): ADMM augmentation parameter.
        max_iter (int): Maximum ADMM iterations.
        n_jobs (int): Number of parallel workers (Joblib Loky backend).
        TAU (bool): Whether to estimate cell-specific capture efficiency π_i.
        return_plots (bool): Whether to output diagnostic plots for gene-pair inference.
        log_path (str): Directory for logs / plots / iteration history.
        return_res (bool): Whether to return intermediate results.

    Returns:
        tuple:
            res_bursting: Per-gene burst frequency & burst size estimates.
            res_regulation: Per-gene-pair regulation type & strength inference.
    """
    os.makedirs(log_path, exist_ok=True)
    for root, dirs, files in os.walk(log_path):
        for f in files: os.remove(os.path.join(root, f))
        for d in dirs: shutil.rmtree(os.path.join(root, d))
    genename, singlegene_count_storage, genepair_count_storage = count_preprocessing(grn_info, rnaseq_data, tau, n_jobs, TAU)
    res_bursting = admm_optimizer(genename, singlegene_count_storage, genepair_count_storage, rho, r, tol, n_jobs, max_iter, log_path, return_res)
    res_regulation = genepair_interactions_inference(genepair_count_storage, n_jobs, return_plots, log_path, return_res)
    return res_bursting, res_regulation


def count_preprocessing(grn_info, rnaseq_data, tau, n_jobs, TAU):
    """
    Wrapper to preprocess data before BurstLink inference.
    
    Returns:
        genename (np.ndarray)
        singlegene_count_storage (list)
        genepair_count_storage (list)
    """
    genename, counts, pi = estimate_pai_hat(rnaseq_data, tau, (0.01, 0.99), 1e-6, TAU)
    singlegene_count_storage = singlegene_count_preprocessing(counts, pi)
    genepair_count_storage = genepair_count_preprocessing(grn_info, genename, counts, pi, n_jobs)
    return genename, singlegene_count_storage, genepair_count_storage


def estimate_pai_hat(rnaseq_data, tau, winsorize_T_quantiles, clip_min_pi, TAU):
    """
    Estimate per-cell capture efficiency π_i.

    Args:
        rnaseq_data: RNA-seq dataframe
        tau: Scalar multiplier
        winsorize_T_quantiles: (low, high) quantiles for clipping T_i
        clip_min_pi: Lower bound for π_i
        TAU: Whether to estimate π_i

    Returns:
        genename, counts, pi
    """
    genename = rnaseq_data.iloc[:, 1].to_numpy() 
    counts = rnaseq_data.iloc[:, 2:].to_numpy(dtype=float)
    if TAU == True:
        T = np.nansum(counts, axis=0)
        q_low, q_high = winsorize_T_quantiles
        q_low = max(0.0, min(1.0, float(q_low)))
        q_high = max(0.0, min(1.0, float(q_high)))
        lo = np.nanquantile(T, q_low)
        hi = np.nanquantile(T, q_high)
        T_used = np.clip(T, lo, hi)
        T_bar = np.nanmean(T_used)
        hat_pi = (T_used / T_bar) * tau
        hat_pi = np.clip(hat_pi, clip_min_pi, np.inf)
        a_vec = hat_pi / np.nanmean(hat_pi)
    else: a_vec = np.ones(counts.shape[1])
    return genename, counts, a_vec
       

def singlegene_count_preprocessing(counts, pi):
    """
    Produce non-NaN count vector across cells and matched π_i values for each gene.
    
    Returns:
        list of [counts_i, pi_i] for each gene
    """
    
    countdata = []
    for idx in tqdm(range(counts.shape[0]), desc='Single-gene countdata preprocessing'):
        counts_idx = counts[idx, :]
        count_data_idx = counts_idx[~np.isnan(counts_idx)]
        pi_idx = pi[~np.isnan(counts_idx)]
        countdata.append([count_data_idx, pi_idx])
    return countdata

    
def genepair_count_preprocessing(grn_info, genename, counts, pi, n_jobs):
    """
    Preprocess all gene pairs Parallelly.
    Each pair returns:
        [pair_name, regulation_info, 2×N count matrix, π_i values]

    Returns:
        list, length = number of gene pairs
    """
    genepair_count_storage = Parallel(n_jobs=n_jobs, backend="loky", verbose=5)(delayed(
        single_genepair_count_preprocessing)(m, grn_info, genename, counts, pi) for m in range(len(grn_info)))
    return genepair_count_storage


def single_genepair_count_preprocessing(m, grn_info, genename, counts, pi):
    """
    Preprocess a single gene-pair count data

    Returns:
        [genepair_name, regulation_info, 2×M truncated counts, π_i for retained cells]
    """
    genepair_name = grn_info.iloc[m, 0: 2].to_numpy()
    regulation_info = grn_info.iloc[m, 2: 4].astype(int).to_numpy()
    idx1 = np.where(genename == genepair_name[0])[0][0]
    idx2 = np.where(genename == genepair_name[1])[0][0]
    genepair_count = counts[np.array([idx1, idx2]), :]
    mask = ~np.isnan(genepair_count).any(axis=0)
    genepair_count_idx = genepair_count[:, mask]
    pi_idx = pi[mask]
    genepair_count_idx_kpet, pre_truncation_idx = pre_truncation(genepair_count_idx)
    pi_idx_kpet = pi_idx[pre_truncation_idx]
    return [genepair_name, regulation_info, genepair_count_idx_kpet, pi_idx_kpet]


def pre_truncation(vals, iqr_factor=3.0, num=150):
    vals = np.asarray(vals, dtype=float)
    finite_mask = np.all(np.isfinite(vals), axis=0)
    v = vals[:, finite_mask]
    idx_keep = np.where(finite_mask)[0]

    if v.shape[1] <= num: return v, idx_keep
    u = np.log1p(v)
    lo1, hi1 = compute_bounds_upper(u[0, :], iqr_factor)
    lo2, hi2 = compute_bounds_upper(u[1, :], iqr_factor)
    
    keep = (u[0, :] >= lo1) & (u[0, :] <= hi1) & \
           (u[1, :] >= lo2) & (u[1, :] <= hi2)

    v2 = v[:, keep]
    idx_keep2 = idx_keep[keep]
    if v2.shape[1] <= num: return v2, idx_keep2
    return v2, idx_keep2

def compute_bounds_upper(x, iqr_factor):
    x = np.asarray(x, dtype=float)
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    if iqr <= 0:
        lo = x.min()
        hi = x.max()
    else:
        lo = x.min()
        hi = q3 + iqr_factor * iqr
    return lo, hi


def admm_optimizer(genename, singlegene_count_storage, genepair_count_storage, rho, r, tol, n_jobs, max_iter, log_path, return_res):
    """
    Perform ADMM optimization for genome-wide burst parameter inference.

    Args:
        genename (np.ndarray): Array of gene names.
        singlegene_count_storage (list): Per-gene count and pi storage.
        genepair_count_storage (list): Per-gene-pair count and pi storage.
        rho (float): ADMM penalty parameter for local updates.
        r (float): Relaxation parameter for consensus updates.
        tol (float): Convergence tolerance.
        n_jobs (int): Number of parallel workers.
        max_iter (int): Maximum number of ADMM iterations.
        log_path (str): Directory for reading/writing intermediate TSVs.
        return_res (bool): Whether to return full results from burst_info.

    Returns:
        Any: Result object returned by burst_info (e.g. per-gene bursting summary).
    """
    z, u, scalers = admm_initialization(singlegene_count_storage, genepair_count_storage, genename, tol, r, n_jobs, log_path) 
    if len(genepair_count_storage) > 1:
        genepair_count_storage, genepair_params = cleaning_genepair_count_storage(genepair_count_storage, 0, log_path)
        
        for iteration in range(1, max_iter + 1):
            parallel_genepair_burst_admm(genepair_count_storage, genepair_params, z, u, rho, tol, n_jobs, iteration, log_path, scalers)
            z, z_prev, u, scalers = consensus_dual_update(z, u, r, iteration, log_path)
            genepair_count_storage, genepair_params = cleaning_genepair_count_storage(genepair_count_storage, iteration, log_path)
            converged, r_norm, s_norm = admm_convergence_test(genepair_count_storage, genepair_params, z, z_prev, u, rho, iteration, scalers, log_path)
            if converged: break
            rho_old = rho
            rho = adapt_rho(rho, r_norm, s_norm)
            if rho != rho_old: u[:, 2:] = (rho_old / rho) * u[:, 2:].astype(float)
            
    res = burst_info(singlegene_count_storage, genename, z, log_path, return_res)  
    return res

def admm_initialization(singlegene_count_storage, genepair_count_storage, genename, tol, r, n_jobs, log_path):
    """
    Initialize ADMM variables using univariate and bivariate MLEs.

    Args:
        singlegene_count_storage (list): Per-gene (counts, pi) storage.
        genepair_count_storage (list): Per-gene-pair storage.
        genename (np.ndarray): Array of gene names.
        tol (float): Tolerance passed to bivariate initialization optimization.
        r (float): Relaxation parameter for consensus update.
        n_jobs (int): Number of parallel workers.
        log_path (str): Directory to save initial TSVs.

    Returns:
        tuple: (z, u, scalers) for ADMM iterations.
    """
    singlegene_inference(genename, singlegene_count_storage, n_jobs, log_path)
    gene_params = pd.read_csv(log_path + '/' + 'gene_inference_params0.tsv', sep='\t').to_numpy()
    w_params = w_initialization(genepair_count_storage, gene_params)

    parallel_single_genegpair_ini(genepair_count_storage, gene_params, w_params, tol, n_jobs, log_path)
    genepair_params = pd.read_csv(log_path + '/' + 'genepair_inference_params0.tsv', sep='\t').to_numpy()
    
    z0 = gene_params[:, 0: 4]
    u0 = np.zeros([len(genepair_params), 6])
    u0 = np.column_stack([genepair_params[:, 0: 2], u0])
    z, _, u, scalers = consensus_dual_update(z0, u0, r, 0, log_path)
    return z, u, scalers


def singlegene_inference(genename, singlegene_count_storage, n_jobs, log_path):
    """
    Run univariate MLE for each gene independently.

    Args:
        genename (np.ndarray): Array of gene names.
        singlegene_count_storage (list): Per-gene (counts, pi) tuples.
        n_jobs (int): Number of parallel workers.
        log_path (str): Directory to store the TSV result.
    """
    uni_mle_res = Parallel(n_jobs=n_jobs, backend='loky', verbose=5)(delayed(
        uni_maximum_likelihood)(idx, singlegene_count_storage_idx) for idx, singlegene_count_storage_idx in enumerate(singlegene_count_storage))
    records = []
    for idx, res, con_ in uni_mle_res:
        alpha, beta, phi = res
        records.append((genename[idx], alpha, beta, phi, con_))
    df_res = pd.DataFrame(records, columns=['genename', 'alpha_est', 'beta_est', 'phi_est', 'conv'])
    tsv_path = os.path.join(log_path, 'gene_inference_params0.tsv')
    df_res.to_csv(tsv_path, sep="\t", index=False, float_format="%.6g")
    return

        
def uni_maximum_likelihood(idx, singlegene_count_storage_idx):
    """
    Perform maximum likelihood estimation for a single gene.

    Args:
        idx (int): Index of the gene.
        singlegene_count_storage_idx (tuple): (counts, pi) for this gene.

    Returns:
        tuple: (idx, params, conv_flag) where params = [alpha, beta, phi],
               conv_flag = 1 if successfully converged within bounds, else 0.
    """
    eps = 1e-8
    vals, pi = singlegene_count_storage_idx
    x0 = uni_moment_inference(vals, pi, eps)
    bnds = ((1e-3, 1e3), (1e-3, 1e3), (1, 1e4))
    try: 
        ll = minimize(uni_loglikelihood, x0, args=(vals, pi), method='L-BFGS-B', bounds=bnds)
        if ll.success: res = ll.x
        else: res = np.array([np.nan, np.nan, np.nan])
    except: res = np.array([np.nan, np.nan, np.nan])
    if np.any(np.isnan(res)) or violates_bounds_uni(res, bnds): return idx, res, 0
    else: return idx, res, 1


def uni_moment_inference(vals, pi, eps):
    """
    Estimate initial univariate Poisson-Beta parameters via moments.

    Args:
        vals (np.ndarray): Raw counts for a gene across cells.
        pi (np.ndarray): Cell-specific normalization factors.
        eps (float): Small value to avoid division by zero.

    Returns:
        np.ndarray: Initial estimates [alpha, beta, phi].
    """
    vals = vals / pi
    m1 = float(np.mean(vals)) + eps
    m2 = float(np.mean(vals * (vals - 1))) + eps
    m3 = float(np.mean(vals * (vals - 1) * (vals - 2))) + eps
    r1, r2, r3 = m1, m2 / m1, m3 / m2
    denom1 = r1 * r2 - 2 * r1 * r3 + r2 * r3
    denom2 = r1 - 2 * r2 + r3
    if abs(denom1) < eps or abs(denom2) < eps:
        return np.array([1.0, 1.0, 10.0])
    alpha_est = (2 * r1 * (r3 - r2)) / denom1
    beta_est = (2 * (r3 - r2) * (r1 - r3) * (r2 - r1)) / (denom1 * denom2)
    phi_est = (2 * r1 * r3 - r1 * r2 - r2 * r3) / denom2
    return np.array([max(alpha_est, eps), max(beta_est, eps), max(phi_est, 1.0)])


def uni_loglikelihood(params, vals, pi):
    """
    Compute negative log-likelihood for the univariate Poisson-Beta model.

    Args:
        params (array-like): [alpha, beta, phi] parameters.
        vals (np.ndarray): Counts for one gene across cells.
        pi (np.ndarray): Cell-specific normalization factors.

    Returns:
        float: Negative log-likelihood value (to be minimized).
    """
    alpha, beta, phi = params
    if (alpha <= 0) or (beta <= 0) or (phi <= 0): return 1e50
    prob = pc.uni_poissonbeta_pmf(vals, alpha, beta, phi, pi, 50)
    ll = -np.sum(np.log(prob))
    return ll


def violates_bounds_uni(params, bounds):
    return any(np.isclose(p, b[0]) or np.isclose(p, b[1]) for p, b in zip(params, bounds))

def w_initialization(genepair_count_storage, gene_params):
    w_params = np.zeros(len(genepair_count_storage)) 
    return w_params

def parallel_single_genegpair_ini(genepair_count_storage, gene_params, w_params, tol, n_jobs, log_path):
    tsv_path = os.path.join(log_path, 'genepair_inference_params0.tsv')
    cols = ['gene1', 'gene2', 'alpha1', 'alpha2', 'beta1', 'beta2', 'phi1', 'phi2', 'w', 'conv']
    if not os.path.exists(tsv_path):
        pd.DataFrame(columns=cols).to_csv(tsv_path, sep='\t', index=False)
    rows = Parallel(n_jobs=n_jobs, backend='loky', verbose=5)(delayed(single_genegpair_inference_ini)(
        m, genepair_count_storage[m], gene_params, w_params, tol) for m in range(len(genepair_count_storage)))
    
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(tsv_path, sep='\t', mode='a', header=False, index=False, float_format='%.6g')
    return

    
def single_genegpair_inference_ini(m, genepair_count_storage_m, gene_params, w_params, tol):
    genepair_name, _, counts, pi = genepair_count_storage_m
    idx1 = np.where(gene_params[:, 0] == genepair_name[0])[0]
    idx2 = np.where(gene_params[:, 0] == genepair_name[1])[0]
    idx = [idx1[0], idx2[0]]
    params0 = np.concatenate((np.ravel(gene_params[idx, 1]).astype(float), np.ravel(gene_params[idx, 2]).astype(float), np.ravel(gene_params[idx, 3]).astype(float), [float(w_params[m])]))
    res = genepair_burst_inference_ini(counts, pi, params0, tol)
    row = genepair_name.tolist() + res.tolist()
    return row



def genepair_burst_inference_ini(counts, pi, params0, tol):
    """
    Run constrained bivariate Poisson-Beta MLE for one gene pair.

    Args:
        counts (np.ndarray): 2×N count matrix for the gene pair.
        pi (np.ndarray): Cell-specific normalization factors.
        params0 (np.ndarray): Initial parameter vector (length 7).
        tol (float): Tolerance for the SLSQP optimizer.

    Returns:
        np.ndarray: [alpha1, alpha2, beta1, beta2, phi1, phi2, w, conv_flag]
    """
    bnds = ((1e-4, 1e3),)*4 + ((0, 1e4),)*2 + ((-1e3, 1e3),)
    cons = [{'type': 'ineq', 'fun': constraint1}, {'type': 'ineq', 'fun': constraint2}]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            options = {'maxiter': 50, 'ftol': tol, 'disp': False}
            ll = minimize(bivariate_log_likelihood, params0, args = (counts, pi), method = 'SLSQP', constraints = cons, bounds = bnds, options = options)
        if ll.success and np.all(np.isfinite(ll.x)): res = np.hstack([ll.x[0: 7], 1.0])
        else: res = np.hstack([params0, 0.0])
    except Exception: res = np.hstack([params0, 0.0])
    return res



def bivariate_log_likelihood(params, vals, pi):
    """
    Compute negative log-likelihood for the bivariate Poisson-Beta model.

    Args:
        params (array-like): [alpha1, alpha2, beta1, beta2, phi1, phi2, w].
        vals (np.ndarray): 2×N count matrix.
        pi (np.ndarray): Cell-specific normalization factors.

    Returns:
        float: Negative log-likelihood (to be minimized).
    """
    eps=1e-12
    alpha1, alpha2, beta1, beta2, phi1, phi2, w = map(float, params)
    if min(alpha1, alpha2, beta1, beta2, phi1, phi2) <= 0 or not np.isfinite(w): return 1e50
    p1  = pc.uni_poissonbeta_pmf(vals[0, :], alpha1,      beta1, phi1, pi, 50)
    p2  = pc.uni_poissonbeta_pmf(vals[1, :], alpha2,      beta2, phi2, pi, 50)
    p1p = pc.uni_poissonbeta_pmf(vals[0, :], alpha1 + 1., beta1, phi1, pi, 50)
    p2p = pc.uni_poissonbeta_pmf(vals[1, :], alpha2 + 1., beta2, phi2, pi, 50)
    denom1 = alpha1 + beta1
    denom2 = alpha2 + beta2
    if denom1 <= 0 or denom2 <= 0: return 1e50
    mu1 = alpha1 / denom1
    mu2 = alpha2 / denom2
    a_coef = np.clip(w, -0.99, 0.99) * mu1 * mu2
    joint = p1 * p2 + a_coef * (p1p - p1) * (p2p - p2)
    prob  = np.clip(joint, eps, 1.0)
    return -np.sum(np.log(prob))


def constraint1(params):
    return (params[0] + params[2]) * (params[1] + params[3]) / max(params[0] * params[3], params[1] * params[2]) - params[6]


def constraint2(params):
    return (params[0] + params[2]) * (params[1] + params[3]) / max(params[0] * params[1], params[2] * params[3]) + params[6]


def consensus_dual_update(z0, u0, r, iteration, log_path):
    """
    Perform global consensus and dual updates for ADMM.

    Args:
        z0 (np.ndarray): Previous global parameters [gene, alpha, beta, phi].
        u0 (np.ndarray): Previous dual variables with leading gene labels.
        r (float): Relaxation parameter.
        iteration (int): ADMM iteration index (used to read TSV files).
        log_path (str): Directory containing genepair_inference_params files.

    Returns:
        tuple: (z, z_prev, u, scalers) updated for next ADMM iteration.
    """
    genepair_params__ = pd.read_csv(log_path + '/' + f'genepair_inference_params{iteration}.tsv', sep='\t').to_numpy()
    repeated_gene_params, genepair_params = filtering_local_params(genepair_params__, iteration, log_path)
    z, z_prev, z_hat = consensus_cluster(repeated_gene_params, z0, r, 1.5)
    scalers = compute_global_scalers(genepair_params)
    u = dual_compute(u0, z_hat, genepair_params, scalers)
    return z, z_prev, u, scalers


def filtering_local_params(genepair_params, iteration, log_path):
    genepair_params_ = genepair_params[genepair_params[:, -1] != 0]
    indices = []
    for idx in np.arange(4):
        indices_ = np.where(genepair_params_[:, idx + 2].astype(float) == 1e-3)[0]
        indices__ = np.where(genepair_params_[:, idx + 2].astype(float) == 1e3)[0]
        indices = list(set(indices) | set(indices_) | set(indices__))
    for idx in np.arange(2):
        indices_ = np.where(genepair_params_[:, idx + 6].astype(float) == 1.0)[0]
        indices__ = np.where(genepair_params_[:, idx + 6].astype(float) > 1e3)[0]
        indices = list(set(indices) | set(indices_) | set(indices__))
    filtered_genepair_params = np.delete(genepair_params_, indices, axis = 0)
    
    gene_params = np.vstack([filtered_genepair_params[:, [0, 2, 4, 6]], filtered_genepair_params[:, [1, 3, 5, 7]]])
    sorted_gene_params = gene_params[np.argsort(gene_params[:, 0].astype(str))]
    
    df_res = pd.DataFrame(filtered_genepair_params, columns=['gene1', 'gene2', 'alpha1', 'alpha2', 'beta1', 'beta2', 'phi1', 'phi2', 'w', 'conv'])
    df_sorted_res = df_res.sort_values(by=['gene1', 'gene2'], ascending=[True, True]).reset_index(drop=True)
    tsv_path = os.path.join(log_path, f'genepair_inference_params_f{iteration}.tsv')
    df_sorted_res.to_csv(tsv_path, sep="\t", index=False, float_format="%.6g")
    sorted_genepair_params = df_sorted_res.to_numpy()
    return sorted_gene_params, sorted_genepair_params


def consensus_cluster(repeated_gene_params, z0, r, alpha_over):
    """
    Build consensus per-gene parameters from repeated local estimates.

    Args:
        repeated_gene_params (np.ndarray): Stacked [gene, alpha, beta, phi].
        z0 (np.ndarray): Previous global parameters [gene, alpha, beta, phi].
        r (float): Relaxation parameter.
        alpha_over (float): Over-relaxation coefficient.

    Returns:
        tuple: (z, z_prev, z_hat) where each is [gene, alpha, beta, phi].
    """
    _, unique_indices = np.unique(repeated_gene_params[:, 0], return_index=True)
    genename = repeated_gene_params[:, 0][np.sort(unique_indices)]
    z_iter = np.zeros([len(genename), 3])
    for idx in np.arange(len(genename)):
        genename_idx = genename[idx]
        n = np.where(repeated_gene_params[:, 0] == genename_idx)[0]
        if len(n) == 1:
            for nn in np.arange(3): z_iter[idx, nn] = repeated_gene_params[n[0], nn+1]
        elif len(n) > 1:
            for nn in np.arange(3): z_iter[idx, nn] = robust_trimmed_mean(repeated_gene_params[n, nn+1], 2.0)
            
    z0_map = {g: i for i, g in enumerate(z0[:, 0])}
    take = [z0_map[g] for g in genename]
    z_prev_core = z0[np.array(take, dtype=int), 1:].astype(float)
    
    z_core = (1 - r) * z_prev_core + r * z_iter
    z = np.column_stack([genename, z_core])
    z_prev = np.column_stack([genename, z_prev_core])
    z_hat = np.column_stack([z[:,0], alpha_over * z[:,1] + (1 - alpha_over) * z_prev[:,1],
                             alpha_over * z[:,2] + (1 - alpha_over) * z_prev[:,2],
                             alpha_over * z[:,3] + (1 - alpha_over) * z_prev[:,3]])
    return z, z_prev, z_hat
    

def robust_trimmed_mean(x, zcut):
    x = np.asarray(x, dtype=float).ravel()
    med = np.median(x)
    mad = stats.median_abs_deviation(x, scale='normal')
    if mad == 0 or not np.isfinite(mad): return float(np.mean(x))
    z = np.abs((x - med) / mad)
    m = z < zcut
    return float(np.mean(x[m])) if np.any(m) else float(np.mean(x))


def dual_compute(u0, z, genepair_params, scalers):
    """
    Update dual variables for each gene pair based on consensus parameters.

    Args:
        u0 (np.ndarray): Previous dual variables with gene labels.
        z (np.ndarray): Over-relaxed global parameters [gene, alpha, beta, phi].
        genepair_params (np.ndarray): Per-pair parameters after filtering.
        scalers (tuple): (mu, sigma) used for scaling/unscaling.

    Returns:
        np.ndarray: Updated dual variables with leading gene labels.
    """
    u = np.zeros([genepair_params.shape[0], 6])
    for m in range(genepair_params.shape[0]):
        genename1, genename2 = genepair_params[m, 0: 2]
        z_tilde_idx = _pair_z_tilde((genename1, genename2), z, scalers)
        
        lam6_idx = genepair_params[m, 2: 8].astype(float)
        lam_tilde_idx = _tilde_from_lambda6(lam6_idx, scalers)

        idx1 = np.where(u0[:, 0] == genename1)[0]
        idx2 = np.where(u0[:, 1] == genename2)[0]
        common_idx = np.intersect1d(idx1, idx2)[0]
        u[m, :] = u0[common_idx, 2::] + (lam_tilde_idx - z_tilde_idx)
    u = np.column_stack([genepair_params[:, 0: 2], u])
    return u


def compute_global_scalers(genepair_params):
    """
    Compute global scaling statistics for pairwise parameters.
    
    Args:
        genepair_params (np.ndarray): Per-pair parameters.

    Returns:
        tuple: (mu, sigma) where both are 1D arrays of length 6.
    """
    X = np.log(np.clip(genepair_params[:, 2:8].astype(float), 1e-12, None))
    mu = np.nanmedian(X, axis=0)
    sigma = np.nanstd(X, axis=0)
    sigma = np.clip(sigma, 1e-3, None)
    return mu, sigma    


def cleaning_genepair_count_storage(genepair_count_storage, iteration, log_path):
    genepair_params = pd.read_csv(log_path + '/' + f'genepair_inference_params_f{iteration}.tsv', sep='\t').to_numpy()
    genepair_count_storage_new = []
    for m in np.arange(len(genepair_count_storage)):
        genepair_name, _, _, _ = genepair_count_storage[m]
        genename1, genename2 = genepair_name
        idx1 = np.where(genepair_params[:, 0] == genename1)[0]
        idx2 = np.where(genepair_params[:, 1] == genename2)[0]
        common_idx = np.intersect1d(idx1, idx2)
        if len(common_idx) == 1: genepair_count_storage_new.append(genepair_count_storage[m])
    return genepair_count_storage_new, genepair_params[:, :-1]
            

def parallel_genepair_burst_admm(genepair_count_storage, genepair_params, z, u, rho, tol, n_jobs, iteration, log_path, scalers):
    """
    Run ADMM local updates for all gene pairs in parallel.

    Args:
        genepair_count_storage (list): List of per-pair (names, regs, counts, pi).
        genepair_params (np.ndarray): Current per-pair parameters.
        z (np.ndarray): Global consensus parameters [gene, alpha, beta, phi].
        u (np.ndarray): Dual variables with leading gene labels.
        rho (float): ADMM penalty parameter.
        tol (float): Tolerance for SLSQP optimizer.
        n_jobs (int): Number of parallel workers.
        iteration (int): ADMM iteration index.
        log_path (str): Directory for output TSV files.
        scalers (tuple): (mu, sigma) scaling statistics.
    """
    tsv_path = os.path.join(log_path, f'genepair_inference_params{iteration}.tsv')
    cols = ['gene1', 'gene2', 'alpha1', 'alpha2', 'beta1', 'beta2', 'phi1', 'phi2', 'w', 'conv']
    if not os.path.exists(tsv_path): 
        pd.DataFrame(columns=cols).to_csv(tsv_path, sep='\t', index=False)
    
    n_pairs = len(genepair_count_storage)
    batch_size = 5000
    for start in range(0, n_pairs, batch_size):
        end = min(start + batch_size, n_pairs)
        batch = genepair_count_storage[start: end]
        rows = Parallel(n_jobs=n_jobs, backend="loky", verbose=5)(delayed(single_genepair_burst_admm)(
            genepair_count_storage_item, genepair_params, z, u, rho, tol, scalers) for genepair_count_storage_item in batch)
        df_batch = pd.DataFrame(rows, columns=cols)
        df_batch.to_csv(tsv_path, sep='\t', mode='a', header=False, index=False, float_format='%.6g')
    return



def single_genepair_burst_admm(genepair_count_storage_item, genepair_params, z, u, rho, tol, scalers):
    """
    Optimize a single gene-pair local ADMM subproblem via constrained SLSQP.

    Args:
        genepair_count_storage_item (list): One entry from genepair_count_storage.
        genepair_params (np.ndarray): Current per-pair parameter array.
        z (np.ndarray): Global consensus parameters.
        u (np.ndarray): Dual variables.
        rho (float): ADMM penalty parameter.
        tol (float): Tolerance for SLSQP.
        scalers (tuple): (mu, sigma) scaling statistics.

    Returns:
        list: Row [gene1, gene2, alpha1, alpha2, beta1, beta2, phi1, phi2, w, conv].
    """
    genepair_name, _, counts, pi = genepair_count_storage_item
    lamda0, tilde_zm, um = _build_params(genepair_name, genepair_params, z, u, scalers)
    bnds = ((1e-4, 1e3),) * 4 + ((1e-6, 1e3),) * 2 + ((-1e3, 1e3),)
    cons = [{'type': 'ineq', 'fun': constraint1}, {'type': 'ineq', 'fun': constraint2}]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            options = {'maxiter': 150, 'ftol': float(tol), 'disp': False}
            obj = lambda lam: loss_admm(lam, counts, pi, tilde_zm, um, rho, scalers)
            ll = minimize(obj, lamda0, method='SLSQP',
                          constraints=cons, bounds=bnds, options=options)
        if ll.success and np.all(np.isfinite(ll.x)): res = np.hstack([ll.x[0: 7], 1.0]) 
        else: res = np.hstack([lamda0, 0.0])     
    except Exception: res = np.hstack([lamda0, 0.0])
    res_row = genepair_name.tolist() + res.tolist()
    return res_row


def _build_params(genepair_name, genepair_params, z, u, scalers):
    genename1, genename2 = genepair_name
    idx1 = np.where(genepair_params[:, 0] == genename1)[0]
    idx2 = np.where(genepair_params[:, 1] == genename2)[0]
    idx = np.intersect1d(idx1, idx2)[0]
    params0 = genepair_params[idx, 2: 9]
    u_idx = u[idx, 2::]
    
    idx1 = np.where(z[:, 0] == genename1)[0]
    idx2 = np.where(z[:, 0] == genename2)[0]
    idx = [idx1[0], idx2[0]]
    z_idx = np.concatenate((np.ravel(z[idx, 1]).astype(float), np.ravel(z[idx, 2]).astype(float), np.ravel(z[idx, 3]).astype(float)))
    tilde_z_idx = _tilde_from_lambda6(z_idx, scalers)
    return params0, tilde_z_idx, u_idx


def _tilde_from_lambda6(lam6, scalers):
    x = np.log(np.clip(np.asarray(lam6, dtype=float), 1e-12, None))
    mu, sigma = scalers
    return (x - mu) / sigma


def loss_admm(lamda, data, pi, z_tilde, u_tilde, rho, scalers):
    """
    Evaluate ADMM augmented objective (negative log-likelihood + penalty).

    Args:
        lamda (np.ndarray): Parameter vector (length 7).
        data (np.ndarray): 2×N count matrix.
        pi (np.ndarray): Cell-specific scaling factors.
        z_tilde (np.ndarray): Standardized consensus vector (length 6).
        u_tilde (np.ndarray): Dual vector (length 6).
        rho (float): ADMM penalty parameter.
        scalers (tuple): (mu, sigma) for scaling.

    Returns:
        float: Augmented objective value.
    """
    neglikelihood = bivariate_log_likelihood(lamda, data, pi)
    tilde_lambda = _tilde_from_lambda6(lamda[:6], scalers)
    diff = tilde_lambda - z_tilde + u_tilde
    lagrangian = 0.5 * rho * float(np.dot(diff, diff))
    return neglikelihood + lagrangian


def admm_convergence_test(genepair_count_storage, genepair_params, z, z_prev, u, rho, iteration, scalers, log_path):
    """
    Check ADMM convergence using primal/dual residuals and log progress.

    Args:
        genepair_count_storage (list): Per-pair (names, regs, counts, pi).
        genepair_params (np.ndarray): Current per-pair parameters.
        z (np.ndarray): Current global parameters.
        z_prev (np.ndarray): Previous global parameters.
        u (np.ndarray): Dual variables.
        rho (float): ADMM penalty parameter.
        iteration (int): Iteration index.
        scalers (tuple): (mu, sigma) scaling statistics.
        log_path (str): Directory for convergence log TSV.

    Returns:
        tuple: (converged, r_rms, s_rms).
    """
    r2_sum = 0.0; s2_sum = 0.0
    lam_norm_acc = 0.0; z_norm_acc = 0.0; total_loss = 0.0
    used_pairs_r = 0; used_pairs_s = 0

    for m in range(len(genepair_count_storage)):
        genepair_name, _, counts, pi = genepair_count_storage[m]

        i1 = np.where(genepair_params[:, 0] == genepair_name[0])[0]
        i2 = np.where(genepair_params[:, 1] == genepair_name[1])[0]
        idx = np.intersect1d(i1, i2)[0]
       
        lam6 = genepair_params[idx, 2: 8].astype(float)
        lam_tilde = _tilde_from_lambda6(lam6, scalers)
        lam_norm_acc += float(np.dot(lam_tilde, lam_tilde))

        z_tilde_now = _pair_z_tilde(genepair_name, z, scalers)
        diff = lam_tilde - z_tilde_now
        r2_sum += float(np.dot(diff, diff))
        used_pairs_r += 1

        z_norm_acc += float(np.dot(z_tilde_now, z_tilde_now))

        lam7  = genepair_params[idx, 2: 9]
        total_loss += float(_loss_fn(lam7, counts, pi))
   
    for m in range(genepair_params.shape[0]):
        g1, g2 = str(genepair_params[m, 0]), str(genepair_params[m, 1])
        z_now_tilde  = _pair_z_tilde((g1, g2), z, scalers)
        z_prev_tilde = _pair_z_tilde((g1, g2), z_prev, scalers)
      
        dz = z_now_tilde - z_prev_tilde
        s2_sum += float(np.dot(dz, dz))
        used_pairs_s += 1

    n_r = max(used_pairs_r, 1) * 6
    n_s = max(used_pairs_s, 1) * 6

    r_rms = np.sqrt(r2_sum / max(n_r, 1))
    s_rms = rho * np.sqrt(s2_sum / max(n_s, 1))

    z_rms = np.sqrt(z_norm_acc / max(n_r, 1))
    lam_rms = np.sqrt(lam_norm_acc / max(n_r, 1))
    eps_abs = 2e-3; eps_rel = 0.08
    eps_pri  = eps_abs + eps_rel * max(z_rms, 1.0)
    eps_dual = eps_abs + eps_rel * rho * max(lam_rms, 1.0)
    converged = (r_rms <= eps_pri) and (s_rms <= eps_dual)

    tsv_path = os.path.join(log_path, 'admm_convergence_log.tsv')
    df = pd.DataFrame([{'iteration': iteration, 'rho': rho, 'loss_fn': total_loss, 
                        'r_rms': r_rms, 's_rms': s_rms, 'eps_pri': eps_pri, 'eps_dual': eps_dual, 
                        'used_pairs_r': used_pairs_r, 'used_pairs_s': used_pairs_s, 'converged': int(converged)}])
    write_header = not os.path.exists(tsv_path)
    df.to_csv(tsv_path, sep="\t", mode="a", header=write_header, index=False, float_format="%.6g")
    return converged, r_rms, s_rms


def _pair_z_tilde(genepair_name, z, scalers):
    g1, g2 = genepair_name
    idx1 = np.where(z[:, 0] == g1)[0]
    idx2 = np.where(z[:, 0] == g2)[0]
    a1, b1, p1 = map(float, z[idx1[0], 1:4])
    a2, b2, p2 = map(float, z[idx2[0], 1:4])
    raw6 = np.array([a1, a2, b1, b2, p1, p2], dtype=float)
    return _tilde_from_lambda6(raw6, scalers)


def _loss_fn(lamda, data, pi):
    neglikelihood = bivariate_log_likelihood(lamda, data, pi)
    return neglikelihood

def adapt_rho(rho, r_rms, s_rms):
    eta = (r_rms / (s_rms + 1e-12))
    tau_incr, tau_decr = 3.0, 3.0
    mu_low, mu_high = 1.5, 1.5
    rho_min, rho_max = 1e-3, 1e5  
    if eta > (1.0 + mu_high): rho = min(rho * tau_incr, rho_max)
    elif eta < (1.0 / (1.0 + mu_low)): rho = max(rho / tau_decr, rho_min)
    return rho

def burst_info(singlegene_count_storage, genename, z, log_path, return_res):
    bf = (1 / (1 / z[:, 1].astype(float) + 1 / z[:, 2]).astype(float)).reshape(-1, 1).astype(object)
    bs = (z[:, 3].astype(float) / z[:, 2]).astype(float).reshape(-1, 1).astype(object)
    cv2_pobe, cv2 = compute_cv2(singlegene_count_storage, genename, z)
    outputs = np.hstack([z, bf, bs, cv2_pobe, cv2])
    outputs_df = pd.DataFrame(outputs, columns=['genename', 'alpha', 'beta', 'phi', 'bf', 'bs', 'cv2_pobe', 'cv2'])
    outputs_path = os.path.join(log_path, 'res_bursting_converged.tsv')
    outputs_df.to_csv(outputs_path, sep='\t', index=False, float_format='%.6g')
    return outputs_df.to_numpy() if return_res else None

def compute_cv2(singlegene_count_storage, genename0, z):
    genename = z[:, 0]
    cv2_pobe, cv2 = np.ones(genename.shape), np.ones(genename.shape)
    for n in np.arange(genename.shape[0]):
        genename_idx = genename[n]
        idx = np.where(genename0 == genename_idx)[0]
        counts, pi = singlegene_count_storage[idx[0]]
        counts_pi = counts / pi
        mean = np.mean(counts_pi, axis=0)
        var = np.var(counts_pi, axis=0, ddof=1)
        cv2_pobe[n] = var / (mean ** 2 + 1e-8)
        
        mean = np.mean(counts, axis=0)
        var = np.var(counts, axis=0, ddof=1)
        cv2[n] = var / (mean ** 2 + 1e-8)
    return cv2_pobe.reshape(-1, 1).astype(object), cv2.reshape(-1, 1).astype(object)  


def genepair_interactions_inference(genepair_count_storage, n_jobs, return_plots, log_path, return_res):
    """
    Infer gene-pair regulatory interactions using inferred bursting parameters.

    Args:
        genepair_count_storage (list): Per-pair (names, regs, counts, pi).
        n_jobs (int): Number of parallel workers.
        return_plots (bool): Whether to generate diagnostic plots.
        log_path (str): Directory for reading/writing TSVs.
        return_res (bool): Whether to return results as numpy array.

    Returns:
        np.ndarray or None: Interaction results if return_res True, else None.
    """
    gene_params = pd.read_csv(log_path + '/' + 'res_bursting_converged.tsv', sep='\t').to_numpy()
    # gene_params = [genename, alpha, beta, phi, bf, bs, cv2_pobe]
    genepair_count_storage, genepair_params =  _match_genepair_params(genepair_count_storage, gene_params, log_path)
    if return_plots:
        outputs = loop_genepair_interactions_inference(genepair_count_storage, genepair_params, return_plots, return_res)
    else:
        outputs = parallel_genepair_interactions_inference(genepair_count_storage, genepair_params, n_jobs, return_plots, log_path)
    return outputs
      
def _match_genepair_params(genepair_count_storage, gene_params, log_path):
    genepair_params_info = pd.read_csv(log_path + '/' + 'genepair_inference_params_f0.tsv', sep='\t').to_numpy()[:, :-1]
    genepair_count_storage_new = []
    for m in np.arange(len(genepair_count_storage)):
        genepair_name, _, _, _ = genepair_count_storage[m]
        idx1 = np.where(genepair_params_info[:, 0] == genepair_name[0])[0]
        idx2 = np.where(genepair_params_info[:, 1] == genepair_name[1])[0]
        common_idx = np.intersect1d(idx1, idx2)
        if len(common_idx) == 1: genepair_count_storage_new.append(genepair_count_storage[m])
    genepair_params = _compute_genepair_params(genepair_count_storage_new, gene_params)
    return genepair_count_storage_new, genepair_params
    

def _compute_genepair_params(genepair_count_storage_new, gene_params):
    genename = gene_params[:, 0]
    genepair_params = []
    for m in range(len(genepair_count_storage_new)):
        genepair_name, genepair_grn_info, genepair_count, pi = genepair_count_storage_new[m]
        idx1 = np.where(genename == genepair_name[0])[0]
        idx2 = np.where(genename == genepair_name[1])[0]
        alpha1, beta1, phi1 = gene_params[idx1[0], 1: 4]
        alpha2, beta2, phi2 = gene_params[idx2[0], 1: 4]
        cov = np.cov(genepair_count[0, :] / pi, genepair_count[1, :] / pi)[0, 1]
        w = float((((alpha1 + beta1)**2) * ((alpha2 + beta2)**2) * (alpha1 + beta1 + 1) * (alpha2 + beta2 + 1) * cov) / (phi1 * phi2 * alpha1 * alpha2 * beta1 * beta2))  
        genepair_params_row = [genepair_name[0], genepair_name[1], genepair_grn_info[0], genepair_grn_info[1], 
                            alpha1, alpha2, beta1, beta2, phi1, phi2, w]
        genepair_params.append(genepair_params_row)
    return np.array(genepair_params, dtype=object)

def loop_genepair_interactions_inference(genepair_count_storage, genepair_params, return_plots, return_res):
    counts_density = []; inferred_density = []; outputs = []
    for m in np.arange(len(genepair_params)):
        item = genepair_params[m, :]
        pxy_counts_item, pxy_item, outputs_item = _safe_single_genepair_interactions_inference(item, genepair_count_storage, return_plots)
        counts_density.append(pxy_counts_item)
        inferred_density.append(pxy_item)
        outputs.append(outputs_item)

    # mu.joint_marginal_plots3d(counts_density[0].shape[1], counts_density[0].shape[0], counts_density[1].shape[0], 
    #                          counts_density[0], counts_density[1], counts_density[2], cm.Purples, '#7B3294', '3d_counts_marginal_density.pdf')
    # mu.joint_marginal_plots3d(inferred_density[0].shape[1], inferred_density[0].shape[0], inferred_density[1].shape[0], 
    #                           inferred_density[0], inferred_density[1], inferred_density[2], cm.Blues, '#2166AC', '3d_inferred_marginal_density.pdf')
    return np.array(outputs) if return_res else None


def parallel_genepair_interactions_inference(genepair_count_storage, genepair_params, n_jobs, return_res, log_path):
    """
    Infer gene-pair interactions in parallel.

    Args:
        genepair_count_storage (list): Per-pair storage.
        genepair_params (np.ndarray): Gene-pair parameter array.
        n_jobs (int): Number of parallel workers.
        return_plots (bool): Whether to produce plots (unused here).
        log_path (str): Directory to save TSV.
    """
    jobs = [genepair_params[m, :] for m in range(genepair_params.shape[0])]
    res_interactions = Parallel(n_jobs=n_jobs, backend="loky", verbose=5, batch_size=16)(delayed(
        _safe_single_genepair_interactions_inference)(item, genepair_count_storage, None) for item in jobs)

    tsv_path = os.path.join(log_path, 'genepair_interactions.tsv')
    cols = ['gene1', 'gene2', 'grn_info1', 'grn_info2', 'corr', 'MI', 'sign_y_given_x', 'sign_x_given_y', 'wmi_y_givenx', 'wmi_x_giveny']
    outputs_df = pd.DataFrame(res_interactions, columns=cols)
    write_header = not os.path.exists(tsv_path)
    outputs_df.to_csv(tsv_path, sep='\t', mode='a', header=write_header, index=False, float_format='%.6g')
    return outputs_df.to_numpy() if return_res else None
    


def _safe_single_genepair_interactions_inference(item, genepair_count_storage, return_plots):
    try:
        return single_genepair_interactions_inference(item, genepair_count_storage, return_plots)
    except Exception as e:
        genepair_name, grn_info = item[0: 2].astype(str), item[2: 4].astype(float)
        return [genepair_name[0], genepair_name[1], grn_info[0], grn_info[1], 0.0, 0.0, 0, 0, 0.0, 0.0]
    

# genepair_params_item = item
def single_genepair_interactions_inference(genepair_params_item, genepair_count_storage, return_plots):
    """
    Infer interaction direction and strength for a single gene pair.

    Args:
        genepair_params_item (np.ndarray): One row of genepair_params.
        genepair_count_storage (list): Per-pair (names, regs, counts, pi).
        return_plots (bool): Whether to output density/heatmap plots.

    Returns:
        list or tuple: Interaction metrics, optionally with density arrays.
    """
    genepair_name, grn_info, params = genepair_params_item[0: 2].astype(str), genepair_params_item[2: 4].astype(float), genepair_params_item[4::].astype(float)
    counts, pi = _match_genepair_count_storage(genepair_name, genepair_count_storage)
    pxy, px, py = pc.binary_poissonbeta_pmf(params, None, None, (12, 4), counts, pi, False)
    corr, MI = mutual_info_and_corr_from_data(counts)
    eps_ = 1e-8
    p_y_given_x = np.divide(pxy, px + eps_, where=(px > 0))
    p_x_given_y = np.divide(pxy.T, py.T + eps_, where=(py.T > 0))

    rescaled_density_y_given_x = rescaled_density(p_y_given_x)
    rescaled_density_x_given_y = rescaled_density(p_x_given_y)
    sign_y_given_x = sign_from_rcp_centroid_slope(rescaled_density_y_given_x)
    sign_x_given_y = sign_from_rcp_centroid_slope(rescaled_density_x_given_y)
    wmi_y_givenx = weighted_mutual_information(pxy)
    wmi_x_giveny = weighted_mutual_information(pxy.T)
    res_interactions = [genepair_name[0], genepair_name[1], grn_info[0], grn_info[1], corr, MI, sign_y_given_x, sign_x_given_y, wmi_y_givenx, wmi_x_giveny]
    if return_plots: 
        pxy_counts_v, pxy, px, py = pc.binary_poissonbeta_pmf(params, rescaled_density_y_given_x, rescaled_density_x_given_y, (12, 4), counts, pi, True)
        return pxy_counts_v, pxy, res_interactions
    else: return res_interactions

def _match_genepair_count_storage(genepair_name, genepair_count_storage):
    genename1, genename2 = genepair_name
    for m, item in enumerate(genepair_count_storage):
        pair = item[0]
        p1, p2 = str(pair[0]), str(pair[1])
        if (p1 == genename1) and (p2 == genename2): 
            return item[2], item[3]

def mutual_info_and_corr_from_data(counts):
    x, y = counts[0].astype(float), counts[1].astype(float)
    x_log, y_log = np.log1p(x), np.log1p(y)
    corr = np.corrcoef(x_log, y_log)[0, 1]
    
    x_binned = np.digitize(x, np.histogram_bin_edges(x, bins=32)) - 1
    y_binned = np.digitize(y, np.histogram_bin_edges(y, bins=32)) - 1
    MI = mutual_info_score(x_binned, y_binned)
    return corr, MI


def rescaled_density(p_y_given_x):
    col_max = p_y_given_x.max(axis=0)
    col_max = np.where(col_max <= 0, 1.0, col_max)
    R = p_y_given_x / col_max
    return R


def sign_from_rcp_centroid_slope(R):
    eps_ = 1e-8
    min_col_mass = 1e-10
    ny, nx = R.shape
    y_idx = np.arange(ny, dtype=float)
    w_col = R.sum(axis=0)

    m = (R * y_idx[:, None]).sum(axis=0) / (w_col + eps_)
    mask = w_col > min_col_mass
    x = np.arange(nx, dtype=float)[mask]
    m = m[mask]
    if x.size < 3: return 0
    rho, _ = spearmanr(x, m) 
    if (rho is None) or np.isnan(rho): rho = 0.0
    if abs(rho) <= 0.05: sign = 0
    elif abs(rho) > 0.05: sign = np.sign(rho)
    return sign

def weighted_mutual_information(pxy): 
    eps_ = 1e-12
    px = pxy.sum(axis=0, keepdims=True)       
    py = pxy.sum(axis=1, keepdims=True)
    p_y_given_x = np.divide(pxy, px + eps_, where=(px > 0))
    with np.errstate(divide='ignore', invalid='ignore'):
        log_term = np.where(p_y_given_x > 0, np.log(p_y_given_x + eps_) - np.log(py + eps_), 0.0)
    cols_wmi = (p_y_given_x * log_term).sum(axis=0) 
    wmi = cols_wmi.sum()
    return wmi

