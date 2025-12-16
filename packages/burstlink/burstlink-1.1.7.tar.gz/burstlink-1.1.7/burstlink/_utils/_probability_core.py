import numpy as np
from scipy.stats import norm
from scipy.special import gammaln, j_roots, beta as beta_fn
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns


def poisson_pmf(vals, lam, normal_cut):
    pmf = np.empty_like(lam, dtype=float)
    use_normal = lam >= normal_cut
    if np.any(~use_normal):
        m_small = np.clip(lam[~use_normal], 1e-300, np.inf)
        x_small = np.broadcast_to(vals, lam.shape)[~use_normal]
        logp = x_small * np.log(m_small) - m_small - gammaln(x_small + 1.0)
        pmf[~use_normal] = np.exp(np.clip(logp, -745, 709))

    if np.any(use_normal):
        m_big = lam[use_normal]
        x_big = np.broadcast_to(vals, lam.shape)[use_normal]
        pmf[use_normal] = norm.pdf(x_big, loc=m_big, scale=np.sqrt(m_big))

    return np.clip(pmf, 1e-300, 1.0)


def uni_poissonbeta_pmf(vals, alpha, beta, phi, pi, quad_n):
    eps=1e-12
    vals = np.asarray(vals, dtype=float).ravel()
    pi = np.asarray(pi, dtype=float).ravel()

    x, w = j_roots(quad_n, beta - 1.0, alpha - 1.0)
    z = (1.0 + x) / 2.0 
    wz = w

    lam = (phi * pi)[:, None] * z[None, :]
    vals_col = vals[:, None]
    poissonpmf = poisson_pmf(vals_col, lam, 1e6)     
    gs = np.sum(wz[None, :] * poissonpmf, axis=1)  
    const = (2.0 ** (-alpha - beta + 1.0)) / (beta_fn(alpha, beta) + eps)
    prob = const * gs
    prob = np.clip(prob, eps, 1.0)
    return prob


def binary_poissonbeta_pmf(params, R1, R2, figsize, counts, pi, return_plots):
    alpha1, alpha2, beta1, beta2, phi1, phi2, w = params
    mu1 = alpha1 / (alpha1 + beta1)
    mu2 = alpha2 / (alpha2 + beta2)
    x_max = counts[0, :].max()
    y_max = counts[1, :].max()
    xs = np.arange(int(x_max) + 1, dtype=float)
    ys = np.arange(int(y_max) + 1, dtype=float)
    X, Y = np.meshgrid(xs, ys, indexing='xy')
    nx, ny = X.shape[1], X.shape[0]
    x_flat = X.ravel()
    y_flat = Y.ravel()

    pi1_vec = _ensure_pi_for_vals(x_flat, pi)
    pi2_vec = _ensure_pi_for_vals(y_flat, pi)

    p1 = uni_poissonbeta_pmf(x_flat, alpha1, beta1, phi1, pi1_vec, 50)
    p1_p = uni_poissonbeta_pmf(x_flat, alpha1 + 1., beta1, phi1, pi1_vec, 50)
    p2 = uni_poissonbeta_pmf(y_flat, alpha2, beta2, phi2, pi2_vec, 50)
    p2_p = uni_poissonbeta_pmf(y_flat, alpha2 + 1., beta2, phi2, pi2_vec, 50)

    joint = p1 * p2 + w * mu1 * mu2 * (p1_p - p1) * (p2_p - p2)
    clip_neg_tol = 1e-8
    joint = np.where(joint < clip_neg_tol, 0.0, joint)
    pxy = joint.reshape(ny, nx)
    pxy = pxy / pxy.sum()

    px = pxy.sum(axis=0)  
    py = pxy.sum(axis=1)  
    
    if return_plots == True: 
        pxy_counts_v = joint_marginal_plots2(counts, pxy, R1, R2, figsize)
        return pxy_counts_v, pxy, px, py
    else: return pxy, px, py


def _ensure_pi_for_vals(vals, pi):
    n = vals.size
    reps = int(np.ceil(n / pi.size))
    return np.tile(pi, reps)[:n]

def _density_counts(counts):
    xmax, ymax = int(np.max(counts[0])), int(np.max(counts[1]))
    count = np.zeros([xmax, ymax])
    col = counts.shape[1]
    for i in range(xmax):
        for j in range(ymax):
            cnt = 0
            for k in range(col):
                if i <= counts[0, k] and counts[0, k] < i + 1 and j <= counts[1, k] and counts[1, k] < j + 1:
                    cnt = cnt + 1
            count[i, j] = cnt
    count = np.transpose(count)       
    pxy = count / np.sum(np.sum(count))
    return(pxy)


