"""Sort images by an automatically generated ID before photo-identification"""

from collections import Counter
from pathlib import Path
from typing import Tuple, List, Optional
import os
import shutil

from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

def prep_images(image_dir: str, all_image_dir: str) -> None:
    """Copy all images to a flat directory and save a csv with encounter info.

    Some users may have their image directory structured such that each image
    is in a subfolder by encounter, e.g., original_images/enc1/img1.jpg. The
    `FeatureExtractor` in `pyseter.extract` prefers flat directories. 
    `prep_images` flattens the `original_images` directory by copying every 
    image to `all_image_dir`, then saves a csv with encounter information to the
    working directory. 

    Parameters
    ----------
    image_dir : str
        Path to directory containing images.
    all_image_dir : str
        Path to new directory where user wants to copy all their images. 
    
    Returns
    -------
    None
        Saves images to the all_image_dir and the encounter information to the 
        csv in the working_dir.

    Examples
    --------
    For a complete working example with real images, see:
    
    - [Tutorial](../tutorial.ipynb)
    
    Basic usage pattern::
    
        from pyseter.sort import prep_images

        # old directory, structured by encounter
        working_dir = 'working_dir'
        original_image_dir = working_dir + '/original_images'

        # new, flattened directory containing every image
        image_dir = working_dir + '/all_images'
        prep_images(original_image_dir, all_image_dir=image_dir)  

    """
    images, encounters = process_images(image_dir, all_image_dir)
    working_dir = Path(image_dir).parent.absolute().as_posix()
    save_encounter_info(working_dir, encounters, images)

def process_images(image_root: str, all_image_dir: str) -> Tuple[List[str], List[str]]:
    """Copy all images to a temporary directory and return encounter information"""
    image_list = []
    encounter_list = []

    # the temporary directory lies in the image root
    os.makedirs(all_image_dir, exist_ok=True)
    
    # loop over all the files in the image root 
    i = 0
    for path, dirs, files in os.walk(image_root, topdown=True):

        # only look at images, not in the tmp dir, or images that have already been sorted
        dirs[:] = [d for d in dirs if d not in all_image_dir]
        dirs[:] = [d for d in dirs if 'cluster' not in d]
        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            image_list.append(file)
            
            # get string identifies for the encounter 
            full_path = os.path.join(path, file)
            p = Path(full_path)
            encounter = p.parts[-2]
            encounter_list.append(encounter)
            
            # finally, copy all of the images to the tmp dir
            shutil.copy(full_path, all_image_dir)
            i += 1
            
    print(f'Copied {i} images to:', all_image_dir)
    
    return image_list, encounter_list

def save_encounter_info(output_dir: str, encounters: List[str], images: List[str]) -> None:
    encounter_df = pd.DataFrame(dict(encounter=encounters, image=images))
    encounter_path = os.path.join(output_dir, 'encounter_info.csv')
    encounter_df.to_csv(encounter_path, index=False)
    print('Saved encounter information to:', encounter_path)

