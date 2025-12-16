import numpy as np
import random, math
from scipy.stats import poisson, norm, uniform, gaussian_kde
from scipy.special import j_roots, beta as beta_fun
from scipy.interpolate import interp1d
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm

def genes2_coexpression(params, BURST, PLOTS, figname):
    """
    Simulate two-gene co-expression dynamics using SSA and extract steady-state samples.

    Args:
        params (array-like): Parameter vector
            [kon1, kon2, koff1, koff2, ksyn1, ksyn2, kdeg,
             h1, h2, rk, eps, T].
        BURST (bool): Whether to compute burst statistics (BF, BS) for each gene.
        PLOTS (bool): Whether to generate 2D joint density plots for co-expression.
        figname (str): File name to save the 2D joint plot if PLOTS is True.

    Returns:
        dict: Dictionary containing:
            - 's_stable' (np.ndarray): 2×N steady-state samples [X1; X2].
            - Optional burst keys per gene i = 1,2 if BURST is True:
              'mbf{i}', 'mbs{i}', 'mbf_theory{i}', 'mbs_theory{i}', 'mkon{i}'.
    """
    sample_window=1000.0; sample_dt=0.1
  
    kon1, kon2, koff1, koff2, ksyn1, ksyn2, kdeg = params[0: 7]
    h1, h2, rk, eps, T = params[7::]

    # reaction stoichiometry: [OFFx1, ONx1, OFFx2, ONx2, X1, X2]
    reaction_matrix = np.array([
        [-1,  1,  0,  0,  0,  0],  
        [ 1, -1,  0,  0,  0,  0],  
        [ 0,  0, -1,  1,  0,  0],  
        [ 0,  0,  1, -1,  0,  0], 
        [ 0,  0,  0,  0,  1,  0],  
        [ 0,  0,  0,  0,  0,  1],  
        [ 0,  0,  0,  0, -1,  0], 
        [ 0,  0,  0,  0,  0, -1],  
    ], dtype=float)

    # initial state [OFFx1, ONx1, OFFx2, ONx2, X1, X2]
    state = np.array([1, 0, 1, 0, 2, 2], dtype=float)

  
    t_list = [0.0]
    state_list = [state.copy()]
    interval_time = []
    kon = [[] for _ in range(2)]
    bs = [[] for _ in range(2)]
    tt = 0.0

    while tt < T:
        x1, x2 = state[-2:]
        kon_x1 = kon1 * hill_function2(x2, h1, rk, eps)
        kon_x2 = kon2 * hill_function2(x1, h2, rk, eps)

        prop = np.array([
            kon_x1 * (state[0] == 1), koff1 * (state[1]  == 1),   
            kon_x2 * (state[2] == 1), koff2 * (state[3]  == 1),  
            ksyn1 * (state[1] == 1), ksyn2 * (state[3]  == 1),   
            kdeg * x1, kdeg * x2])

        p0 = prop.sum()
        if p0 <= 0.0: break  

        r1 = random.random()
        tau = (1.0 / p0) * math.log(1.0 / r1)

        r2 = random.random()
        threshold = r2 * p0
        cum_prop = np.cumsum(prop)
        next_r = np.searchsorted(cum_prop, threshold)

        tt += tau
        t_list.append(tt)

        state = state + reaction_matrix[next_r]
        state_list.append(state.copy())

        interval_time.append(tau)
        bs[0].append(int(next_r == 4)); bs[1].append(int(next_r == 5))
        kon[0].append(kon_x1); kon[1].append(kon_x2)

    t = np.asarray(t_list, dtype=float)
    S = np.vstack(state_list)

    t_start = max(T - sample_window, t[0])
    tq = np.arange(t_start, T, sample_dt)

    xx, yy = S[:, 4], S[:, 5]
    x_interpfunc = interp1d(t, xx, kind='previous', fill_value='extrapolate')
    y_interpfunc = interp1d(t, yy, kind='previous', fill_value='extrapolate')

    xx_ = x_interpfunc(tq)
    yy_ = y_interpfunc(tq)
    s_stable = np.vstack((xx_, yy_))
    res = {'s_stable': s_stable}

    if PLOTS: jointplots2(s_stable, figname)   
    if BURST:
        interval_time = np.asarray(interval_time, dtype=float)
        for i in range(2):
            gene_params = [params[i], params[i + 2], params[i + 4]]
            mbf, mbs, mbf_theory, mbs_theory, mkon = burst_info(S[:, 2 * i + 1], bs[i], kon[i], gene_params, interval_time)
            res[f'mbf{i + 1}'] = mbf; res[f'mbs{i + 1}'] = mbs
            res[f'mbf_theory{i + 1}'] = mbf_theory; res[f'mbs_theory{i + 1}'] = mbs_theory
            res[f'mkon{i + 1}'] = mkon
    return res
    


