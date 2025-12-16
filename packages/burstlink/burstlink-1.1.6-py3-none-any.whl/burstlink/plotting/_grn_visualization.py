import math
import numpy as np
import pandas as pd
import umap 
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm


def info_integration(counts_csv, degrees_csv, burst_info_csv, edges_csv):
    degrees = pd.read_csv(degrees_csv).to_numpy()
    indegree = degrees[:, 1].astype(float)
    outdegree = degrees[:, 2].astype(float)
    tf_idx = np.where(indegree - outdegree <= 0)[0]
    tg_idx = np.where(indegree - outdegree > 0)[0]
    id_to_gene =  np.asarray(degrees[:, 0]).ravel().tolist()
    
    n_neighbors = 10
    min_dist = 0.035
    spread = 1.0
    metric='cosine'
    pca_components = 50
    umap_n_jobs = 1  

    tf_coords = umap_embed_genes_subset(counts_csv, tf_idx, n_neighbors, min_dist, spread, metric, pca_components, umap_n_jobs)

    n_neighbors = 70
    min_dist = 1.15
    spread = 1.45
    metric='cosine'
    pca_components = 400
    umap_n_jobs = 1  

    tg_coords = umap_embed_genes_subset(counts_csv, tg_idx, n_neighbors, min_dist, spread, metric, pca_components, umap_n_jobs)

    burst_info = pd.read_csv(burst_info_csv).to_numpy()
    gene_names = np.asarray(degrees[:, 0]).ravel().tolist()
    gene_info = {g: {"bf": np.log10(float(burst_info[i, 1])), "bs": np.log10(float(burst_info[i, 2]))} for i, g in enumerate(gene_names)}
    
    
    def _idx2gene(i):
        return id_to_gene[i] if 0 <= i < len(id_to_gene) else None
    
    df_edges = pd.read_csv(edges_csv, header=None, names=['src_id', 'dst_id', 'keep'])
    df_edges = df_edges[df_edges['keep'] > 0].copy()
    id_to_gene = np.asarray(degrees[:, 0]).ravel().tolist()
    
    
    df_edges['src'] = df_edges['src_id'].astype(int).map(_idx2gene)
    df_edges['dst'] = df_edges['dst_id'].astype(int).map(_idx2gene)
    df_edges = df_edges.dropna(subset=['src', 'dst'])
    node_set = set(tf_coords.keys()) | set(tg_coords.keys())
    df_edges = df_edges[df_edges['src'].isin(node_set) & df_edges['dst'].isin(node_set)]
    df_edges = df_edges[df_edges['src'] != df_edges['dst']]
    
    df_edges = df_edges.drop_duplicates(subset=['src', 'dst']).reset_index(drop=True)
    edges_info = list(map(tuple, df_edges[['src', 'dst']].values))
    
    return tf_coords, tg_coords, gene_info, edges_info, id_to_gene





def umap_embed_genes_subset(counts_csv, genes_index, n_neighbors, min_dist, spread, metric, pca_components, umap_n_jobs):
    """
    Embed a subset of genes into 2D using PCA + UMAP.

    Args:
        counts_csv (str): Path to gene-by-cell count matrix (CSV, genes as index).
        genes_index (array-like): Iterable of gene indices or IDs to keep.
        n_neighbors (int): UMAP n_neighbors parameter.
        min_dist (float): UMAP min_dist parameter.
        spread (float): UMAP spread parameter.
        metric (str): UMAP distance metric (e.g., "cosine").
        pca_components (int or None): Number of PCA components before UMAP (None disables PCA).
        umap_n_jobs (int): Number of parallel jobs for UMAP.

    Returns:
        dict: Mapping {gene -> (x, y)} of 2D UMAP coordinates.
    """
    random_state=42
    df = pd.read_csv(counts_csv, index_col=0)
    genes_index = [g for g in genes_index if g in df.index]

    sub = df.loc[genes_index].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    X = sub.values

    if pca_components is not None:
        k = min(int(pca_components), X.shape[1], X.shape[0])
        pca = PCA(n_components=k, svd_solver='auto', whiten=False, random_state=random_state)
        X = pca.fit_transform(X)

    umap_kwargs = dict(n_neighbors=n_neighbors, min_dist=min_dist, spread = spread, metric=metric, random_state=random_state, )
    umap_kwargs["n_jobs"] = int(umap_n_jobs)
        
    reducer = umap.UMAP(**umap_kwargs)
    emb = reducer.fit_transform(X)

    genes_kept = list(sub.index)
    return {gene: (float(emb[i, 0]), float(emb[i, 1])) for i, gene in enumerate(genes_kept)}



