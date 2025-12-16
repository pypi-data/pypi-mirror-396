import numpy as np
import pandas as pd
import pyarrow.parquet as pq

def select_genepair_grn(read_filename, save_filename):
    """
    Select gene–gene pairs with potential interactions from base GRN (parquet).

    Args:
        read_filename (str): Path to the input Parquet file containing the base GRN.
        save_filename (str): Path to the output CSV file for the gene-pair GRN.
    """
    parquet_file = pq.ParquetFile(read_filename)
    base_GRN = parquet_file.read().to_pandas().iloc[:, 1:]   

    key_col = base_GRN.columns[0]
    base_GRN[key_col] = base_GRN[key_col].astype(str).str.lower().to_numpy()
    base_GRN.columns = [key_col] + base_GRN.columns[1:].astype(str).str.lower().tolist()
    
    value_cols = [c for c in base_GRN.columns if c != key_col]
    vals_num = base_GRN[value_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    vals_num = pd.DataFrame(vals_num.to_numpy(dtype='int8', copy=True), columns=value_cols, index=base_GRN.index)
    df_clean = pd.concat([base_GRN[[key_col]], vals_num], axis=1).copy()
    base_GRN = df_clean.groupby(key_col, as_index=False, sort=False)[value_cols].max()
    
    genepair_grn = screen_genepair_grn(base_GRN, key_col)
    genepair_grn.to_csv(save_filename, index=False)
    return


def screen_genepair_grn(base_GRN, key_col):
    """
    Screen target–TF gene pairs from a base GRN table.

    Args:
        base_GRN (pd.DataFrame): Base GRN with columns [target_gene, tf1, tf2, ...]
                                 containing binary indicators.
        key_col (str): Name of the target gene column.

    Returns:
        pd.DataFrame: DataFrame with columns ['gene1', 'gene2', 'interaction1', 'interaction2'].
    """
    target_genename = base_GRN[key_col].astype(str).to_numpy()
    tf_genename = base_GRN.columns[1:].astype(str).to_numpy()
    value_df = (base_GRN.drop(columns=[key_col]).apply(pd.to_numeric, errors='coerce').fillna(0).astype(int))
    rows, cols = np.where(value_df.to_numpy() == 1)
    genepair_name = [(target_genename[i], tf_genename[j]) for i, j in zip(rows, cols)]
    
    seen = {}
    for gene1, gene2 in genepair_name:
        key_sorted = tuple(sorted((gene1, gene2)))
        d = seen.setdefault(key_sorted, {'count': 0, 'pairs': []})
        d['count'] += 1
        d['pairs'].append((gene1, gene2))
    symmetric_genepair_ = [k for k, info in seen.items() if info['count'] >= 2]
    asymmetric_genepair_ = [p for info in seen.values() if info['count'] < 2 for p in info['pairs']]
    sym_df = pd.DataFrame(symmetric_genepair_, columns=['gene1', 'gene2'])
    if not sym_df.empty:
        sym_df['interaction1'] = 1
        sym_df['interaction2'] = 1
    asym_df = pd.DataFrame(asymmetric_genepair_, columns=['gene1', 'gene2'])
    if not asym_df.empty:
        asym_df['interaction1'] = 0
        asym_df['interaction2'] = 1

    genepair_grn_df = pd.concat([sym_df, asym_df], ignore_index=True)
    mask = genepair_grn_df['gene1'].astype(str) > genepair_grn_df['gene2'].astype(str)
    genepair_grn_df.loc[mask, ['gene1', 'gene2']] = genepair_grn_df.loc[mask, ['gene2', 'gene1']].to_numpy()
    genepair_grn_df.loc[mask, ['interaction1', 'interaction2']] = genepair_grn_df.loc[mask, ['interaction2', 'interaction1']].to_numpy()
    genepair_grn_sorted = genepair_grn_df.sort_values(['gene1', 'gene2'], kind='mergesort').reset_index(drop=True)
    return genepair_grn_sorted
    

def integration_grn(read_filename_atac, read_filename_tf, save_filename):
    """
    Integrate two GRN sources into a consensus GRN.

    Args:
        read_filename_atac (str): Path to the first GRN CSV file (e.g., ATAC-based).
        read_filename_tf (str): Path to the second GRN CSV file (e.g., TF-based).
        save_filename (str): Path to the output integrated GRN CSV file.
    """
    grn_atac = pd.read_csv(read_filename_atac, sep=',')
    grn_tf = pd.read_csv(read_filename_tf, sep=',')
    integrated_grn = merge_and_filter_genepairs(grn_atac, grn_tf)
    integrated_grn.to_csv(save_filename, index=False)
    return


def merge_and_filter_genepairs(grn1, grn2):
    """
    Merge two canonical GRN tables and filter by agreement.

    Args:
        grn1 (pd.DataFrame): First GRN table with columns ['gene1','gene2','interaction1','interaction2'].
        grn2 (pd.DataFrame): Second GRN table with the same column structure.

    Returns:
        pd.DataFrame: Merged and filtered GRN with columns ['gene1','gene2','interaction1','interaction2'].
    """
    grn1 = _check_grn(grn1)
    grn2 = _check_grn(grn2)
    
    m = grn1.merge(grn2, on=['gene1','gene2'], how='outer', suffixes=('_grn1','_grn2'), indicator=True)
    singles = m.loc[m['_merge'] != 'both', ['gene1','gene2','interaction1_grn1','interaction2_grn1','interaction1_grn2','interaction2_grn2']].copy()
    singles['interaction1'] = singles['interaction1_grn1'].combine_first(singles['interaction1_grn2']).astype('int8')
    singles['interaction2'] = singles['interaction2_grn1'].combine_first(singles['interaction2_grn2']).astype('int8')
    singles = singles[['gene1','gene2','interaction1','interaction2']]

    both = m.loc[m['_merge'] == 'both'].copy()
    agree = (both['interaction1_grn1'] == both['interaction1_grn2']) & (both['interaction2_grn1'] == both['interaction2_grn2'])
    both_keep = both.loc[agree, ['gene1','gene2','interaction1_grn1','interaction2_grn1']].copy()
    both_keep = both_keep.rename(columns={'interaction1_grn1':'interaction1','interaction2_grn1':'interaction2'})

    out = pd.concat([singles, both_keep], ignore_index=True)
    grn = out.sort_values(['gene1','gene2'], kind='mergesort').reset_index(drop=True)
    return grn


def _check_grn(grn):
    grn = grn[grn.iloc[:, 0] != grn.iloc[:, 1]].copy()   
    mask = grn.iloc[:, 0] > grn.iloc[:, 1]              

    grn.iloc[mask.values, [0, 1]] = grn.iloc[mask.values, [1, 0]].to_numpy()
    grn.iloc[mask.values, [2, 3]] = grn.iloc[mask.values, [3, 2]].to_numpy()
    grn = grn.sort_values(by=[grn.columns[0], grn.columns[1]]).reset_index(drop=True)
    return grn
    

def RNAseq_analysis(read_filename, threshold_value, save_filename):  
    """
    Filter RNA-seq genes by mean expression and save filtered counts.

    Args:
        read_filename (str): Path to the input RNA-seq TSV file.
        threshold_value (float): Minimum per-gene mean threshold.
        save_filename (str): Path to the output filtered TSV file.
    """
    rna_seq = pd.read_csv(read_filename, sep='\t').to_numpy()[:, 1::]
    genename = rna_seq[:, 0].astype(str)
    counts = rna_seq[:, 1::].astype(float)
    mean = np.nanmean(counts, axis=1)

    idx = np.where(mean >= threshold_value)[0]
    sub_counts = counts[idx, :] 
    sub_counts = np.column_stack([genename[idx], sub_counts])
    pd.DataFrame(sub_counts).to_csv(save_filename, sep='\t', encoding='utf-8') 
    return


def selection_GRNandRNAseq(filename_grn, filename_countdata, save_filename_grn, save_filename_countdata):
    """
    Select consistent GRN edges and RNA-seq genes and save the final subset.

    Args:
        filename_grn (str): Path to the input GRN file (CSV).
        filename_countdata (str): Path to the input RNA-seq count file (TSV).
        save_filename_grn (str): Path to the filtered GRN output file (TSV).
        save_filename_countdata (str): Path to the filtered RNA-seq output file (TSV).
    """
    grn = pd.read_csv(filename_grn, sep=',').to_numpy()
    counts = pd.read_csv(filename_countdata, sep='\t').to_numpy()[:, 1::]

    genename = counts[:, 0].astype(str)
    m0 = np.isin(grn[:, 0], genename)
    m1 = np.isin(grn[:, 1], genename)
    row_mask = m0 & m1                   
    selected_genepair_grn = grn[row_mask, :]

    grn_genename = np.vstack([selected_genepair_grn[:, 0], selected_genepair_grn[:, 1]])
    unique_sorted_grn_genename = np.sort(np.unique(grn_genename))
    idx = []
    for n in np.arange(len(genename)):
        genename_idx = genename[n]
        mask = np.isin(genename_idx, unique_sorted_grn_genename)
        if mask: idx.append(n)
    selected_counts = counts[idx, :]
    
    pd.DataFrame(selected_genepair_grn).to_csv(save_filename_grn, sep='\t', encoding='utf-8') 
    pd.DataFrame(selected_counts).to_csv(save_filename_countdata, sep='\t', encoding='utf-8')
    return



    