def load_features(feature_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load previously extracted features.
    
    Load features produced by the FeatureExtractor.

    Parameters
    ----------
    feature_path : str
        Path to .npy file
    
    Returns
    -------
    filenames, feature_array: np.array, np.array 
        The `filenames` array correspond to each row of the `feature_array`,
        which has shape `(image_count, feature_count)`
    """

    # the features are stored in a dictionary with image names as keys
    feature_dict = np.load(feature_path, allow_pickle=True).item()

    # unpack the dictionary into arrays
    image_names = np.array(list(feature_dict.keys()))
    feature_array = np.array(list(feature_dict.values()))

    return image_names, feature_array

class HierarchicalCluster:
    """Hierarchical clustering of images
    
    Cluster images with the hierarchical agglomerative clustering (HAC) 
    algorithm from scikit-learn.

    Parameters
    ----------
    match_threshold : float
        Threshold dictating how closely knit clusters should be. Must be between
        zero and one. 

    Examples
    --------
    >>> import numpy as np
    >>> from pyseter.sort import HierarchicalCluster
    >>> from numpy.random import normal
    >>> 
    >>> cluster1 = normal(-200, 1, size=(15, 5504))
    >>> cluster2 = normal(200, 1, size=(5, 5504))
    >>> feature_array = np.vstack([cluster1, cluster2])
    >>> 
    >>> hac = HierarchicalCluster(match_threshold=0.5)
    >>> cluster_indices = hac.cluster_images(feature_array)
    >>> len(np.unique(cluster_indices))
    2

    Attributes
    ----------
    match_threshold
        Threshold indicating how closely knit clusters should be.

    Notes
    -----
    HierarchicalCluster works best for larger datasets, say, over 1000 images. 
    HierarchicalCluster may be prone to false negative errors.

    HierarchicalCluster uses the version of HAC with a distance threshold 
    specified--i.e., an unknown number of clusters--complete linkage, and cosine
    as the distance metric.
    """
    def __init__(self, match_threshold: float=0.5) -> None:

        if (match_threshold > 1.0) or (match_threshold < 0.0):
            raise ValueError('Match threshold must lie between 0 and 1')
        self.match_threshold=match_threshold

    def cluster_images(self, features: np.ndarray) -> np.ndarray:
        """Cluster images
        
        Cluster feature vectors according to their cosine distance from one 
        another.

        Parameters
        ----------
        features : np.ndarray
            Array with shape `(image_count, feature_count)` containing the 
            feature vector for each image.
        
        Returns
        -------
        np.ndarray
            NumPy array containing integer labels for each cluster.
        
        """
    
        # convert similarity threshold to distance
        distance_threshold = 1 - self.match_threshold

        # cluster using average linkage
        hac_results = AgglomerativeClustering(
            n_clusters=None, 
            distance_threshold=distance_threshold, 
            linkage='complete',
            metric='cosine'
        ).fit(features)

        # report results
        cluster_labels = hac_results.labels_
        return cluster_labels 

class NetworkCluster: 
    """Network clustering of images
    
    Cluster images with a simple network, where images are nodes and edges
    are images whose similarity score is above the `match_threshold`

    Parameters
    ----------
    match_threshold : float
        Similarity score threshold above which two images are considered to 
        contain the same animal. Must lie between [0.0, 1.0]

    Notes
    -----
    Network clustering works best with smaller datasets, say, around 1000 images.

    Examples
    --------
    >>> import numpy as np
    >>> from pyseter.sort import NetworkCluster
    >>> from sklearn.metrics.pairwise import cosine_similarity
    >>> from numpy.random import normal
    >>> 
    >>> cluster1 = normal(-200, 1, size=(15, 5504))
    >>> cluster2 = normal(200, 1, size=(5, 5504))
    >>> feature_array = np.vstack([cluster1, cluster2])
    >>> scores = cosine_similarity(feature_array)
    >>> 
    >>> nc = NetworkCluster(match_threshold=0.5)
    >>> results = nc.cluster_images(scores)
    >>> len(np.unique(results.cluster_idx))
    2

    """

    def __init__(self, match_threshold: float=0.5) -> None:

        if (match_threshold > 1.0) or (match_threshold < 0.0):
            raise ValueError('Match threshold must lie between 0 and 1')
        self.match_threshold=match_threshold

    def cluster_images(self, similarity: np.ndarray, message: bool=True):
        """Cluster images
        
        Cluster images based on their similarity scores with network clustering.

        Parameters
        ----------
        similarity : np.ndarray
            Array with shape `(image_count, image_count)` indicating the 
            similarity between each pair of images. 
        message : bool
            Should a message about potential false positives be printed to the
            console?
        
        Returns
        -------
        results : ClusterResults
            Object of type `pyster.ClusterResult`. Integer labels for the cluster
            assignment of each image can be accessed with `results.cluster_idx`.
        
        """

        MODULARITY_THRESHOLD = 0.3

        matches = (similarity > self.match_threshold) 
        # matches = np.where(distance < distance_threshold, distance, 0)

        # Get connected components from the graph
        G = nx.from_numpy_array(matches)
        connected_components = (G.subgraph(c) for c in nx.connected_components(G))

        # Create a mapping from node index to cluster index
        file_count, _ = similarity.shape 
        cluster_labels = np.empty(file_count, dtype=object)
        cluster_indices = np.empty(file_count, dtype=int)

        # Assign clusters to the cluster_labels array
        df_list = []
        bad_clusters = []
        bad_cluster_idx = []
        for cluster_idx, subgraph in enumerate(connected_components):

            cluster_label = f'ID_{cluster_idx:04d}'
            for node in subgraph:
                cluster_labels[node] = cluster_label
                cluster_indices[node] = cluster_idx

            # modularity is the warning sign for a bad cluster
            community = nx.community.louvain_communities(subgraph) # type: ignore
            modularity = nx.community.quality.modularity(subgraph, community) # pyright: ignore[reportAttributeAccessIssue]

            if modularity > MODULARITY_THRESHOLD:
                bad_clusters.append(cluster_label)
                bad_cluster_idx.append(cluster_idx)
                
            for community_idx, comm in enumerate(community):
                for node in comm:
                    row = pd.DataFrame({
                        'cluster_id': [cluster_label],
                        'modularity': modularity,
                        # 'filename': fnames[node],
                        'community': community_idx
                    })
                    df_list.append(row)

        if bad_clusters and message:
            w = f'Following clusters may contain false positives:\n{bad_clusters}'
            print(w)

        df = pd.concat(df_list, ignore_index=True)

        results = ClusterResults(cluster_labels)
        # results.filenames = fnames
        results.graph = G
        results.false_positive_df = df
        results.bad_clusters = bad_clusters
        results.bad_cluster_idx = bad_cluster_idx
        results.cluster_idx = format_ids(cluster_indices)

        return results

class ClusterResults:
    """Storing NetworkCluster results.
    """
    def __init__(self, cluster_labels):
        self.cluster_labels = cluster_labels
        self.cluster_idx = [None]
        self.filenames = None
        self.cluster_count = len(set(cluster_labels))
        self.cluster_sizes = Counter(cluster_labels).values()
        self.false_positive_df = None  # type: Optional[pd.DataFrame]
        self.graph = nx.Graph()  # Initialize with empty graph instead of None
        self.bad_clusters = []
        self.bad_cluster_idx = []

    def plot_suspicious(self):
        graph = self.graph
        # Get connected components from the graph
        if graph is None or graph.number_of_nodes() == 0:
            print("No graph data available to plot suspicious connections.")
            return
        connected_components = [graph.subgraph(c) for c 
                                in nx.connected_components(self.graph)]

        subplot_count = len(self.bad_clusters)
        n_col = 5
        n_row = int(np.ceil(subplot_count / n_col))
        width = 1.5
        height = 1.5

        fig, axes = plt.subplots(n_row, n_col, tight_layout=True,
                                figsize=(n_col * width, n_row * height))
        flat = axes.flatten()

        for i, idx in enumerate(self.bad_cluster_idx):
            
            ax = flat[i]

            # remove self loops
            G = connected_components[idx].copy()
            G.remove_edges_from(nx.selfloop_edges(G))

            # modularity is the warning sign for a bad cluster
            community = nx.community.louvain_communities(G) # pyright: ignore[reportAttributeAccessIssue]

            layout = nx.spring_layout(G)
            nx.draw_networkx_edges(G, pos=layout, ax=ax, edge_color='C7', 
                                   alpha=0.3)
            # color each node based on the louvain_communities
            community = nx.community.louvain_communities(G) # pyright: ignore[reportAttributeAccessIssue]
            color_map = {}
            for idx, comm in enumerate(community):
                for node in comm:
                    color_map[node] = idx
            node_colors = [color_map[node] for node in G.nodes]
            nx.draw_networkx_nodes(G, layout, node_size=20, edgecolors='k',
                                   node_color=node_colors, cmap='tab10', ax=ax) # pyright: ignore[reportArgumentType]

            label = self.bad_clusters[i]
            ax.set_title(label, fontsize=10, loc='center')

        # delete unused axes
        for idx in range(subplot_count, len(flat)):
            fig.delaxes(flat[idx])

        s = 'Matches between images\nSingle links between clusters are suspicious'
        fig.suptitle(s, fontsize=12)

        plt.tight_layout()
        plt.show()

def format_ids(ids: np.ndarray) -> List:
    return [f'ID-{i:04d}' for i in ids]

def report_cluster_results(cluster_labs: np.ndarray) -> None:

    # quick summary of the cluster_labs results
    label, count = np.unique(cluster_labs, return_counts=True)
    print(f'Found {len(label)} clusters.')
    print(f'Largest cluster has {np.max(count)} images.')

def sort_images(id_df, all_image_dir: str, output_dir: str) -> None:
    """Sort images into subfolders by proposed ID then encounter.

    Copy images from the flat `all_image_dir` into the `output_dir`, where the 
    `output_dir` is now divided in subfolders by proposed ID then encounter. 

    Parameters
    ----------
    id_df : pd.DataFrame
        Pandas DataFrame with columns `['image', 'proposed_id', 'encounter']`. 
    all_image_dir : str
        Path to flat directory with every image in the `id_df`.
    output_dir : str
        Path to new directory into which `sort_images` will copy files. 
    
    Returns
    -------
    None
        Copies images to the output_dir.

    Examples
    --------
    For a complete working example with real images, see:
    
    - [Tutorial](../tutorial.ipynb) 

    """

    # check that the input directory is a valid derectory
    if not os.path.isdir(all_image_dir):
        raise ValueError('input_dir', all_image_dir, 'is not a valid directory')
    
    # check that the names are valid
    required_column_names = ['image', 'proposed_id', 'encounter']
    names_correct = all([i in id_df.columns for i in required_column_names])
    if not names_correct:
        raise ValueError("id_df must contain the column names 'image', 'proposed_id', 'encounter'")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    grouped = id_df.groupby(['proposed_id', 'encounter'])
    i = 0
    j = 0
    for (clust_id, enc_id), mini_df in grouped:

        i += 1
        cluster_dir = os.path.join(output_dir, clust_id)
        os.makedirs(cluster_dir, exist_ok=True)

        encounter_dir = os.path.join(cluster_dir, enc_id)
        os.makedirs(encounter_dir, exist_ok=True)

        for img in mini_df['image']:
            j += 1
            old_path = os.path.join(all_image_dir, img)
            shutil.copy(old_path, encounter_dir)
        
    print(f'Sorted {j} images into {i} folders.')