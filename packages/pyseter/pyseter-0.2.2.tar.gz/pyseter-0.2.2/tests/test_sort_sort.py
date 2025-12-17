"""Test file processing functions."""
import pytest
import pandas as pd
import os
from pathlib import Path
from pyseter.sort import (
    save_encounter_info,
    process_images
)

def test_save_encounter_info(tmp_path):
    """Test saving encounter information to csv."""
    encounters = ['enc1', 'enc2', 'enc3']
    images = ['image1.jpg', 'image2.jpg', 'image3.jpg']
    
    save_encounter_info(str(tmp_path), encounters, images)
    
    # check that the file was created
    csv_path = tmp_path / 'encounter_info.csv'
    assert csv_path.exists()
    
    # check the file contents
    df = pd.read_csv(csv_path)
    assert len(df) == 3
    assert list(df['encounter']) == encounters
    assert list(df['image']) == images
    assert list(df.columns) == ['encounter', 'image']

def test_process_images_empty_dir(tmp_path):
    """Test processing with when the directories are empty."""
    all_image_dir = tmp_path / "all_images"
    
    images, encounters = process_images(str(tmp_path), str(all_image_dir))
    
    assert images == []
    assert encounters == []
    assert all_image_dir.exists()

def test_process_images_with_images(tmp_path):
    """Test processing directory with images."""

    # create directory tree for the first encounter
    enc1_dir = tmp_path / "encounter1"
    enc1_dir.mkdir()

    # touch creates the empty file
    (enc1_dir / "image1.jpg").touch()
    (enc1_dir / "image2.jpg").touch()
    
    # same for the second encounter
    enc2_dir = tmp_path / "encounter2"
    enc2_dir.mkdir()
    (enc2_dir / "image3.jpg").touch()
    
    all_image_dir = tmp_path / "all_images"
    
    images, encounters = process_images(str(tmp_path), str(all_image_dir))
    
    assert len(images) == 3
    assert len(encounters) == 3
    assert 'image1.jpg' in images
    assert 'image2.jpg' in images
    assert 'image3.jpg' in images
    assert encounters.count('encounter1') == 2
    assert encounters.count('encounter2') == 1
    
    # check images were copied
    assert (all_image_dir / "image1.jpg").exists()
    assert (all_image_dir / "image2.jpg").exists()
    assert (all_image_dir / "image3.jpg").exists()

def test_process_images_ignores_file_types(tmp_path):
    """Test that process_images ignores bad file types."""
    enc_dir = tmp_path / "encounter"
    enc_dir.mkdir()
    (enc_dir / "image1.jpg").touch()
    (enc_dir / "image2.png").touch()
    (enc_dir / "image3.tiff").touch()
    (enc_dir / "data.txt").touch()
    
    all_image_dir = tmp_path / "all_images"
    
    images, encounters = process_images(str(tmp_path), str(all_image_dir))
    
    assert len(images) == 2
    assert images[0] == 'image1.jpg'
    assert images[1] == 'image2.png'