def genes3_coexpression(params, BURST, PLOTS, figname):
    """
    Simulate three-gene co-expression dynamics with mutual regulation and extract steady-state samples.

    Args:
        params (array-like): Parameter vector
            [kon1, kon2, kon3,
             koff1, koff2, koff3,
             ksyn1, ksyn2, ksyn3, kdeg,
             h21, h31, h12, h32, h13, h23,
             rk, eps, T].
        BURST (bool): Whether to compute burst statistics (BF, BS) for each gene.
        PLOTS (bool): Whether to generate 3D co-expression KDE projections.
        figname (str): File name to save the 3D joint plot if PLOTS is True.

    Returns:
        dict: Dictionary containing:
            - 's_stable' (np.ndarray): 3×N steady-state samples [X1; X2; X3].
            - Optional burst keys per gene i = 1,2,3 if BURST is True:
              'mbf{i}', 'mbs{i}', 'mbf_theory{i}', 'mbs_theory{i}', 'mkon{i}'.
    """
    sample_window=1000.0; sample_dt=0.1
    
    kon1, kon2, kon3 = params[0: 3]
    koff1, koff2, koff3 = params[3: 6]
    ksyn1, ksyn2, ksyn3, kdeg= params[6: 10]
    h21, h31, h12, h32, h13, h23 = params[10: 16]
    rk, eps, T = params[16: 19]

    # reaction stoichiometry: [OFF_x1, ON_x1, OFF_x2, ON_x2, OFF_x3, ON_x3, X1, X2, X3]
    reaction_matrix = np.array([
        [-1,  1,  0,  0,  0,  0,  0,  0,  0],
        [ 1, -1,  0,  0,  0,  0,  0,  0,  0],  
        [ 0,  0, -1,  1,  0,  0,  0,  0,  0],  
        [ 0,  0,  1, -1,  0,  0,  0,  0,  0],  
        [ 0,  0,  0,  0, -1,  1,  0,  0,  0],  
        [ 0,  0,  0,  0,  1, -1,  0,  0,  0],  
        [ 0,  0,  0,  0,  0,  0,  1,  0,  0], 
        [ 0,  0,  0,  0,  0,  0,  0,  1,  0],  
        [ 0,  0,  0,  0,  0,  0,  0,  0,  1],  
        [ 0,  0,  0,  0,  0,  0, -1,  0,  0],  
        [ 0,  0,  0,  0,  0,  0,  0, -1,  0], 
        [ 0,  0,  0,  0,  0,  0,  0,  0, -1],  
    ])
    
    # initial state [OFFx1, ONx1, OFFx2, ONx2, OFF_x3, ON_x3, X1, X2, X3]
    state = np.array([1, 0, 1, 0, 1, 0, 2, 2, 2], dtype=float)

    t_list = [0.0]
    state_list = [state.copy()]
    interval_time = []
    kon = [[] for _ in range(3)]
    bs = [[] for _ in range(3)]
    tt = 0.0

    while tt < T:
        x1, x2, x3 = state[-3:]
        kon_x1 = kon1 * hill_function2(x2, h21, rk, eps) * hill_function2(x3, h31, rk, eps)
        kon_x2 = kon2 * hill_function2(x1, h12, rk, eps) * hill_function2(x3, h32, rk, eps)
        kon_x3 = kon3 * hill_function2(x1, h13, rk, eps) * hill_function2(x2, h23, rk, eps)

        prop = np.array([
            kon_x1 * (state[0] == 1), koff1 * (state[1] == 1),
            kon_x2 * (state[2] == 1), koff2 * (state[3] == 1),
            kon_x3 * (state[4] == 1), koff3 * (state[5] == 1),
            ksyn1 * (state[1] == 1), ksyn2 * (state[3] == 1), ksyn3 * (state[5] == 1),
            kdeg * x1, kdeg * x2, kdeg * x3])
        
        p0 = prop.sum()
        if p0 <= 0.0: break  

        r1 = random.random()
        tau = (1.0 / p0) * math.log(1.0 / r1)

        r2 = random.random()
        threshold = r2 * p0
        cum_prop = np.cumsum(prop)
        next_r = np.searchsorted(cum_prop, threshold)

        tt += tau
        t_list.append(tt)

        state = state + reaction_matrix[next_r]
        state_list.append(state.copy())
        
        interval_time.append(tau)
        bs[0].append(int(next_r == 6)); bs[1].append(int(next_r == 7)); bs[2].append(int(next_r == 8))
        kon[0].append(kon_x1); kon[1].append(kon_x2); kon[2].append(kon_x3)

    t = np.asarray(t_list, dtype=float)
    S = np.vstack(state_list)

    t_start = max(T - sample_window, t[0])
    tq = np.arange(t_start, T, sample_dt)
    interp = lambda i: interp1d(t, np.array(S[:, i]).flatten(), 'previous')(tq)
    exprs = [interp(6), interp(7), interp(8)]
    s_stable = np.vstack(exprs)
    res = {'s_stable': s_stable}
    
    if PLOTS: 
        cmap = cm.viridis
        jointplot3(s_stable, cmap, figname)
    if BURST:
        interval_time = np.asarray(interval_time, dtype=float)
        for i in range(3):
            gene_params = [params[i], params[i + 3], params[i + 6]]
            mbf, mbs, mbf_theory, mbs_theory, mkon = burst_info(S[:, 2 * i + 1], bs[i], kon[i], gene_params, interval_time)
            res[f'mbf{i + 1}'] = mbf; res[f'mbs{i + 1}'] = mbs
            res[f'mbf_theory{i + 1}'] = mbf_theory; res[f'mbs_theory{i + 1}'] = mbs_theory
            res[f'mkon{i + 1}'] = mkon
    return res


    