def joint_plots2(counts, pxy):
    pxy_counts = _density_counts(counts)
    ny1, nx1 = pxy_counts.shape
    ny2, nx2 = pxy.shape
    ny = min(ny1, ny2); nx = min(nx1, nx2)
    pxy_counts_v = pxy_counts[:ny, :nx]
    pxy_v = pxy[:ny, :nx]
    
    vmax = max(pxy_counts_v.max(), pxy_v.max())
    vmin = 0.0
    fig, axes = plt.subplots(1, 2, figsize = (8, 4), dpi = 900)
    im0 = axes[0].imshow(pxy_counts_v, origin='lower', aspect='equal', interpolation='nearest', vmin=vmin, vmax=vmax, cmap='viridis')
    axes[0].set_title('Empirical joint (counts)')
    axes[0].set_xlabel('gene1 count')
    axes[0].set_ylabel('gene2 count')
    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
    im1 = axes[1].imshow(pxy_v, origin='lower', aspect='equal', interpolation='nearest', vmin=vmin, vmax=vmax, cmap='plasma')
    axes[1].set_title('Inferred joint (Poisson–Beta)')
    axes[1].set_xlabel('gene1 count')
    axes[1].set_ylabel('gene2 count')
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.show()
    return pxy_counts_v



def joint_marginal_plots2(counts, pxy, R1, R2, figsize):
    pxy_counts = _density_counts(counts)
    ny1, nx1 = pxy_counts.shape
    ny2, nx2 = pxy.shape
    ny = min(ny1, ny2); nx = min(nx1, nx2)
    pxy_counts_v = pxy_counts[:ny, :nx]
    pxy_v = pxy[:ny, :nx]
    
    pxy_counts, px_counts, py_counts = standardization_pxy(pxy_counts_v)
    pxy, px, py = standardization_pxy(pxy_v)

    four_panel_figure(pxy_counts, px_counts, py_counts, pxy, px, py, R1, R2, figsize)
    return pxy_counts


def standardization_pxy(pxy):
    pxy = pxy / pxy.sum()
    px = pxy.sum(axis=0)  
    py = pxy.sum(axis=1)  
    return pxy, px, py



def add_cbar_right(fig, ax, im, size="4%", pad=0.05):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=size, pad=pad)
    return fig.colorbar(im, cax=cax)

def _tight_align_marginals(ax_joint, ax_marg_x, ax_marg_y, gap=0.002):
    pj = ax_joint.get_position()
    pmx = ax_marg_x.get_position()
    pmy = ax_marg_y.get_position()
    ax_marg_x.set_position([pj.x0, pmx.y0, pj.width, pmx.height])
    ax_marg_x.set_position([pj.x0, pj.y0 + pj.height + gap, pj.width, pmx.height])
    ax_marg_y.set_position([pmy.x0, pj.y0, pmy.width, pj.height])
    ax_marg_y.set_position([pj.x0 + pj.width + gap, pj.y0, pmy.width, pj.height])
    return

def _panel_title(fig, ax_joint, text, fontsize=6, pad=0.1):
    pj = ax_joint.get_position()
    x = pj.x0 + pj.width / 2
    y = pj.y0 + pj.height + pad
    fig.text(x, y, text, ha="center", va="bottom", fontsize=fontsize)
    return

