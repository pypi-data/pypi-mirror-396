import pytest
import numpy as np
from pyseter.sort import (
    format_ids,
    report_cluster_results,
)

def test_format_ids():
    """Test that integers return properly formatted"""
    ids = np.array([0, 1, 2, 99, 100, 9999])
    formatted = format_ids(ids)
    assert formatted == ['ID-0000', 'ID-0001', 'ID-0002', 
                         'ID-0099', 'ID-0100', 'ID-9999']
    
def test_format_ids_empty():
    """Test formatting empty array."""
    ids = np.array([])
    result = format_ids(ids)
    assert result == []

def test_report_cluster_results(capsys):
    """Test cluster results reporting prints correctly."""
    cluster_labels = np.array([0, 0, 1, 2, 2, 2, 2])
    
    report_cluster_results(cluster_labels)
    
    captured = capsys.readouterr()
    assert 'Found 3 clusters' in captured.out
    assert 'Largest cluster has 4 images' in captured.out

def test_hierarchical_cluster_init():
    pass

def test_network_cluster_init():
    pass