def hill_function2(m, h, rk, eps):
    if h < 0:
        if m == 0: kon_hill = eps
        else: kon_hill = 1.0 / (1.0 + 1.0 / ((rk * m) ** (-h))) + eps
    elif h == 0: kon_hill = 0.5 + eps
    elif h > 0: 
        if m == 0: kon_hill = 1.0 + eps
        else: kon_hill = 1.0 / (1.0 + (rk * m) ** h) + eps
    return kon_hill




def jointplots2(s_stable, figname):
    g = sns.jointplot(x=s_stable[0, :], y=s_stable[1, :], kind="kde", fill=True, marginal_kws=dict(fill=True), cut=0)
    g.ax_joint.set_xlim([0, np.max(s_stable[0, :])])
    g.ax_joint.set_ylim([0, np.max(s_stable[1, :])])
    g.ax_marg_x.set_xlim([0, np.max(s_stable[0, :])])
    g.ax_marg_y.set_ylim([0, np.max(s_stable[1, :])])
    g.ax_joint.set_xlabel('$X_1$')
    g.ax_joint.set_ylabel('$X_2$')
    plt.savefig(figname)
    plt.show()
    return




def jointplot3(s_stable, cmap, figname):
    x = s_stable[0, :]; y = s_stable[1, :]; z = s_stable[2, :]
    
    X_xy, Y_xy, Z_xy = kde_2d(x, y)
    X_xz, Z_xz, Y_xz = kde_2d(x, z)
    Y_yz, Z_yz, X_yz = kde_2d(y, z)
    
    fig = plt.figure(dpi = 900)
    ax = fig.add_subplot(111, projection='3d')
    ax.xaxis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))

    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    ax.xaxis._axinfo["grid"]["linewidth"] = 0
    ax.yaxis._axinfo["grid"]["linewidth"] = 0
    ax.zaxis._axinfo["grid"]["linewidth"] = 0
    
    ax.scatter(x, y, z, color=(1, 1, 1), s=8, alpha=0.035, edgecolor='none')
    
    ax.plot_surface(X_xy, Y_xy, np.full_like(Z_xy, z.min()), rstride=1, cstride=1,
                    facecolors=cmap(Z_xy / Z_xy.max()), shade=False, alpha=1.0)

    ax.plot_surface(X_xz, np.full_like(Y_xz, y.max()), Z_xz, rstride=1, cstride=1,
                    facecolors=cmap(Y_xz / Y_xz.max()), shade=False, alpha=1.0)

    ax.plot_surface(np.full_like(X_yz, x.min()), Y_yz, Z_yz, rstride=1, cstride=1,
                    facecolors=cmap(X_yz / X_yz.max()), shade=False, alpha=1.0)

    ax.set_xlabel('Gene1')
    ax.set_ylabel('Gene2')
    ax.set_zlabel('Gene3')
    ax.set_title("3D Scatter with 2D KDE Projections")
    plt.tight_layout()
    plt.savefig(figname)
    plt.show()
    return

    
     

