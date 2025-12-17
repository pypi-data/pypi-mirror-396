'''Grade images by distinctiveness.'''

from warnings import warn

from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import numpy as np

from pyseter.sort import NetworkCluster

def rate_distinctiveness(features: np.ndarray, match_threshold: float=0.6) -> np.ndarray:
    '''Grade images by their distinctiveness.
    
    Compute the embedding recognizability score (ERS) for each image in the 
    feature array.

    Parameters
    ----------
    features : np.ndarray
        NumPy array of shape (image_count, feature_count) containing feature 
        vectors for each image
    match_threshold: float
        The threshold above which two images are considered a match. Must be 
        between (0, 1)
    
    Returns
    -------
    np.array
        Embedding recognizability score (ERS), a measure of distinctiveness,
        for every image in the dataset.
    '''

    # watch out!
    warn(UserWarning('Distinctiveness grades are experimental and should be verified.'))

    # we use single linkage clustering to find the unrecognizable identity (UI)
    scores = cosine_similarity(features)
    nc = NetworkCluster(match_threshold=match_threshold)
    results = nc.cluster_images(scores, message=False)

    # we assume that the largest cluster is the UI
    cluster_ids = np.array(results.cluster_idx)
    labs, count = np.unique(cluster_ids, return_counts=True)
    ui_index = labs[np.argmax(count)]
    print(f'Unrecognizable identity cluster consists of {np.max(count)} images.')

    # average the features for all images in the largest cluster to get the UI embedding
    ui_feature_array = features[cluster_ids == ui_index]
    ui_norm = normalize(ui_feature_array)
    ui_center = ui_norm.mean(axis=0)

    # compute the embedding recognizability score
    ers = [cosine(f, ui_center) for f in features]
    return np.array(ers)