def plot_2d_coords(coords, title):
    xs = [p[0] for p in coords.values()]
    ys = [p[1] for p in coords.values()]
    genes = list(coords.keys())

    plt.figure(figsize=(6, 6), dpi=900)
    plt.scatter(xs, ys, c="tab:red", s=40, alpha=0.7, edgecolors="k")
    for gene, x, y in zip(genes, xs, ys):
        plt.text(x, y, gene, fontsize=8, ha="right", va="bottom")
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.title(title)
    plt.show()
    return

def canonical_perp(x1, y1, x2, y2):
    vx, vy = (x2 - x1), (y2 - y1)
    if (vx < 0) or (vx == 0 and vy < 0):
        vx, vy = -vx, -vy
    d = math.hypot(vx, vy)
    if d < 1e-12:
        return 0.0, 0.0, d
    return -vy / d, vx / d, d


def quad_bezier_3d(P0, P1, P2, t):
    P0 = np.asarray(P0); P1 = np.asarray(P1); P2 = np.asarray(P2)
    T = t[:, None]
    return (1 - T) ** 2 * P0 + 2 * (1 - T) * T * P1 + T ** 2 * P2


def quad_bezier_tangent_3d(P0, P1, P2, t_scalar):
    P0 = np.asarray(P0); P1 = np.asarray(P1); P2 = np.asarray(P2)
    t = float(t_scalar)
    return 2 * (1 - t) * (P1 - P0) + 2 * t * (P2 - P1)


def union_box(tf_coords, tg_coords, margin=0.10):
    xs = [p[0] for p in tf_coords.values()] + [p[0] for p in tg_coords.values()]
    ys = [p[1] for p in tf_coords.values()] + [p[1] for p in tg_coords.values()]
    x_min, x_max = float(np.min(xs)), float(np.max(xs))
    y_min, y_max = float(np.min(ys)), float(np.max(ys))
    xr = max(1e-6, x_max - x_min)
    yr = max(1e-6, y_max - y_min)
    x_min -= xr * margin; x_max += xr * margin
    y_min -= yr * margin; y_max += yr * margin
    return x_min, x_max, y_min, y_max

def make_plane_from_box(box, z):
    x_min, x_max, y_min, y_max = box
    xx, yy = np.meshgrid([x_min, x_max], [y_min, y_max])
    zz = np.ones_like(xx) * z
    return xx, yy, zz

def recenter_and_fit(coords, box, frac=0.6):
    if not coords:
        return coords
    x_min, x_max, y_min, y_max = box
    box_w, box_h = (x_max - x_min), (y_max - y_min)
    cx_box, cy_box = (x_min + x_max) / 2.0, (y_min + y_max) / 2.0

    xs = np.array([p[0] for p in coords.values()])
    ys = np.array([p[1] for p in coords.values()])
    cx, cy = float(xs.mean()), float(ys.mean())

    xs_c, ys_c = xs - cx, ys - cy
    rng = max(np.ptp(xs), np.ptp(ys), 1e-12)
    target_span = frac * min(box_w, box_h)
    scale = target_span / rng

    xs_new = xs_c * scale + cx_box
    ys_new = ys_c * scale + cy_box
    genes = list(coords.keys())
    return {g: (float(xs_new[i]), float(ys_new[i])) for i, g in enumerate(genes)}