def kde_2d(a, b):
    xy = np.vstack([a, b])
    kde = gaussian_kde(xy)
    axmax = int(np.ceil(a.max()))
    aymax = int(np.ceil(b.max()))

    x_grid = np.arange(0, axmax + 1, 1)
    y_grid = np.arange(0, aymax + 1, 1)
    Xg, Yg = np.meshgrid(x_grid, y_grid)
    grid = np.vstack([Xg.ravel(), Yg.ravel()])
    Z = kde(grid).reshape(Xg.shape)
    return Xg, Yg, Z




def burst_info(s, bs, kon_list, gene_params, interval_time):
    bs = np.asarray(bs, dtype=float)
    kon = np.asarray(kon_list, dtype=float)
    D = np.diff(s, axis = 0)
    index = np.where(D == 1)[0] + 1
    intervaltime, bs_ = [], []
    
    nn = np.min(len(index))
    nn0 = int(np.round(nn / 3))
    for n in np.arange(nn0, nn): 
        intervaltime.append(np.sum(interval_time[index[n - 1]: index[n]]))
        bs_.append(np.sum(bs[index[n - 1]: index[n]]))
    
    mbf = 1.0 / np.mean(intervaltime) if len(intervaltime) > 0 else np.nan
    mbs = np.mean(bs_) if len(bs_) > 0 else np.nan
     
    _, koff, ksyn = gene_params
    mkon = np.mean(kon[1000::]) if len(kon[1000::]) > 0 else np.nan
    mbf_theory = 1 / (1 / mkon + 1 / koff) if mkon > 0 and koff > 0 else np.nan
    mbs_theory = ksyn / koff if koff > 0 else np.nan
    return mbf, mbs, mbf_theory, mbs_theory, mkon



