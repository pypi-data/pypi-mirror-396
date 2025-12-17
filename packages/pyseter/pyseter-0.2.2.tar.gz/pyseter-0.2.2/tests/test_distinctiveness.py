"""Test distinctiveness grading functionality."""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pyseter.grade import rate_distinctiveness

@pytest.mark.filterwarnings("ignore:UserWarning")
def test_rate_distinctiveness_warns():
    """Test that function issues warning."""
    features = np.array([
        [1.0, 0.0],
        [0.0, 1.0]
    ])
    
    with pytest.warns(UserWarning, match="Distinctiveness grades are experimental"):
        rate_distinctiveness(features)

# basic i/o

def test_rate_distinctiveness_returns_array():
    """Test that function returns numpy array."""
    # three of these features are similar and one is different
    features = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.1, 0.0],
        [1.0, 0.0, 0.1],
        [0.0, 1.0, 0.0]
    ])
    
    result = rate_distinctiveness(features, match_threshold=0.6)
    
    assert isinstance(result, np.ndarray)
    assert len(result) == len(features)

def test_rate_distinctiveness_output_range():
    """Test that distinctiveness scores are in valid range."""
    # two are similar and one is different
    features = np.array([
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.0, 1.0, 0.0]
    ])
    
    scores = rate_distinctiveness(features, match_threshold=0.5)
    
    # Cosine distance is between -1 and 2
    assert np.all(scores >= -1)
    assert np.all(scores <= 2)

# check resulting scores 

def test_rate_distinctiveness_identical_features():
    """Test with all identical features (all unrecognizable)."""
    # all features are the same
    features = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0]
    ])
    
    scores = rate_distinctiveness(features, match_threshold=0.9)
    
    # all should have similar low distinctiveness scores
    assert np.all(scores < 0.01)  # Very close to UI center

def test_rate_distinctiveness_distinct_feature():
    """Test with one very distinct feature."""
    # three similar, one different
    features = np.array([
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.9, 0.0, 0.1],
        [0.0, 0.0, 1.0]  
    ])
    
    scores = rate_distinctiveness(features, match_threshold=0.8)
    
    # the fourth feature should have the highest ers
    assert scores[3] > scores[0]
    assert scores[3] > scores[1]
    assert scores[3] > scores[2]

def test_rate_distinctiveness_prints_ui_size(capsys):
    """Test that function prints UI cluster size."""
    features = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ])
    
    rate_distinctiveness(features, match_threshold=0.9)
    
    captured = capsys.readouterr()
    assert "Unrecognizable identity cluster" in captured.out
    assert "images" in captured.out

# thresholds 

def test_rate_distinctiveness_different_thresholds():
    """Test that different thresholds produce different results."""
    features = np.array([
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],
        [0.8, 0.2, 0.0],
        [0.2, 0.8, 0.0]
    ])
    
    scores_low = rate_distinctiveness(features, match_threshold=0.2)
    scores_high = rate_distinctiveness(features, match_threshold=0.8)
    
    print(scores_low)
    print(scores_high)

    # Different thresholds should produce different scores
    # (because UI cluster size will differ)
    assert not np.allclose(scores_low, scores_high)

# fake data scenario 

def test_rate_distinctiveness_realistic_scenario():
    """Test with more larger datasets."""
    rng = np.random.default_rng(17)
    
    # make twenty features: 15 similar (UI), 5 distinct individuals
    ui_count = 15
    distinct_count = 20 - ui_count
    feature_count = 2

    ui_features = rng.normal(-200, 1, size=(ui_count, feature_count))
    distinct_features = rng.normal(200, 1, size=(distinct_count, feature_count))
    features = np.vstack([ui_features, distinct_features])

    scores = rate_distinctiveness(features, match_threshold=0.6)
    
    # Distinct individuals should have higher scores on average
    ui_scores = scores[:ui_count]
    individual_scores = scores[ui_count:]
    
    assert np.mean(individual_scores) > np.mean(ui_scores)