def draw_bezier_edge(
    ax, P0, P2, bend_sign=+1,
    curve_strength=0.24,
    edge_color="#aaaaaa", edge_lw=0.4, edge_alpha=0.15,
    draw_arrows=False, arrow_pos_t=0.7, arrow_len_scale=0.18,
    n_curve_pts=120):
    x1, y1, z1 = P0; x2, y2, z2 = P2
    nx, ny, d_xy = canonical_perp(x1, y1, x2, y2)
    if d_xy < 1e-8:
        ax.plot([x1, x1], [y1, y1], [z1, z2],
                color=edge_color, lw=edge_lw, alpha=edge_alpha, zorder=6)
        return

    offset = curve_strength * d_xy * bend_sign
    P1 = ((x1 + x2) / 2 + offset * nx,
          (y1 + y2) / 2 + offset * ny,
          (z1 + z2) / 2)

    t = np.linspace(0, 1, int(n_curve_pts))
    B = quad_bezier_3d(P0, P1, P2, t)
    ax.plot(B[:, 0], B[:, 1], B[:, 2],
            color=edge_color, lw=edge_lw, alpha=edge_alpha, zorder=7)

    if draw_arrows:
        tt = float(np.clip(arrow_pos_t, 0.05, 0.95))
        P = quad_bezier_3d(P0, P1, P2, np.array([tt]))[0]
        T = quad_bezier_tangent_3d(P0, P1, P2, tt)
        nrm = float(np.linalg.norm(T))
        if nrm >= 1e-8:
            v = (T / nrm) * (arrow_len_scale * d_xy)
            ax.quiver(P[0], P[1], P[2], v[0], v[1], v[2],
                      arrow_length_ratio=0.25, linewidth=edge_lw,
                      color=edge_color, alpha=edge_alpha, length=1.0, normalize=False)

def scale_box(box, scale_x, scale_y):
    x_min, x_max, y_min, y_max = box
    cx, cy = (x_min + x_max) / 2.0, (y_min + y_max) / 2.0
    hw, hh = (x_max - x_min) * 0.5 * scale_x, (y_max - y_min) * 0.5 * scale_y
    return cx - hw, cx + hw, cy - hh, cy + hh



def shift_box(box, dx, dy):
    x_min, x_max, y_min, y_max = box
    cx, cy = (x_min + x_max)/2.0, (y_min + y_max)/2.0
    w, h = (x_max - x_min), (y_max - y_min)
    cx2, cy2 = cx + dx, cy + dy
    return (cx2 - w/2.0, cx2 + w/2.0, cy2 - h/2.0, cy2 + h/2.0)


def adjust_color_intensity(color, factor):
    rgb = np.array(color[:3]) 
    rgb = np.clip(rgb * factor, 0, 1)
    return tuple(rgb)



