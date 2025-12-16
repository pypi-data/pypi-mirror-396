"""
Tests for COCO recipe.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

import warpdata as wd


@pytest.fixture
def coco_data_dir(tmp_path):
    """Create a minimal COCO dataset structure for testing."""
    # Create directory structure
    root = tmp_path / "coco"
    train_dir = root / "train2017"
    val_dir = root / "val2017"
    ann_dir = root / "annotations"

    train_dir.mkdir(parents=True)
    val_dir.mkdir(parents=True)
    ann_dir.mkdir(parents=True)

    # Create dummy images
    (train_dir / "000000000001.jpg").write_bytes(b"fake_image_1")
    (train_dir / "000000000002.jpg").write_bytes(b"fake_image_2")
    (val_dir / "000000000003.jpg").write_bytes(b"fake_image_3")

    # Create instances annotation
    instances_train = {
        "images": [
            {"id": 1, "file_name": "000000000001.jpg", "width": 640, "height": 480},
            {"id": 2, "file_name": "000000000002.jpg", "width": 640, "height": 480},
        ],
        "annotations": [
            {
                "image_id": 1,
                "category_id": 1,
                "bbox": [100, 100, 50, 50],
                "area": 2500.0,
                "iscrowd": 0,
            },
            {
                "image_id": 1,
                "category_id": 2,
                "bbox": [200, 200, 30, 30],
                "area": 900.0,
                "iscrowd": 0,
            },
        ],
        "categories": [
            {"id": 1, "name": "person"},
            {"id": 2, "name": "car"},
        ],
    }

    instances_val = {
        "images": [
            {"id": 3, "file_name": "000000000003.jpg", "width": 800, "height": 600},
        ],
        "annotations": [
            {
                "image_id": 3,
                "category_id": 1,
                "bbox": [150, 150, 100, 100],
                "area": 10000.0,
                "iscrowd": 0,
            },
        ],
        "categories": [
            {"id": 1, "name": "person"},
        ],
    }

    # Create captions annotation
    captions_train = {
        "images": [
            {"id": 1, "file_name": "000000000001.jpg"},
            {"id": 2, "file_name": "000000000002.jpg"},
        ],
        "annotations": [
            {"image_id": 1, "caption": "A person walking in the park"},
            {"image_id": 1, "caption": "Person enjoying a sunny day"},
            {"image_id": 2, "caption": "A car on the street"},
        ],
    }

    captions_val = {
        "images": [
            {"id": 3, "file_name": "000000000003.jpg"},
        ],
        "annotations": [
            {"image_id": 3, "caption": "A person standing"},
        ],
    }

    # Write annotation files
    (ann_dir / "instances_train2017.json").write_text(
        json.dumps(instances_train), encoding="utf-8"
    )
    (ann_dir / "instances_val2017.json").write_text(
        json.dumps(instances_val), encoding="utf-8"
    )
    (ann_dir / "captions_train2017.json").write_text(
        json.dumps(captions_train), encoding="utf-8"
    )
    (ann_dir / "captions_val2017.json").write_text(
        json.dumps(captions_val), encoding="utf-8"
    )

    return root


def test_coco_recipe_both_tasks(coco_data_dir):
    """Test COCO recipe with both instances and captions."""
    result = wd.run_recipe(
        "coco",
        "warpdata://test/coco-both",
        data_dir=str(coco_data_dir),
        task="both",
        create_split_subdatasets=True,
    )

    # Should return complex result
    assert isinstance(result, dict)
    assert "main" in result
    assert "subdatasets" in result

    # Check subdatasets
    assert "train" in result["subdatasets"]
    assert "val" in result["subdatasets"]

    # Load main dataset
    data = wd.load("warpdata://test/coco-both", as_format="pandas")
    assert len(data) == 3  # 2 train + 1 val images

    # Check columns
    assert "image_id" in data.columns
    assert "file_name" in data.columns
    assert "image_path" in data.columns
    assert "split" in data.columns
    assert "instances_json" in data.columns
    assert "captions_json" in data.columns
    assert "num_instances" in data.columns
    assert "num_captions" in data.columns

    # Check data
    row1 = data[data["image_id"] == 1].iloc[0]
    assert row1["split"] == "train"
    assert row1["num_instances"] == 2
    assert row1["num_captions"] == 2
    assert row1["gold_present"] == True

    # Parse instances
    instances = json.loads(row1["instances_json"])
    assert len(instances) == 2
    assert instances[0]["category"] in ["person", "car"]
    assert len(instances[0]["bbox"]) == 4

    # Parse captions
    captions = json.loads(row1["captions_json"])
    assert len(captions) == 2

    # Load train split
    train = wd.load("warpdata://test/coco-both-train", as_format="pandas")
    assert len(train) == 2

    # Load val split
    val = wd.load("warpdata://test/coco-both-val", as_format="pandas")
    assert len(val) == 1


def test_coco_recipe_instances_only(coco_data_dir):
    """Test COCO recipe with instances only."""
    result = wd.run_recipe(
        "coco",
        "warpdata://test/coco-inst",
        data_dir=str(coco_data_dir),
        task="instances",
        create_split_subdatasets=False,
    )

    # Load data
    data = wd.load("warpdata://test/coco-inst", as_format="pandas")
    assert len(data) == 3

    # Should have instances but no captions
    row1 = data[data["image_id"] == 1].iloc[0]
    assert row1["instances_json"] is not None
    assert pd.isna(row1["captions_json"])
    assert row1["num_instances"] == 2
    assert row1["num_captions"] == 0


def test_coco_recipe_captions_only(coco_data_dir):
    """Test COCO recipe with captions only."""
    result = wd.run_recipe(
        "coco",
        "warpdata://test/coco-caps",
        data_dir=str(coco_data_dir),
        task="captions",
        create_split_subdatasets=False,
    )

    # Load data
    data = wd.load("warpdata://test/coco-caps", as_format="pandas")
    assert len(data) == 3

    # Should have captions but no instances
    row1 = data[data["image_id"] == 1].iloc[0]
    assert pd.isna(row1["instances_json"])
    assert row1["captions_json"] is not None
    assert row1["num_instances"] == 0
    assert row1["num_captions"] == 2


def test_coco_recipe_metadata(coco_data_dir):
    """Test COCO recipe metadata."""
    result = wd.run_recipe(
        "coco",
        "warpdata://test/coco-meta",
        data_dir=str(coco_data_dir),
        task="both",
    )

    # Check metadata
    metadata = result["metadata"]
    assert metadata["task"] == "both"
    assert metadata["total_images"] == 3
    assert metadata["total_instances"] == 3  # 2 in train + 1 in val
    assert metadata["total_captions"] == 4  # 2 for img1 + 1 for img2 + 1 for img3

    # Check split stats
    split_stats = metadata["split_stats"]
    assert "train2017" in split_stats
    assert split_stats["train2017"]["images"] == 2
    assert split_stats["train2017"]["instances"] == 2
    assert split_stats["train2017"]["captions"] == 3  # 2 for img1 + 1 for img2


def test_coco_recipe_invalid_dir():
    """Test COCO recipe with invalid directory."""
    with pytest.raises(ValueError, match="Data directory not found"):
        wd.run_recipe(
            "coco",
            "warpdata://test/coco-invalid",
            data_dir="/nonexistent/path",
        )


def test_coco_recipe_no_annotations(tmp_path):
    """Test COCO recipe with images but no annotations."""
    # Create directory with images only
    root = tmp_path / "coco_no_ann"
    train_dir = root / "train"
    train_dir.mkdir(parents=True)

    # Create dummy images
    (train_dir / "img1.jpg").write_bytes(b"fake_image_1")
    (train_dir / "img2.jpg").write_bytes(b"fake_image_2")

    result = wd.run_recipe(
        "coco",
        "warpdata://test/coco-no-ann",
        data_dir=str(root),
        task="both",
    )

    # Should still process images
    data = wd.load("warpdata://test/coco-no-ann", as_format="pandas")
    assert len(data) == 2

    # No annotations
    assert (data["num_instances"] == 0).all()
    assert (data["num_captions"] == 0).all()
    assert (data["gold_present"] == False).all()
