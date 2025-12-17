"""Test feature processing functions."""
import pytest
import numpy as np
from pyseter.extract import load_and_process_features, load_all_features

def test_load_and_process_features_no_l2(tmp_path):
    """Test loading features without l2 norm."""
    # Create fake feature file
    features = {
        'image1.jpg': np.array([1, 2, 3, 4, 5]),
        'image2.jpg': np.array([6, 7, 8, 9, 10])
    }
    feature_path = tmp_path / "features.npy"
    np.save(feature_path, features)
    
    # Test loading
    image_list = ['image1.jpg', 'image2.jpg']
    result = load_and_process_features(str(feature_path), image_list, l2=False)
    
    assert result.shape == (2, 5)
    np.testing.assert_array_equal(result[0], [1, 2, 3, 4, 5])
    np.testing.assert_array_equal(result[1], [6, 7, 8, 9, 10])

def test_load_and_process_features_with_l2(tmp_path):
    """Test loading features with l2 norm."""
    features = {
        'image1.jpg': np.array([3.0, 4.0]),  
        'image2.jpg': np.array([5.0, 12.0])  
    }
    feature_path = tmp_path / "features.npy"
    np.save(feature_path, features)
    
    image_list = ['image1.jpg', 'image2.jpg']
    result = load_and_process_features(str(feature_path), image_list, l2=True)
    
    norms = np.linalg.norm(result, axis=0)
    np.testing.assert_array_almost_equal(norms, [1.0, 1.0])