def visualization_3d_bursting_grn(tf_coords, tg_coords, edges_info, gene_info, size_scale, tf_size_mul, tg_size_mul, tf_size_range, tg_size_range, size_contrast, tf_color_mul, tg_color_mul,
                                  z_tf, z_tg, plane_alpha, plane_color, plane_margin, edge_color, edge_lw, edge_alpha, tf_intra_edge_lw, tf_intra_edge_alpha,
                                  curve_strength, draw_arrows, elev, azim, fit_frac_tf, fit_frac_tg, scale_x, scale_y, id_to_gene, figsize):
    """
    Plot a 3D TF–TG burst network with UMAP-based coordinates.
    """
   
    box = union_box(tf_coords, tg_coords, margin=plane_margin)
    plane_box_align = scale_box(box, scale_x, scale_y)
    tf_coords = recenter_and_fit(tf_coords, plane_box_align, fit_frac_tf)
    tg_coords = recenter_and_fit(tg_coords, plane_box_align, fit_frac_tg)

    def scale_coords(coords, factor):
        return {g: (x * factor, y * factor) for g, (x, y) in coords.items()}
    
    global_scale = 0.4
    tf_coords = scale_coords(tf_coords, global_scale)
    tg_coords = scale_coords(tg_coords, global_scale)
    plane_box_draw = shift_box(plane_box_align, 2.4, -2.0)
    all_genes = list(set(tf_coords.keys()) | set(tg_coords.keys()))
    bfs = [gene_info[g]["bf"] for g in all_genes if g in gene_info]
    bss = [gene_info[g]["bs"] for g in all_genes if g in gene_info]

    cmap = cm.get_cmap('viridis')
    norm_bf = mcolors.Normalize(vmin=min(bfs), vmax=max(bfs))
    
    
    def adjust_color_intensity(color, factor):
        rgb = np.array(color[:3]) 
        rgb = np.clip(rgb * factor, 0, 1)
        return tuple(rgb)

    bs_min, bs_max = min(bss), max(bss)
    eps = 1e-12
    
    def map_to_range(val, vmin, vmax, rmin, rmax, contrast=1.0):
        if vmax - vmin < eps:
            return (rmin + rmax) * 0.5
        t = (val - vmin) / (vmax - vmin)
        if contrast != 1.0:
            t = np.clip(t, 0.0, 1.0) ** float(contrast)
        return rmin + (rmax - rmin) * float(np.clip(t, 0.0, 1.0))


    fig = plt.figure(figsize=figsize, dpi=900)
    ax = fig.add_subplot(111, projection="3d")
    
    xx, yy, zz = make_plane_from_box(plane_box_draw, z_tf)
    ax.plot_surface(xx, yy, zz, color=plane_color, alpha=plane_alpha,
                    linewidth=0, edgecolor="none", shade=False, zorder=1)
    xx, yy, zz = make_plane_from_box(plane_box_draw, z_tg)
    ax.plot_surface(xx, yy, zz, color=plane_color, alpha=plane_alpha,
                    linewidth=0, edgecolor="none", shade=False, zorder=1)

    for g, (x, y) in tf_coords.items():
        if g in gene_info:
            bf, bs = gene_info[g]["bf"], gene_info[g]["bs"]
            color = adjust_color_intensity(cmap(norm_bf(bf)), tf_color_mul)
            size_px = map_to_range(bs, bs_min, bs_max, tf_size_range[0], tf_size_range[1], contrast=size_contrast)
            size_px *= tf_size_mul * (size_scale / 10.0) 
            ax.scatter(x, y, z_tf, s=size_px, c=[color], edgecolors="none", zorder=4)

    for g, (x, y) in tg_coords.items():
        if g in gene_info:
            bf, bs = gene_info[g]["bf"], gene_info[g]["bs"]
            color = adjust_color_intensity(cmap(norm_bf(bf)), tg_color_mul)
            size_px = map_to_range(bs, bs_min, bs_max, tg_size_range[0], tg_size_range[1], contrast=size_contrast)
            size_px *= tg_size_mul * (size_scale / 10.0)
            ax.scatter(x, y, z_tg, s=size_px, c=[color], edgecolors="none", zorder=3)

        
    def norm_node(n):
        if (n not in tf_coords) and (n not in tg_coords):
            if id_to_gene is not None:
                try:
                    return id_to_gene[int(n)]
                except Exception:
                    return n
        return n
    
    for src, dst in edges_info:
        src = norm_node(src); dst = norm_node(dst)
        src_tf, src_tg = (src in tf_coords), (src in tg_coords)
        dst_tf, dst_tg = (dst in tf_coords), (dst in tg_coords)

        if src_tf and dst_tg:          
            P0 = (*tf_coords[src], z_tf); P2 = (*tg_coords[dst], z_tg)
            draw_bezier_edge(ax, P0, P2, +1, curve_strength,
                             edge_color, edge_lw, edge_alpha, draw_arrows)

        elif src_tg and dst_tf:       
            P0 = (*tg_coords[src], z_tg); P2 = (*tf_coords[dst], z_tf)
            draw_bezier_edge(ax, P0, P2, -1, curve_strength,
                             edge_color, edge_lw, edge_alpha, draw_arrows)

        elif src_tf and dst_tf:      
            P0 = (*tf_coords[src], z_tf); P2 = (*tf_coords[dst], z_tf)
            bend = +1 if str(src) < str(dst) else -1
            lw_use    = tf_intra_edge_lw    if tf_intra_edge_lw    is not None else edge_lw
            alpha_use = tf_intra_edge_alpha if tf_intra_edge_alpha is not None else edge_alpha
            draw_bezier_edge(ax, P0, P2, bend, curve_strength,
                             edge_color, lw_use, alpha_use, draw_arrows)

        elif src_tg and dst_tg:       
            P0 = (*tg_coords[src], z_tg); P2 = (*tg_coords[dst], z_tg)
            bend = +1 if str(src) < str(dst) else -1
            draw_bezier_edge(ax, P0, P2, bend, curve_strength,
                             edge_color, edge_lw, edge_alpha, draw_arrows)
        else:

            continue
    ax.set_zlim(0, 1.1)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()

    sm = cm.ScalarMappable(cmap=cmap, norm=norm_bf)
    sm.set_array([])

    plt.tight_layout()
    plt.show()
    return



