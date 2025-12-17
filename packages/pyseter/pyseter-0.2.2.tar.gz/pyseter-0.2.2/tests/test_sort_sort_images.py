"""Test image sorting functionality."""
import pytest
import pandas as pd
import os
from pyseter.sort import sort_images

def test_sort_images_invalid_directory():
    """Test that invalid directory raises error."""
    df = pd.DataFrame({
        'image': ['img1.jpg'],
        'proposed_id': ['ID_0'],
        'encounter': ['enc1']
    })
    
    with pytest.raises(ValueError, match="is not a valid directory"):
        sort_images(df, "/fake/directory", "/output")

def test_sort_images_missing_columns():
    """Test that missing columns raises error."""
    df = pd.DataFrame({
        'image': ['img1.jpg'],
        'wrong_column': ['ID_0']
    })
    
    with pytest.raises(ValueError, match="must contain the column names"):
        sort_images(df, ".", "/output")

def test_sort_images_basic(tmp_path):
    """Test basic image sorting."""

    # create input directory with images
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "img1.jpg").touch()
    (input_dir / "img2.jpg").touch()
    
    # fake id df
    df = pd.DataFrame({
        'image': ['img1.jpg', 'img2.jpg'],
        'proposed_id': ['ID_0000', 'ID_0000'],
        'encounter': ['enc1', 'enc2']
    })
    
    output_dir = tmp_path / "output"
    
    sort_images(df, str(input_dir), str(output_dir))
    
    # check that proper directory structure was created
    assert (output_dir / "ID_0000" / "enc1" / "img1.jpg").exists()
    assert (output_dir / "ID_0000" / "enc2" / "img2.jpg").exists()

def test_sort_images_multiple_clusters(tmp_path):
    """Test sorting with multiple clusters."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "img1.jpg").touch()
    (input_dir / "img2.jpg").touch()
    (input_dir / "img3.jpg").touch()
    
    df = pd.DataFrame({
        'image': ['img1.jpg', 'img2.jpg', 'img3.jpg'],
        'proposed_id': ['ID_0000', 'ID_0001', 'ID_0001'],
        'encounter': ['enc1', 'enc1', 'enc2']
    })
    
    output_dir = tmp_path / "output"
    
    sort_images(df, str(input_dir), str(output_dir))
    
    # Check both clusters created
    assert (output_dir / "ID_0000").exists()
    assert (output_dir / "ID_0001").exists()
    assert (output_dir / "ID_0000" / "enc1" / "img1.jpg").exists()
    assert (output_dir / "ID_0001" / "enc1" / "img2.jpg").exists()
    assert (output_dir / "ID_0001" / "enc2" / "img3.jpg").exists()