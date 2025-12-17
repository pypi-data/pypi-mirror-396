"""Test data loading functionality."""
import pytest
import pandas as pd
from pyseter.extract import load_bounding_boxes

def test_load_bounding_boxes(tmp_path):
    """Test bounding box loading."""
    
    # create a test CSV
    csv_path = tmp_path / "boxes.csv"
    df = pd.DataFrame({
        'filename': ['image1.jpg', 'image2.jpg'],
        'xmin': [10, 20],
        'ymin': [15, 25],
        'xmax': [110, 120],
        'ymax': [115, 125]
    })
    df.to_csv(csv_path, index=False)
    
    # Test loading
    boxes = load_bounding_boxes(csv_path)
    
    assert 'image1.jpg' in boxes
    assert boxes['image1.jpg'] == (10, 15, 110, 115)
    assert 'image2.jpg' in boxes
    assert boxes['image2.jpg'] == (20, 25, 120, 125)

def test_load_bounding_boxes_empty(tmp_path):
    """Test loading empty CSV."""
    csv_path = tmp_path / "empty.csv"
    df = pd.DataFrame({
        'filename': [],
        'xmin': [],
        'ymin': [],
        'xmax': [],
        'ymax': []
    })
    df.to_csv(csv_path, index=False)
    
    boxes = load_bounding_boxes(str(csv_path))
    assert boxes == {}