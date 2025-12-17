"""Test clustering classes."""
import pytest
import numpy as np
from pyseter.sort import (
    HierarchicalCluster,
    NetworkCluster,
    ClusterResults
)

# hac initialization tests

def test_hierarchical_cluster_init():
    """Test HierarchicalCluster initialization."""
    cluster = HierarchicalCluster(match_threshold=0.17)
    assert cluster.match_threshold == 0.17

def test_hierarchical_cluster_invalid_threshold():
    """Test invalid thresholds raise errors."""
    with pytest.raises(ValueError):
        HierarchicalCluster(match_threshold=1.1)

    with pytest.raises(ValueError):
        HierarchicalCluster(match_threshold=-0.5)

def test_hierarchical_cluster_boundary_values():
    """Test boundary values are accepted."""
    cluster1 = HierarchicalCluster(match_threshold=0.0)
    cluster2 = HierarchicalCluster(match_threshold=1.0)
    assert cluster1.match_threshold == 0.0
    assert cluster2.match_threshold == 1.0

# network initialization tests

def test_network_cluster_init():
    """Test NetworkCluster initialization."""
    cluster = NetworkCluster(match_threshold=0.17)
    assert cluster.match_threshold == 0.17

def test_network_cluster_invalid_threshold():
    """Test invalid thresholds raise errors."""
    with pytest.raises(ValueError):
        NetworkCluster(match_threshold=1.1)
    
    with pytest.raises(ValueError):
        NetworkCluster(match_threshold=-0.5)

def test_network_cluster_boundary_values():
    """Test boundary values are accepted."""
    cluster1 = NetworkCluster(match_threshold=0.0)
    cluster2 = NetworkCluster(match_threshold=1.0)
    assert cluster1.match_threshold == 0.0
    assert cluster2.match_threshold == 1.0

# ClusterResults

def test_cluster_results_init():
    """Test ClusterResults initialization."""
    labels = np.array(['ID_0', 'ID_0', 'ID_1'])
    results = ClusterResults(labels)
    
    assert np.array_equal(results.cluster_labels, labels)
    assert results.cluster_count == 2
    assert results.filenames is None
    assert results.false_positive_df is None
    assert list(results.cluster_sizes) == [2, 1]

def test_cluster_results_empty():
    """Test ClusterResults with empty labels."""
    labels = np.array([])
    results = ClusterResults(labels)
    
    assert results.cluster_count == 0
    assert len(results.cluster_sizes) == 0

# simple clustering tests

def test_hierarchical_cluster_identical_features():
    """Test clustering with identical features."""
    # should produce one cluster
    features = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0]
    ])
    
    hc = HierarchicalCluster(match_threshold=0.5)
    labels = hc.cluster_images(features)
    
    # All should be in same cluster
    assert len(np.unique(labels)) == 1

def test_hierarchical_cluster_different_features():
    """Test clustering with very different features."""
    # should produce three clusters
    features = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ])
    
    hc = HierarchicalCluster(match_threshold=0.5)
    labels = hc.cluster_images(features)
    
    # All should be in different clusters
    assert len(np.unique(labels)) == 3

def test_network_cluster_simple():
    """Test network clustering with simple similarity matrix."""
    # simple similarity matrix where images 0 and 1 match yet image 2 is different
    similarity = np.array([
        [1.0, 0.9, 0.1],
        [0.9, 1.0, 0.1],
        [0.1, 0.1, 1.0]
    ])
    
    nc = NetworkCluster(match_threshold=0.5)
    results = nc.cluster_images(similarity, message=False)
    
    # should produce two clusters
    unique_labels = np.unique(results.cluster_labels)
    assert len(unique_labels) == 2
    
    # images 0 and 1 should be in same cluster
    assert results.cluster_labels[0] == results.cluster_labels[1]
    assert results.cluster_labels[0] != results.cluster_labels[2]