def visualization_3d_grn(degrees, burst_info, edges_info, counts_data, figsize):
    """
    Visualize a transcriptional regulatory network in a 3D TF–TG layout.

    Parameters
    ----------
    degrees : str or array-like
        Path to a degree file or an array containing per-gene degree information
        (e.g., gene name, indegree, outdegree).
    burst_info : str or array-like
        Path to a file or array containing burst-related metrics per gene
        (e.g., burst frequency and burst size).
    edges_info : str or array-like
        Path to a file or edge list describing gene regulatory interactions.
    counts_data : str
        Path to the gene-by-cell count matrix used for dimensionality reduction
        (e.g., UMAP).
    figsize : tuple[float, float]
        Size of the output figure.

    Returns
    -------
    None
        This function generates and displays a 3D visualization of the
        transcriptional regulatory network.
    """
    tf_coords, tg_coords, gene_info, edges_info, id_to_gene = info_integration(counts_data, degrees, burst_info, edges_info)
    
    size_scale = 6.0; size_contrast=1.0        
    tf_size_mul = 0.6; tg_size_mul = 0.5; tf_size_range=(1, 6); tg_size_range=(0.5, 5)                      
    tf_color_mul = 1.0; tg_color_mul = 1.2; z_tf = 1.00; z_tg = 0.45
    plane_alpha = 0.25; plane_color = "#d3d3d3"; plane_margin = 0.06; edge_color = "#aaaaaa"
    edge_lw = 0.002; edge_alpha = 0.01; tf_intra_edge_lw = 0.02; tf_intra_edge_alpha = 0.05
    curve_strength = 0.24; draw_arrows = False; elev = 14; azim = -75
    fit_frac_tf = 0.9; fit_frac_tg = 0.88; scale_x = 0.75; scale_y = 1.2

    visualization_3d_bursting_grn(tf_coords, tg_coords, edges_info, gene_info, size_scale, tf_size_mul, tg_size_mul, tf_size_range, tg_size_range, size_contrast, tf_color_mul, tg_color_mul, 
                                  z_tf, z_tg, plane_alpha, plane_color, plane_margin, edge_color, edge_lw, edge_alpha, tf_intra_edge_lw, tf_intra_edge_alpha,
                                  curve_strength, draw_arrows, elev, azim, fit_frac_tf, fit_frac_tg, scale_x, scale_y, id_to_gene, figsize)
    return