def joint_counts_on_axes(fig, subspec, pxy_counts, px_counts, py_counts, cmap="Purples", title="The simulated",
                         joint_ratio=6, marg_ratio=1, wspace=0.0, hspace=0.0):
    ny, nx = pxy_counts.shape
    gs = GridSpecFromSubplotSpec(2, 2, subplot_spec=subspec, width_ratios=[joint_ratio, marg_ratio], 
                                 height_ratios=[marg_ratio, joint_ratio], wspace=wspace, hspace=hspace)
    ax_marg_x = fig.add_subplot(gs[0, 0])
    ax_joint  = fig.add_subplot(gs[1, 0], sharex=ax_marg_x)
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_joint)
    ax_empty = fig.add_subplot(gs[0, 1])
    ax_empty.axis("off")

    ax_joint.imshow(pxy_counts, origin="lower", cmap=cmap, aspect="equal")
    ax_joint.set_aspect("equal", adjustable="box")
    ax_joint.set_xlabel("Gene1")
    ax_joint.set_ylabel("Gene2")

    x_vals = np.arange(nx)
    y_vals = np.arange(ny)
    bar_color  = "#7B3294"
    fill_color = "#C2A5CF"

    ax_marg_x.bar(x_vals, np.maximum(px_counts, 1e-12), color=fill_color, edgecolor=bar_color, alpha=0.8, linewidth=0.6)
    ax_marg_y.barh(y_vals, np.maximum(py_counts, 1e-12), color=fill_color, edgecolor=bar_color, alpha=0.8, linewidth=0.6)
    ax_joint.set_xlim(-0.5, nx - 0.5)
    ax_joint.set_ylim(-0.5, ny - 0.5)
    ax_marg_x.set_xlim(-0.5, nx - 0.5)
    ax_marg_y.set_ylim(-0.5, ny - 0.5)
    ax_marg_x.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_marg_x.tick_params(axis="y", left=False, labelleft=False)
    ax_marg_y.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_marg_y.tick_params(axis="y", left=False, labelleft=False)

    for ax in [ax_marg_x, ax_marg_y, ax_joint]:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    return ax_joint, ax_marg_x, ax_marg_y, title


def joint_pobe_on_axes(fig, subspec, pxy, px, py, cmap="Blues", title="The inferred", 
                       joint_ratio=6, marg_ratio=1, wspace=0.0, hspace=0.0):
    ny, nx = pxy.shape
    gs = GridSpecFromSubplotSpec(2, 2, subplot_spec=subspec, width_ratios=[joint_ratio, marg_ratio],
                                 height_ratios=[marg_ratio, joint_ratio], wspace=wspace, hspace=hspace)
    ax_marg_x = fig.add_subplot(gs[0, 0])
    ax_joint  = fig.add_subplot(gs[1, 0], sharex=ax_marg_x)
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_joint)
    ax_empty = fig.add_subplot(gs[0, 1])
    ax_empty.axis("off")

    ax_joint.imshow(pxy, origin="lower", cmap=cmap, aspect="equal")
    ax_joint.set_aspect("equal", adjustable="box")
    ax_joint.set_xlabel("Gene1")
    ax_joint.set_ylabel("Gene2")
    x_vals = np.arange(nx)
    y_vals = np.arange(ny)

    ax_marg_x.plot(x_vals, px, color="#257AB6", lw=1.2)
    ax_marg_x.fill_between(x_vals, px, color="#257AB6", alpha=0.15)
    ax_marg_y.plot(py, y_vals, color="#257AB6", lw=1.2)
    ax_marg_y.fill_betweenx(y_vals, py, color="#257AB6", alpha=0.15)
    ax_joint.set_xlim(-0.5, nx - 0.5)
    ax_joint.set_ylim(-0.5, ny - 0.5)
    ax_marg_x.set_xlim(-0.5, nx - 0.5)
    ax_marg_y.set_ylim(-0.5, ny - 0.5)

    ax_marg_x.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_marg_x.tick_params(axis="y", left=False, labelleft=False)
    ax_marg_y.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_marg_y.tick_params(axis="y", left=False, labelleft=False)

    for ax in [ax_marg_x, ax_marg_y, ax_joint]:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    return ax_joint, ax_marg_x, ax_marg_y, title


def conditional_heatmap_on_ax(ax, R, idx_x, idx_y, cmap=cm.viridis, title=None, vmin=None, vmax=None):
    R = np.asarray(R)
    if R.ndim != 2 or R.size == 0:
        raise ValueError(f"R must be a non-empty 2D array, got shape={R.shape}")
    im = ax.imshow(R, origin="lower", cmap=cmap, aspect="equal", vmin=vmin, vmax=vmax)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(idx_x)
    ax.set_ylabel(idx_y)
    ax.set_title(title, fontsize=7, pad=4)
    return im