def gibbs_sample(params, burn_in, num):
    """
    Draw samples from a bivariate Poisson-Beta model using Gibbs sampling.

    Args:
        params (array-like): Parameter vector of the bivariate Poisson-Beta model.
        burn_in (int): Number of initial Gibbs iterations to discard.
        num (int): Total number of Gibbs iterations to run.

    Returns:
        np.ndarray: 2×N array of samples [X; Y] after burn-in.
    """
    Xs, Ys = [], []
    y0=15; y = int(y0)
    for i in range(num):
        x = sample_x(params, y, num=1)[0]
        y = sample_y(params, x, num=1)[0]
        if i >= burn_in: Xs.append(x); Ys.append(y)
    Xs = np.array(Xs, dtype=int)
    Ys = np.array(Ys, dtype=int)
    samples = np.vstack([Xs, Ys])
    return samples



def poisson_pmf(A, lam):
    if np.max(lam) < 1e6: return poisson.pmf(A, lam)
    else: return norm.pdf(A, loc=lam, scale=np.sqrt(lam))


def pobe_pdf(A, alpha, beta, phi):
    A = np.asarray(A, dtype=float)
    alpha = np.asarray(alpha, dtype=float)
    beta = np.asarray(beta, dtype=float)
    phi = np.asarray(phi, dtype=float)

    row, col = A.shape
    prob = np.zeros((row, col), dtype=float)

    for i in range(row):
        aa = A[i].reshape(-1, 1)        
        x, w = j_roots(col, beta[i] - 1, alpha[i] - 1) 
        lam = phi[i] * (1.0 + x) / 2.0 
        GJInt = np.sum(w * poisson_pmf(aa, lam), axis=1) 
        prob[i] = (2.0 ** (-alpha[i] - beta[i] + 1.0) / beta_fun(alpha[i], beta[i])) * GJInt
    return prob

    

def conditional_prob(params, vals):
    vals = np.asarray(vals, dtype=float)
    row, col = vals.shape
    a = np.asarray(params[0: 2], dtype=float)   
    b = np.asarray(params[2: 4], dtype=float)  
    phi = np.asarray(params[4: 6], dtype=float) 
    w = float(params[6])

    mu = a / (a + b)  
    mu1, mu2 = mu[0], mu[1]
    ac = a + 1.0

    uniprob = pobe_pdf(vals, a, b, phi)  
    uniprob1 = pobe_pdf(vals, ac, b, phi)  

    eps = 1e-15
    u0 = uniprob[0] + eps
    u1 = uniprob[1] + eps

    ratio10 = uniprob1[1] / u1
    ratio01 = uniprob1[0] / u0

    p_xgiveny = uniprob[0] + w * mu1 * mu2 * (uniprob1[0] - uniprob[0]) * (ratio10 - 1.0)
    p_ygivenx = uniprob[1] + w * mu1 * mu2 * (uniprob1[1] - uniprob[1]) * (ratio01 - 1.0)

    p_xgiveny = np.clip(p_xgiveny, 0.0, None)
    p_ygivenx = np.clip(p_ygivenx, 0.0, None)

    sx = p_xgiveny.sum()
    sy = p_ygivenx.sum()
    if sx > 0: p_xgiveny /= sx
    if sy > 0: p_ygivenx /= sy
    return np.vstack([p_xgiveny, p_ygivenx])



def sample_x(params, y, num):
    max_k=200
    x_grid = np.arange(max_k, dtype=float)
    vals = np.vstack([x_grid, np.full(max_k, float(y))])
    p = conditional_prob(params, vals)[0] 
    cdf = np.cumsum(p)
    cdf[-1] = 1.0 
    u = uniform.rvs(size=num)
    idx = np.searchsorted(cdf, u)
    return idx.astype(int)



def sample_y(params, x, num):
    max_k=200
    y_grid = np.arange(max_k, dtype=float)
    vals = np.vstack([np.full(max_k, float(x)), y_grid])
    p = conditional_prob(params, vals)[1]
    cdf = np.cumsum(p)
    cdf[-1] = 1.0
    u = uniform.rvs(size=num)
    idx = np.searchsorted(cdf, u)
    return idx.astype(int)


