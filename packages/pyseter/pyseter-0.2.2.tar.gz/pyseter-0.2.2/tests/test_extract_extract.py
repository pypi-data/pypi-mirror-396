"""Test FeatureExtractor class."""
import pytest
from unittest.mock import patch
from pyseter.extract import FeatureExtractor

def test_feature_extractor_init_default():
    """Test FeatureExtractor initialization with defaults."""
    extractor = FeatureExtractor(batch_size=8)
    
    assert extractor.batch_size == 8
    assert extractor.stochastic == False
    assert extractor.bbox_csv is None
    assert extractor.device in ["cuda", "mps", "cpu"]

def test_feature_extractor_init_mps():
    """Test FeatureExtractor with custom device."""
    extractor = FeatureExtractor(batch_size=4, device="mps")
    
    assert extractor.device == "mps"
    assert extractor.batch_size == 4

def test_feature_extractor_init_boxes():
    """Test FeatureExtractor with bounding box CSV."""
    extractor = FeatureExtractor(
        batch_size=16,
        bbox_csv="path/to/bboxes.csv"
    )
    
    assert extractor.bbox_csv == "path/to/bboxes.csv"

def test_feature_extractor_stochastic_mode():
    """Test FeatureExtractor in stochastic mode."""
    extractor = FeatureExtractor(batch_size=8, stochastic=True)
    
    assert extractor.stochastic == True