def four_panel_figure(pxy_counts, px_counts, py_counts, pxy, px, py, R1, R2,
                      figsize, share_heatmap_scale=True, gap=0.002):
    fig = plt.figure(figsize=figsize, dpi=900)
    outer = GridSpec(1, 4, width_ratios=[1, 1, 1, 1], wspace=0.30)
    jc = joint_counts_on_axes(fig, outer[0], pxy_counts, px_counts, py_counts, cmap="Purples", title="The simulated",
                              joint_ratio=7, marg_ratio=1, wspace=0.0, hspace=0.0)
    jp = joint_pobe_on_axes(fig, outer[1], pxy, px, py, cmap="Blues", title="The inferred",
                            joint_ratio=7, marg_ratio=1, wspace=0.0, hspace=0.0)
    vmin = vmax = None
    if share_heatmap_scale:
        R1a = np.asarray(R1); R2a = np.asarray(R2)
        vmin = np.nanmin([R1a.min(), R2a.min()])
        vmax = np.nanmax([R1a.max(), R2a.max()])
    ax3 = fig.add_subplot(outer[2])
    im1 = conditional_heatmap_on_ax(ax3, R1, "Gene2", "Gene1", cmap=cm.viridis, title="Rescaled conditional probability", vmin=vmin, vmax=vmax)
    add_cbar_right(fig, ax3, im1, size="4%", pad=0.05)
    ax4 = fig.add_subplot(outer[3])
    im2 = conditional_heatmap_on_ax(ax4, R2, "Gene1", "Gene2", cmap=cm.viridis, title="Rescaled conditional probability", vmin=vmin, vmax=vmax)
    add_cbar_right(fig, ax4, im2, size="4%", pad=0.05)
    fig.canvas.draw()
    ax_joint1, ax_mx1, ax_my1, title1 = jc
    _tight_align_marginals(ax_joint1, ax_mx1, ax_my1, gap=gap)
    _panel_title(fig, ax_joint1, title1, fontsize=7, pad=0.1)
    ax_joint2, ax_mx2, ax_my2, title2 = jp
    _tight_align_marginals(ax_joint2, ax_mx2, ax_my2, gap=gap)
    _panel_title(fig, ax_joint2, title2, fontsize=7, pad=0.1)
    fig.tight_layout()
    _shrink_all_axes(fig, fs_label=5, fs_tick=4, lw_spine=0.8, lw_tick=0.8, tick_len=3.0)
    plt.show()
    return fig

def _shrink_all_axes(fig, fs_label=7, fs_tick=6, lw_spine=0.8, lw_tick=0.8, tick_len=3.0):
    for ax in fig.axes:
        if hasattr(ax, "colorbar") or "colorbar" in repr(ax).lower():
            continue
        ax.tick_params(axis="both", which="both", labelsize=fs_tick, width=lw_tick, length=tick_len, pad=1.0)
        ax.xaxis.label.set_size(fs_label)
        ax.yaxis.label.set_size(fs_label)
        for spine in ax.spines.values(): spine.set_linewidth(lw_spine)
    return

def joint_density_plots3d(nx, ny, nz, P_xy, P_xz, P_yz, cmap, figname):
    x_grid = np.arange(nx)
    y_grid = np.arange(ny)
    z_grid = np.arange(nz)
    
    X_xy, Y_xy = np.meshgrid(x_grid, y_grid) 
    X_xz, Z_xz = np.meshgrid(x_grid, z_grid)  
    Y_yz, Z_yz = np.meshgrid(y_grid, z_grid) 
    
    fig = plt.figure(dpi= 900 )
    ax = fig.add_subplot(111, projection='3d')
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.pane.set_facecolor((1.0, 1.0, 1.0, 0.0))
        axis.pane.fill = False
    ax.grid(False)

    z_plane = z_grid.min()
    y_plane = y_grid.min()   
    x_plane = x_grid.max()

    P_xy_norm = _normalize(P_xy)
    ax.plot_surface(X_xy, Y_xy, np.full_like(P_xy, z_plane), rstride=1, cstride=1, facecolors=cmap(P_xy_norm), shade=False, alpha=0.95)

    P_xz_norm = _normalize(P_xz)
    ax.plot_surface(X_xz, np.full_like(P_xz, y_plane), Z_xz, rstride=1, cstride=1, facecolors=cmap(P_xz_norm), shade=False, alpha=0.95)
    
    P_yz_norm = _normalize(P_yz)
    ax.plot_surface(np.full_like(P_yz, x_plane), Y_yz, Z_yz, rstride=1, cstride=1, facecolors=cmap(P_yz_norm), shade=False, alpha=0.95)

    ax.invert_xaxis()
    ax.set_xlabel('Gene1')
    ax.set_ylabel('Gene2')
    ax.set_zlabel('Gene3')
    ax.set_title("3D projections of pairwise probability distributions")

    ax.view_init(elev=25, azim=45)
    plt.tight_layout()
    plt.savefig(figname)
    plt.show()
    return



