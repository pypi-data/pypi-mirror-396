from typing import Optional
import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from anndata import AnnData

def qc_guide_bins(
    gem_path: str,
    guide_prefix: Optional[str] = None,
    fig_path: Optional[str] = None
) -> None:
    df = pd.read_csv(gem_path, header=0, index_col=None, sep='\t', comment='#')
    if df.columns[0] != 'geneID':
        df.set_index(df.columns[0])
    if guide_prefix != None: df = df[df.geneID.str.startswith(guide_prefix)]
    dup_df = df[df.duplicated(subset=['x', 'y'], keep=False)]
    dedup_df = dup_df.drop_duplicates(subset=['x', 'y'])
    single_df = df.drop_duplicates(subset=['x', 'y'], keep=False)
    x = ['Total CID', 'Singlet CID', 'Doublet CID', 'Dedup CID', 'Combined CID']
    y = [df.shape[0], single_df.shape[0], dup_df.shape[0], dedup_df.shape[0], dedup_df.shape[0] + single_df.shape[0]]
    plt.figure(figsize=(4, 3))
    sns.barplot(x=x, y=y, hue=[1, 2, 3, 4, 5], palette='tab20b', alpha=0.5, legend=False)
    for i in range(5):
        plt.text(x[i], y[i] + (max(y) / 200), y[i], ha='center')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Count')
    plt.yticks([])
    sns.despine()
    if fig_path != None:
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

def remove_mito_ribo_hk_lnc_genes(adata, housekeeping_list="He2020Nature_mouseHK.txt"):
    """
    Usage:
        strip <adata> with genes names beginning with "Mt", "mt-", "Rp", "Gm" and ending with "Rik" or "Rik#";
        strip also with in house housekeeping gene list of mouse housekeeping genes
    Returns:
        clean anndata object without the genes above.
    """
    return_data = adata.copy()
    return_data.var["mt"] = return_data.var_names.str.startswith("Mt")
    return_data.var["mt-"] = return_data.var_names.str.startswith("mt-")
    return_data.var["gm"] = return_data.var_names.str.startswith("Gm")
    return_data.var["Rb"] = return_data.var_names.str.startswith("Rp")
    return_data.var["rik"] = [True if "Rik" in str else False for str in return_data.var_names]
    return_data = return_data[:, ~return_data.var["mt"]].copy()
    return_data = return_data[:, ~return_data.var["mt-"]]
    return_data = return_data[:, ~return_data.var["Rb"]]
    return_data = return_data[:, ~return_data.var["gm"]]
    return_data = return_data[:, ~return_data.var["rik"]]

    with open(housekeeping_list, 'r') as f:
        for line in f:
            hk_genes = line.split('\t')
            break
    return_data = return_data[:, [gene for gene in return_data.var_names if gene not in hk_genes]]
    del return_data.var
    return return_data

def filter_guide_reads(
    gem_path: str,
    guide_prefix: Optional[str] = None,
    output_path: Optional[str] = None,
    binarilize: bool = False,
    assign_pattern: Optional[str] = 'max',
    filter_threshold: Optional[int] = None
) -> pd.DataFrame:
    df = pd.read_csv(gem_path, header=0, index_col=None, sep='\t', comment='#')
    if df.columns[0] != 'geneID':
        df.set_index(df.columns[0], drop=True, inplace=True)
    if guide_prefix != None: df = df[df.geneID.str.startswith(guide_prefix)]
    if filter_threshold != None:
        df = df[df.MIDCount > filter_threshold]
    single_df = df.drop_duplicates(subset=['x', 'y'], keep=False)
    dup_df = df[df.duplicated(subset=['x', 'y'], keep=False)]
    if assign_pattern == 'max':
        max_counts = dup_df.groupby(['x', 'y'])['MIDCount'].transform('max')
        dedup_df = dup_df[dup_df['MIDCount'] == max_counts]
    elif assign_pattern == 'drop':
        dedup_df = pd.DataFrame(columns=dup_df.columns)
    elif assign_pattern == 'all':
        dedup_df = dup_df
    else:
        print('Error: Assign pattern invalid.')
        return
    output_df = pd.concat([single_df, dedup_df], axis=0)
    if binarilize is True:
        output_df['MIDCount'] = 1
        output_df['ExonCount'] = 1
    if output_path == None:
        return output_df
    else:
        output_df.to_csv(filter_threshold, index=False, header=True, sep='\t')
        return
    
