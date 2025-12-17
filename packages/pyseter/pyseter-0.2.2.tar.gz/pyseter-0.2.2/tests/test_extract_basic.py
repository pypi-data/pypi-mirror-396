"""Simplest possible tests of extract functions"""
import pytest
import numpy as np
from pyseter.extract import (
    verify_pytorch,
    get_best_device,
    list_images,
)

## basics

def test_verify_pytorch():
    """Test that verify_pytorch runs without error."""
    # Just test it doesn't crash
    result = verify_pytorch()
    assert result is None

def test_get_best_device():
    """Test device selection returns valid device."""
    device = get_best_device()
    assert device in ["cuda", "mps", "cpu"]

## list images function

def test_list_images_empty_dir(tmp_path):
    """Test listing images in empty directory."""
    images = list_images(str(tmp_path))
    assert images == []

def test_list_images_with_files(tmp_path):
    """Test listing actual image files."""
    # Create fake image files
    (tmp_path / "image1.jpg").touch()
    (tmp_path / "image2.png").touch()
    (tmp_path / "text-file.txt").touch()
    
    images = list_images(str(tmp_path))
    assert len(images) == 2
    assert "image1.jpg" in images
    assert "image2.png" in images
    assert "text-file.txt" not in images

def test_list_images_case_insensitive(tmp_path):
    """Test that image listing is case insensitive."""
    (tmp_path / "image.JPG").touch()
    (tmp_path / "photo.PNG").touch()
    
    images = list_images(str(tmp_path))
    assert len(images) == 2

## 