def joint_density_plots3d_png(nx, ny, nz, P_xy, P_xz, P_yz, cmap, figname):
    x_grid = np.arange(nx)
    y_grid = np.arange(ny)
    z_grid = np.arange(nz)
    
    X_xy, Y_xy = np.meshgrid(x_grid, y_grid) 
    X_xz, Z_xz = np.meshgrid(x_grid, z_grid)  
    Y_yz, Z_yz = np.meshgrid(y_grid, z_grid) 
    
    fig = plt.figure(dpi=900)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_axis_off()
    z_plane = z_grid.min()
    y_plane = y_grid.min()
    x_plane = x_grid.max()
    P_xy_norm = _normalize(P_xy)
    ax.plot_surface(X_xy, Y_xy, np.full_like(P_xy, z_plane), rstride=1, cstride=1, facecolors=cmap(P_xy_norm), shade=False, alpha=0.95)
    P_xz_norm = _normalize(P_xz)
    ax.plot_surface(X_xz, np.full_like(P_xz, y_plane), Z_xz, rstride=1, cstride=1, facecolors=cmap(P_xz_norm), shade=False, alpha=0.95)
    P_yz_norm = _normalize(P_yz)
    ax.plot_surface(np.full_like(P_yz, x_plane), Y_yz, Z_yz, rstride=1, cstride=1, facecolors=cmap(P_yz_norm), shade=False, alpha=0.95)
    ax.invert_xaxis()
    ax.view_init(elev=25, azim=45)
    plt.tight_layout()
    plt.savefig(figname)
    plt.show()
    return



def _normalize(Z):
    Z = np.asarray(Z, dtype=float)
    Z = Z - np.nanmin(Z)
    max_val = np.nanmax(Z)
    if max_val <= 0:
        return np.zeros_like(Z)
    return Z / max_val

def joint_marginal_plots3d(nx, ny, nz, P_xy, P_xz, P_yz, cmap, color, figname):
    x_grid = np.arange(nx)
    y_grid = np.arange(ny)
    z_grid = np.arange(nz)

    X_xy, Y_xy = np.meshgrid(x_grid, y_grid)
    X_xz, Z_xz = np.meshgrid(x_grid, z_grid)
    Y_yz, Z_yz = np.meshgrid(y_grid, z_grid)
    
    px = P_xy.sum(axis=0)
    py = P_xy.sum(axis=1)
    pz = P_xz.sum(axis=1)

    z_plane = z_grid.min()    
    y_plane = y_grid.min()    
    x_plane_yz = x_grid.min()

    fig = plt.figure(dpi=900)
    ax = fig.add_subplot(111, projection='3d')
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.pane.set_facecolor((1, 1, 1, 0))
        axis.pane.fill = False
    ax.grid(False)

    ax.plot_surface(X_xy, Y_xy, np.full_like(X_xy, z_plane), facecolors=cmap(_normalize_m(P_xy)), shade=False, alpha=1.0)
    ax.plot_surface(X_xz, np.full_like(X_xz, y_plane), Z_xz, facecolors=cmap(_normalize_m(P_xz)), shade=False, alpha=1.0)
    ax.plot_surface(np.full_like(P_yz, x_plane_yz), Y_yz, Z_yz, facecolors=cmap(_normalize_m(P_yz)), shade=False, alpha=1.0)

    px_n = px / px.max() * (y_grid.max() * 0.4)
    py_n = py / py.max() * (x_grid.max() * 0.4)
    pz_n = pz / pz.max() * (x_grid.max() * 0.4)

    x_far = x_grid.max()
    y_far = y_grid.max()

    ax.plot(x_grid, y_far + px_n, np.full_like(x_grid, z_plane), color=color, lw=2)
    ax.plot(x_far + py_n, y_grid, np.full_like(y_grid, z_plane), color=color, lw=2)
    ax.plot(x_far + pz_n, np.full_like(z_grid, y_plane), z_grid, color=color, lw=2)
    
    ax.plot([x_grid.min(), x_grid.max()], [y_far, y_far], [z_plane, z_plane], color='grey', lw=1.5, alpha=0.7)
    ax.plot([x_far, x_far], [y_grid.min(), y_grid.max()], [z_plane, z_plane], color='grey', lw=1.5, alpha=0.7)
    ax.plot([x_far, x_far], [y_plane, y_plane], [z_grid.min(), z_grid.max()], color='grey', lw=1.5, alpha=0.7)

    ax.set_xlabel("Gene1")
    ax.set_ylabel("Gene2")
    ax.set_zlabel("Gene3")

    ax.view_init(elev=25, azim=45)
    plt.tight_layout()
    plt.savefig(figname)
    plt.show()
    
    

    