def combine_guide_replicates(gdata):
    """
    Usage:
        combine guide replicates in <gdata> to a single gene name
    Return:
        single gene name anndata
    """
    sgs = gdata.var_names.str.split('_', n=1).str[0]
    sgs_grouped = pd.DataFrame(gdata.X.toarray(), columns=gdata.var_names)
    sgs_grouped = sgs_grouped.groupby(sgs, axis=1).sum()

    cgdata = AnnData(sgs_grouped, obs=gdata.obs, var=pd.DataFrame(index=sgs_grouped.columns))
    cgdata.obsm['spatial'] = gdata.obsm['spatial']
    return cgdata

def nmf_clustering(
    adata: AnnData,
    n_components: int = 10,
    random_state: int = 42,
    max_iter: int = 1000,
    verbose: int = 0,
    n_top_genes: int = 2000,
) -> AnnData:
    from sklearn.decomposition import NMF

    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes)
    hvg_data = adata[:, adata.var['highly_variable']]
    cnt_matrix = hvg_data.X.toarray()
    model = NMF(n_components=n_components, verbose=verbose, random_state=random_state, max_iter=max_iter)
    cnt_matrix_trans = model.fit_transform(cnt_matrix)
    hvg_data.obsm['X_nmf'] = cnt_matrix_trans
    hvg_data.uns['X_nmf_components'] = model.components_
    return hvg_data

def nmf_consensus(
    adata: AnnData,
    min_clusters: Optional[int] = 4,
    max_clusters: Optional[int] = 10,
    n_resamples: Optional[int] = 100,
    resample_frac: Optional[float] = 0.8,
    random_state: Optional[int] = 42,
    n_cluster_genes: Optional[int] = 50,
) -> AnnData:
    from tqdm import tqdm
    from scipy.stats import pearsonr

    cnt_matrix_trans = adata.obsm['X_nmf']
    corr_matrix = np.zeros((cnt_matrix_trans.shape[1], cnt_matrix_trans.shape[1]))
    for i in tqdm(range(cnt_matrix_trans.shape[1])):
        for j in range(i, cnt_matrix_trans.shape[1]):
            corr_matrix[i, j] = pearsonr(cnt_matrix_trans[:, i], cnt_matrix_trans[:, j])[0]
    for i in tqdm(range(corr_matrix.shape[1])):
        for j in range(i):
            corr_matrix[i, j] = corr_matrix[j, i]

    import consensusclustering as cc
    from sklearn.cluster import AgglomerativeClustering

    cc_model = cc.ConsensusClustering(
        AgglomerativeClustering(),
        min_clusters=min_clusters,
        max_clusters=max_clusters,
        n_resamples=n_resamples,
        resample_frac=resample_frac,
        k_param='n_clusters'
    )
    cc_model.fit(corr_matrix)
    k = cc_model.best_k()
    cc_model.plot_clustermap(k)

    model = AgglomerativeClustering(n_clusters=k)
    model.fit(corr_matrix)
    nmf_clusters = model.labels_

    for i in range(k):
        cluster_index = np.where(nmf_clusters == i)[0]
        genes = adata.var_names[np.argsort(adata.uns['X_nmf_components'][cluster_index, :]).flatten()[-n_cluster_genes:]].unique()
        sc.tl.score_genes(adata, genes, score_name=f'nmf_cluster_{i}')
        adata.obs[f'nmf_cluster_{i}'] = (adata.obs[f'nmf_cluster_{i}'] - np.mean(adata.obs[f'nmf_cluster_{i}'])) / np.std(adata.obs[f'nmf_cluster_{i}'])
    
    return adata