def _normalize_m(arr):
    arr = np.asarray(arr, float)
    return (arr - arr.min()) / (arr.max() - arr.min() + 1e-12)





def joint_marginal_noplots(counts, pxy):
    pxy_counts = _density_counts(counts)
    ny1, nx1 = pxy_counts.shape
    ny2, nx2 = pxy.shape
    ny = min(ny1, ny2); nx = min(nx1, nx2)
    pxy_counts_v = pxy_counts[:ny, :nx]
    pxy_v = pxy[:ny, :nx]
    
    pxy_counts, px_counts, py_counts = standardization_pxy(pxy_counts_v)
    pxy, px, py = standardization_pxy(pxy_v)
    
    jointplot_from_pobe_prob(pxy, px, py)
    jointplot_from_counts_prob(pxy_counts, px_counts, py_counts)
    return pxy_counts


def jointplot_from_pobe_prob(pxy, px, py):
    ny, nx = pxy.shape
    x_vals = np.arange(nx)
    y_vals = np.arange(ny)
    X, Y = np.meshgrid(x_vals, y_vals)

    sns.set(style="white")
    dummy = np.zeros(nx)
    g = sns.JointGrid(x=dummy, y=dummy, height=5, ratio=4, space=0)
    g.fig.set_dpi(900)

    # g.ax_joint.contourf(X, Y, pxy, levels=12, cmap='Blues', alpha=1.0)
    g.ax_joint.imshow(pxy, origin='lower', cmap='Blues', aspect='auto')
    g.ax_joint.set_xlim(0, nx - 1)
    g.ax_joint.set_ylim(0, ny - 1)
    g.ax_joint.set_xlabel('Gene1')
    g.ax_joint.set_ylabel('Gene2')

    for spine in ["top", "right"]: g.ax_joint.spines[spine].set_visible(False)
    g.ax_marg_x.plot(x_vals, px, color="#257AB6", lw=1.6)
    g.ax_marg_x.fill_between(x_vals, px, color="#257AB6", alpha=0.15)
    g.ax_marg_x.set_xlim(0, nx - 1)
    g.ax_marg_x.set_xticks([])
    g.ax_marg_x.set_yticks([])
    
    g.ax_marg_y.plot(py, y_vals, color="#257AB6", lw=1.6)
    g.ax_marg_y.fill_betweenx(y_vals, py, color="#257AB6", alpha=0.15)
    g.ax_marg_y.set_ylim(0, ny - 1)
    g.ax_marg_y.set_xticks([])
    g.ax_marg_y.set_yticks([])
    return

    
    

def jointplot_from_counts_prob(pxy_counts, px_counts, py_counts):
    ny, nx = pxy_counts.shape
    x_vals = np.arange(nx)
    y_vals = np.arange(ny)
    X, Y = np.meshgrid(x_vals, y_vals)

    sns.set(style="white")
    dummy = np.zeros(nx)
    g = sns.JointGrid(x=dummy, y=dummy, height=5, ratio=4, space=0)
    g.fig.set_dpi(900)
    
    g.ax_joint.imshow(pxy_counts, origin='lower', cmap='Purples', aspect='auto')
    g.ax_joint.set_xlim(0, nx - 1)
    g.ax_joint.set_ylim(0, ny - 1)
    g.ax_joint.set_xlabel('Gene1')
    g.ax_joint.set_ylabel('Gene2')

    for spine in ["top", "right"]: g.ax_joint.spines[spine].set_visible(False)
    bar_color = "#7B3294"   
    fill_color = "#C2A5CF"   
    
    px_plot = np.maximum(px_counts, 1e-6)
    py_plot = np.maximum(py_counts, 1e-6)
    
    g.ax_marg_x.bar(x_vals, px_plot, width=0.8, color=fill_color, edgecolor=bar_color, alpha=0.8)
    g.ax_marg_x.set_xlim(-0.5, nx - 1)
    g.ax_marg_x.set_xticks([])
    g.ax_marg_x.set_yticks([])

    g.ax_marg_y.barh(y_vals, py_plot, height=0.8, color=fill_color, edgecolor=bar_color, alpha=0.8)
    g.ax_marg_y.set_ylim(-0.5, ny - 1)
    g.ax_marg_y.set_xticks([])
    g.ax_marg_y.set_yticks([])
    return 




